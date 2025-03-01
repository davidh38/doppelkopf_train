#!/usr/bin/env python3
"""
Flask web application for Doppelkopf card game.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant
from agents.random_agent import select_random_action
from agents.rl_agent import RLAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Global game state (in a real application, you'd use a database or session management)
games = {}

def card_to_dict(card):
    """Convert a Card object to a dictionary for JSON serialization."""
    if card is None:
        return None
    
    # Emoji mappings for suits
    suit_emojis = {
        Suit.HEARTS: "♥️",
        Suit.DIAMONDS: "♦️",
        Suit.CLUBS: "♣️",
        Suit.SPADES: "♠️"
    }
    
    # Emoji mappings for ranks
    rank_emojis = {
        Rank.ACE: "🅰️",
        Rank.KING: "👑",
        Rank.QUEEN: "👸",
        Rank.JACK: "🤴",
        Rank.TEN: "🔟",
        Rank.NINE: "9️⃣"
    }
    
    return {
        'suit': card.suit.name,
        'rank': card.rank.name,
        'is_second': card.is_second,
        'suit_emoji': suit_emojis[card.suit],
        'rank_emoji': rank_emojis[card.rank],
        'display': f"{rank_emojis[card.rank]}{suit_emojis[card.suit]} {card.rank.name.capitalize()} of {card.suit.name.capitalize()}" + (" (2)" if card.is_second else ""),
        'id': f"{card.suit.name}_{card.rank.name}_{1 if card.is_second else 0}"
    }

def get_game_state(game_id, player_id=0):
    """Get the current game state for the specified player."""
    if game_id not in games:
        return None
    
    game = games[game_id]['game']
    
    # Convert game state to JSON-serializable format
    state = {
        'current_player': game.current_player,
        'is_player_turn': game.current_player == player_id,
        'player_team': game.teams[player_id].name,
        'game_variant': game.game_variant.name,
        'scores': game.scores,
        'player_scores': game.player_scores,
        'game_over': game.game_over,
        'winner': game.winner.name if game.game_over else None,
        'hand': [card_to_dict(card) for card in game.hands[player_id]],
        'legal_actions': [card_to_dict(card) for card in game.get_legal_actions(player_id)],
        'other_players': [
            {
                'id': i,
                'team': game.teams[i].name,
                'card_count': len(game.hands[i]),
                'is_current': game.current_player == i,
                'score': game.player_scores[i]
            } for i in range(1, game.num_players)
        ],
        'player_score': game.player_scores[player_id],
        'last_trick_points': getattr(game, 'last_trick_points', 0)
    }
    
    # Add current trick with player information - VERY simplified approach
    if game.current_trick:
        # Just send the cards directly
        state['current_trick'] = [card_to_dict(card) for card in game.current_trick]
        
        # Also send player information separately
        starting_player = (game.current_player - len(game.current_trick)) % game.num_players
        trick_players = []
        for i in range(len(game.current_trick)):
            player_idx = (starting_player + i) % game.num_players
            trick_players.append({
                'name': "You" if player_idx == 0 else f"Player {player_idx}",
                'idx': player_idx,
                'is_current': player_idx == game.current_player
            })
        state['trick_players'] = trick_players
        
        # Debug output to help diagnose issues
        print(f"Current trick: {game.current_trick}")
        print(f"Current player: {game.current_player}")
        print(f"Calculated starting player: {starting_player}")
        print(f"Trick players: {trick_players}")
    else:
        state['current_trick'] = []
        state['trick_players'] = []
    
    # Add completed tricks if available
    if hasattr(game, 'tricks') and game.tricks:
        state['last_trick'] = [card_to_dict(card) for card in game.tricks[-1]] if game.tricks else []
        state['trick_winner'] = game.trick_winner
    
    return state

def check_for_hochzeit(hand):
    """Check if the player has both Queens of Clubs."""
    queens_of_clubs = [Card(Suit.CLUBS, Rank.QUEEN, False), Card(Suit.CLUBS, Rank.QUEEN, True)]
    return all(queen in hand for queen in queens_of_clubs)

def ai_play_turn(game_id):
    """Have AI players take their turns."""
    if game_id not in games:
        return
    
    game_data = games[game_id]
    game = game_data['game']
    ai_agents = game_data['ai_agents']
    
    # Keep playing AI turns until it's the human's turn or game is over
    while game.current_player != 0 and not game.game_over:
        current_player = game.current_player
        ai_idx = current_player - 1
        agent = ai_agents[ai_idx]
        
        # Handle both class-based and function-based agents
        if hasattr(agent, 'select_action'):
            action = agent.select_action(game, current_player)
        else:
            action = agent(game, current_player)
        
        # Play the card
        game.play_card(current_player, action)
        
        # Emit game state update after each AI move
        socketio.emit('game_update', get_game_state(game_id), room=game_id)
        
        # Wait for 2 seconds after each card is played (only in web interface)
        socketio.sleep(2)
        
        # If a trick was completed, pause to show it
        if game.trick_winner is not None:
            # Store the trick winner but don't reset it yet
            trick_winner = game.trick_winner
            
            # Emit the game state update with the completed trick
            socketio.emit('game_update', get_game_state(game_id), room=game_id)
            
            # IMPORTANT: Pause for exactly 1 second to show the completed trick
            # This ensures the current trick with all 4 cards stays visible for 1 second
            socketio.sleep(1)
            
            # Calculate points for the trick
            trick_points = sum(card.get_value() for card in game.current_trick)
            
            # Emit the trick completed event with points
            socketio.emit('trick_completed', {
                'winner': trick_winner,
                'is_player': trick_winner == 0,
                'trick_points': trick_points
            }, room=game_id)
            
            # Pause for exactly 3 seconds to show the completed trick
            socketio.sleep(3)
            
            # Now clear the current trick and reset the trick winner
            game.current_trick = []
            game.trick_winner = None
            
            # Emit a game state update to reflect the cleared trick
            socketio.emit('game_update', get_game_state(game_id), room=game_id)

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    """Start a new game."""
    # Generate a unique game ID
    game_id = os.urandom(8).hex()
    
    # Initialize game
    game = DoppelkopfGame()
    game.reset()
    
    # Initialize AI agents
    model_path = 'models/final_model.pt'
    rl_agent = RLAgent(game.get_state_size(), game.get_action_size())
    rl_agent.load(model_path)
    
    # Other players are random agents for now
    ai_agents = [rl_agent] + [select_random_action for _ in range(2)]
    
    # Store game state
    games[game_id] = {
        'game': game,
        'ai_agents': ai_agents
    }
    
    # Return initial game state
    return jsonify({
        'game_id': game_id,
        'state': get_game_state(game_id),
        'has_hochzeit': check_for_hochzeit(game.hands[0])
    })

@app.route('/set_variant', methods=['POST'])
def set_variant():
    """Set the game variant."""
    data = request.json
    game_id = data.get('game_id')
    variant = data.get('variant')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Set the game variant
    if variant == 'normal':
        game.game_variant = GameVariant.NORMAL
    elif variant == 'hochzeit':
        game.game_variant = GameVariant.HOCHZEIT
    elif variant == 'queen_solo':
        game.game_variant = GameVariant.QUEEN_SOLO
    elif variant == 'jack_solo':
        game.game_variant = GameVariant.JACK_SOLO
    else:
        return jsonify({'error': 'Invalid variant'}), 400
    
    # If it's not the player's turn, have AI play
    if game.current_player != 0:
        ai_play_turn(game_id)
    
    return jsonify({
        'state': get_game_state(game_id)
    })

@app.route('/play_card', methods=['POST'])
def play_card():
    """Play a card."""
    data = request.json
    game_id = data.get('game_id')
    card_id = data.get('card_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Check if it's the player's turn
    if game.current_player != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Find the card in the player's hand
    card_parts = card_id.split('_')
    suit_name = card_parts[0]
    rank_name = card_parts[1]
    is_second = card_parts[2] == '1'
    
    suit = Suit[suit_name]
    rank = Rank[rank_name]
    
    # Find the card in the legal actions
    legal_actions = game.get_legal_actions(0)
    selected_card = None
    
    for card in legal_actions:
        if (card.suit.name == suit_name and 
            card.rank.name == rank_name and 
            card.is_second == is_second):
            selected_card = card
            break
    
    if selected_card is None:
        return jsonify({'error': 'Invalid card or not a legal move'}), 400
    
    # Play the card
    game.play_card(0, selected_card)
    
    # Check if a trick was completed
    trick_completed = game.trick_winner is not None
    trick_winner = game.trick_winner
    
    # Have AI players take their turns
    ai_play_turn(game_id)
    
    return jsonify({
        'state': get_game_state(game_id),
        'trick_completed': trick_completed,
        'trick_winner': trick_winner,
        'is_player_winner': trick_winner == 0 if trick_winner is not None else False
    })

@app.route('/get_current_trick', methods=['GET'])
def get_current_trick():
    """Get the current trick data for debugging."""
    game_id = request.args.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Get the current trick data
    current_trick = [card_to_dict(card) for card in game.current_trick]
    
    # Calculate the starting player for this trick
    starting_player = (game.current_player - len(game.current_trick)) % game.num_players
    
    # Add player information to each card in the trick
    trick_players = []
    for i in range(len(game.current_trick)):
        player_idx = (starting_player + i) % game.num_players
        trick_players.append({
            'name': "You" if player_idx == 0 else f"Player {player_idx}",
            'idx': player_idx,
            'is_current': player_idx == game.current_player
        })
    
    return jsonify({
        'current_trick': current_trick,
        'trick_players': trick_players,
        'current_player': game.current_player,
        'starting_player': starting_player
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
