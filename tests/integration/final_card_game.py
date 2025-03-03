#!/usr/bin/env python3
"""
Script to create a Doppelkopf game with only one card left to play.
This allows the user to play the final card in the GUI.
"""

import argparse
import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam
from agents.random_agent import select_random_action
from agents.rl_agent import RLAgent

# Parse command line arguments
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Doppelkopf web app with a final card scenario')
    parser.add_argument('--model', type=str, default='models/final_model.pt',
                        help='Path to a trained model')
    parser.add_argument('--scenario', type=str, choices=['re_wins', 'kontra_wins'], default='re_wins',
                        help='Scenario to set up (re_wins or kontra_wins)')
    return parser.parse_args()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Global game state
games = {}

# Global scoreboard to track wins and player scores
scoreboard = {
    'player_wins': 0,
    'ai_wins': 0,
    'player_scores': [0, 0, 0, 0],  # Individual scores for all 4 players
    'last_starting_player': 0  # Track the last player who started a game
}

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
        'display': f"{rank_emojis[card.rank]}{suit_emojis[card.suit]} {card.rank.name.capitalize()} of {card.suit.name.capitalize()}",
        'id': f"{card.suit.name}_{card.rank.name}_{1 if card.is_second else 0}"
    }

def get_game_state(game_id, player_id=0):
    """Get the current game state for the specified player."""
    if game_id not in games:
        return None
    
    game = games[game_id]['game']
    game_data = games[game_id]
    
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
        'last_trick_points': getattr(game, 'last_trick_points', 0),
        're_announced': game_data.get('re_announced', False),
        'contra_announced': game_data.get('contra_announced', False),
        'no_90_announced': game_data.get('no_90_announced', False),
        'no_60_announced': game_data.get('no_60_announced', False),
        'no_30_announced': game_data.get('no_30_announced', False),
        'multiplier': game_data.get('multiplier', 1),
        'can_announce': True  # Allow announcements in this scenario
    }
    
    # Add current trick with player information
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
    else:
        state['current_trick'] = []
        state['trick_players'] = []
    
    # Add completed tricks if available
    if hasattr(game, 'tricks') and game.tricks:
        state['last_trick'] = [card_to_dict(card) for card in game.tricks[-1]] if game.tricks else []
        state['trick_winner'] = game.trick_winner
    
    return state

def setup_re_wins_scenario(game):
    """Set up a scenario where the Re party will win with exactly 125 points."""
    # Clear existing hands and set up specific cards
    for i in range(game.num_players):
        game.hands[i] = []
    
    # Set up teams
    game.teams = [PlayerTeam.RE, PlayerTeam.KONTRA, PlayerTeam.RE, PlayerTeam.KONTRA]
    
    # Set up scores so that total points will be exactly 240
    # Final trick has 25 points (Ace=11, King=4, Nine=0, Ten=10)
    # So initial scores should total 215 points
    game.scores = [100, 115]  # [RE score, KONTRA score]
    game.player_scores = [50, 57, 50, 58]  # Individual player scores
    
    # Set up the final trick
    game.current_trick = []
    
    # Set up the hands for the final cards
    # Player 0 (human, RE) has the winning card
    game.hands[0] = [Card(Suit.DIAMONDS, Rank.ACE, False)]  # Ace of Diamonds (trump)
    
    # Player 1 (AI, KONTRA)
    game.hands[1] = [Card(Suit.HEARTS, Rank.KING, False)]  # King of Hearts (non-trump)
    
    # Player 2 (AI, RE)
    game.hands[2] = [Card(Suit.SPADES, Rank.NINE, False)]  # Nine of Spades (non-trump)
    
    # Player 3 (AI, KONTRA)
    game.hands[3] = [Card(Suit.CLUBS, Rank.TEN, False)]  # Ten of Clubs (non-trump)
    
    # Set the current player to Player 3 (KONTRA)
    game.current_player = 3
    
    # Set up the tricks list with previous tricks
    game.tricks = []
    
    # Set up the game variant
    game.game_variant = GameVariant.NORMAL
    
    # Set game_over to False
    game.game_over = False
    
    # Set trick_winner to None
    game.trick_winner = None
    
    return game

def setup_kontra_wins_scenario(game):
    """Set up a scenario where the Kontra party will win with exactly 125 points."""
    # Clear existing hands and set up specific cards
    for i in range(game.num_players):
        game.hands[i] = []
    
    # Set up teams
    game.teams = [PlayerTeam.RE, PlayerTeam.KONTRA, PlayerTeam.RE, PlayerTeam.KONTRA]
    
    # Set up scores so that total points will be exactly 240
    # Final trick has 16 points (Nine=0, Jack=2, King=4, Ten=10)
    # So initial scores should total 224 points
    game.scores = [115, 109]  # [RE score, KONTRA score]
    game.player_scores = [57, 55, 58, 54]  # Individual player scores
    
    # Set up the final trick
    game.current_trick = []
    
    # Set up the hands for the final cards
    # Player 0 (human, RE) has a losing card
    game.hands[0] = [Card(Suit.HEARTS, Rank.NINE, False)]  # Nine of Hearts (non-trump)
    
    # Player 1 (AI, KONTRA)
    game.hands[1] = [Card(Suit.DIAMONDS, Rank.JACK, False)]  # Jack of Diamonds (trump)
    
    # Player 2 (AI, RE)
    game.hands[2] = [Card(Suit.SPADES, Rank.KING, False)]  # King of Spades (non-trump)
    
    # Player 3 (AI, KONTRA)
    game.hands[3] = [Card(Suit.CLUBS, Rank.TEN, False)]  # Ten of Clubs (non-trump)
    
    # Set the current player to Player 3 (KONTRA)
    game.current_player = 3
    
    # Set up the tricks list with previous tricks
    game.tricks = []
    
    # Set up the game variant
    game.game_variant = GameVariant.NORMAL
    
    # Set game_over to False
    game.game_over = False
    
    # Set trick_winner to None
    game.trick_winner = None
    
    return game

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
            
            # Calculate points for the trick
            trick_points = sum(card.get_value() for card in game.current_trick)
            
            # Store the last trick information
            games[game_id]['last_trick'] = [card_to_dict(card) for card in game.current_trick]
            
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
            
            games[game_id]['last_trick_players'] = trick_players
            games[game_id]['last_trick_winner'] = trick_winner
            games[game_id]['last_trick_points'] = trick_points
            
            # Emit the trick completed event with points
            socketio.emit('trick_completed', {
                'winner': trick_winner,
                'is_player': trick_winner == 0,
                'trick_points': trick_points
            }, room=game_id)
            
            # Pause for exactly 1 second to show the completed trick
            socketio.sleep(1)
            
            # Now clear the current trick and set the current player to the trick winner
            game.current_trick = []
            game.current_player = trick_winner  # Set the current player to the trick winner
            game.trick_winner = None
            
            # Emit a game state update to reflect the cleared trick
            socketio.emit('game_update', get_game_state(game_id), room=game_id)

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')

@app.route('/model_info', methods=['GET'])
def model_info():
    """Get information about the model being used."""
    args = parse_arguments()
    return jsonify({
        'model_path': args.model
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
    elif variant == 'fleshless':
        game.game_variant = GameVariant.FLESHLESS
    else:
        return jsonify({'error': 'Invalid variant'}), 400
    
    # If it's not the player's turn, have AI play
    if game.current_player != 0:
        ai_play_turn(game_id)
    
    return jsonify({
        'state': get_game_state(game_id)
    })

@app.route('/new_game', methods=['POST'])
def new_game():
    """Start a new game with the final card scenario."""
    # Generate a unique game ID
    game_id = os.urandom(8).hex()
    
    # Initialize game
    game = DoppelkopfGame()
    game.reset()
    
    # Get the scenario from command line arguments
    args = parse_arguments()
    scenario = args.scenario
    
    # Set up the specific scenario
    if scenario == 're_wins':
        game = setup_re_wins_scenario(game)
        print("Setting up RE wins scenario")
    else:  # kontra_wins
        game = setup_kontra_wins_scenario(game)
        print("Setting up KONTRA wins scenario")
    
    # Initialize AI agents - all using the trained model from our training session
    model_path = args.model  # Use the model path from command line arguments
    
    # Use random agents instead of RL agents to avoid requiring a trained model
    ai_agents = [select_random_action for _ in range(3)]
    
    # Store game state
    games[game_id] = {
        'game': game,
        'ai_agents': ai_agents,
        'last_trick': None,
        'last_trick_players': None,
        'last_trick_winner': None,
        'last_trick_points': 0,
        're_announced': False,
        'contra_announced': False,
        'no_90_announced': False,
        'no_60_announced': False,
        'no_30_announced': False,
        'multiplier': 1,  # Score multiplier (doubled for Re/Contra)
        'starting_player': 3  # Player 3 starts in our scenario
    }
    
    # If it's not the player's turn, have AI play
    if game.current_player != 0:
        ai_play_turn(game_id)
    
    # Return initial game state
    return jsonify({
        'game_id': game_id,
        'state': get_game_state(game_id),
        'has_hochzeit': False  # No hochzeit in this scenario
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
    trick_points = 0
    
    # If a trick was completed, handle it before AI plays
    if trick_completed:
        # Calculate points for the trick
        trick_points = sum(card.get_value() for card in game.current_trick)
        
        # Store the trick winner but don't reset it yet
        trick_winner = game.trick_winner
        
        # Clear the current trick and set the current player to the trick winner
        game.current_trick = []
        game.current_player = trick_winner  # Set the current player to the trick winner
        game.trick_winner = None
    
    # Have AI players take their turns
    ai_play_turn(game_id)
    
    # Check if game is over and update scoreboard
    if game.game_over:
        player_team = game.teams[0]
        game_data = games[game_id]
        multiplier = game_data.get('multiplier', 1)
        
        # Count players in each team
        re_players = sum(1 for team in game.teams if team.name == 'RE')
        kontra_players = sum(1 for team in game.teams if team.name == 'KONTRA')
        
        # Get the final scores for each team
        re_score = game.scores[0]
        kontra_score = game.scores[1]
        
        # Determine if special achievements were met
        no_90 = False
        no_60 = False
        no_30 = False
        
        if game.winner.name == 'RE':
            # Check if KONTRA got less than 90 points
            if kontra_score < 90:
                no_90 = True
                # Check if KONTRA got less than 60 points
                if kontra_score < 60:
                    no_60 = True
                    # Check if KONTRA got less than 30 points
                    if kontra_score < 30:
                        no_30 = True
        else:  # KONTRA won
            # Check if RE got less than 90 points
            if re_score < 90:
                no_90 = True
                # Check if RE got less than 60 points
                if re_score < 60:
                    no_60 = True
                    # Check if RE got less than 30 points
                    if re_score < 30:
                        no_30 = True
        
        # Calculate base points
        base_points = 1
        
        # Add points for special achievements
        achievement_points = 0
        if no_90:
            achievement_points += 1
        if no_60:
            achievement_points += 1
        if no_30:
            achievement_points += 1
        
        # Check for RE/CONTRA announcements
        re_announced = game_data.get('re_announced', False)
        contra_announced = game_data.get('contra_announced', False)
        
        # Add points for announcements if the announcing team won
        announcement_points = 0
        if (game.winner.name == 'RE' and re_announced) or (game.winner.name == 'KONTRA' and contra_announced):
            announcement_points += 1
        
        # Special case for 1 vs 3 players
        is_one_vs_three = (re_players == 1 and kontra_players == 3) or (re_players == 3 and kontra_players == 1)
        
        # Calculate total points
        total_points = base_points + achievement_points + announcement_points
        
        # Handle the special case for 1 vs 3
        if is_one_vs_three:
            if game.winner.name == 'RE' and re_players == 1:
                # Single RE player won against 3 KONTRA
                re_points = 3
                if no_90:
                    re_points = 6  # Double points for no 90
                kontra_points = -1
            elif game.winner.name == 'KONTRA' and kontra_players == 1:
                # Single KONTRA player won against 3 RE
                kontra_points = 3
                if no_90:
                    kontra_points = 6  # Double points for no 90
                re_points = -1
            elif game.winner.name == 'RE' and re_players == 3:
                # 3 RE players won against single KONTRA
                re_points = 1
                kontra_points = -3
                if no_90:
                    kontra_points = -6  # Double points for no 90
            else:  # game.winner.name == 'KONTRA' and kontra_players == 3
                # 3 KONTRA players won against single RE
                kontra_points = 1
                re_points = -3
                if no_90:
                    re_points = -6  # Double points for no 90
        else:
            # Normal case (2 vs 2)
            if game.winner.name == 'RE':
                # RE team won
                re_points = total_points / re_players  # Divide points among RE players
                kontra_points = -1  # Each KONTRA player loses 1 point
            else:
                # KONTRA team won
                re_points = -1  # Each RE player loses 1 point
                kontra_points = total_points / kontra_players  # Divide points among KONTRA players
        
        # Apply the points to each player
        for i in range(len(game.teams)):
            if game.teams[i].name == 'RE':
                scoreboard['player_scores'][i] += re_points * multiplier
            else:  # KONTRA team
                scoreboard['player_scores'][i] += kontra_points * multiplier
        
        # Update team scores with multiplier
        game.scores[0] *= multiplier
        game.scores[1] *= multiplier
        
        # Update win counts
        if game.winner == player_team:
            scoreboard['player_wins'] += 1
        else:
            scoreboard['ai_wins'] += 1
    
    return jsonify({
        'state': get_game_state(game_id),
        'trick_completed': trick_completed,
        'trick_winner': trick_winner,
        'is_player_winner': trick_winner == 0 if trick_winner is not None else False,
        'trick_points': trick_points if trick_completed else 0,
        'scoreboard': scoreboard
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

@app.route('/get_last_trick', methods=['GET'])
def get_last_trick():
    """Get the last completed trick."""
    game_id = request.args.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    
    if game_data['last_trick'] is None:
        return jsonify({'error': 'No last trick available'}), 404
    
    return jsonify({
        'last_trick': game_data['last_trick'],
        'trick_players': game_data['last_trick_players'],
        'winner': game_data['last_trick_winner'],
        'trick_points': game_data['last_trick_points']
    })

@app.route('/get_scoreboard', methods=['GET'])
def get_scoreboard():
    """Get the current scoreboard."""
    return jsonify(scoreboard)

@app.route('/announce_re', methods=['POST'])
def announce_re():
    """Announce RE."""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Check if it's the player's turn
    if game.current_player != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Check if the player is on the RE team
    if game.teams[0].name != 'RE':
        return jsonify({'error': 'You are not on the RE team'}), 400
    
    # Check if RE has already been announced
    if game_data.get('re_announced', False):
        return jsonify({'error': 'RE has already been announced'}), 400
    
    # Announce RE
    game_data['re_announced'] = True
    game_data['multiplier'] *= 2  # Double the score multiplier
    
    return jsonify({
        'state': get_game_state(game_id),
        'announcement': 'RE'
    })

@app.route('/announce_contra', methods=['POST'])
def announce_contra():
    """Announce CONTRA."""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Check if it's the player's turn
    if game.current_player != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Check if the player is on the KONTRA team
    if game.teams[0].name != 'KONTRA':
        return jsonify({'error': 'You are not on the KONTRA team'}), 400
    
    # Check if CONTRA has already been announced
    if game_data.get('contra_announced', False):
        return jsonify({'error': 'CONTRA has already been announced'}), 400
    
    # Announce CONTRA
    game_data['contra_announced'] = True
    game_data['multiplier'] *= 2  # Double the score multiplier
    
    return jsonify({
        'state': get_game_state(game_id),
        'announcement': 'CONTRA'
    })

@app.route('/announce_no_90', methods=['POST'])
def announce_no_90():
    """Announce No 90."""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Check if it's the player's turn
    if game.current_player != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Check if RE or CONTRA has been announced
    if not game_data.get('re_announced', False) and not game_data.get('contra_announced', False):
        return jsonify({'error': 'You must announce RE or CONTRA first'}), 400
    
    # Check if the player is on the team that made the initial announcement
    player_team = game.teams[0].name
    if (game_data.get('re_announced', False) and player_team != 'RE') or \
       (game_data.get('contra_announced', False) and player_team != 'KONTRA'):
        return jsonify({'error': 'Only the team that made the initial announcement can announce No 90'}), 400
    
    # Check if No 90 has already been announced
    if game_data.get('no_90_announced', False):
        return jsonify({'error': 'No 90 has already been announced'}), 400
    
    # Announce No 90
    game_data['no_90_announced'] = True
    game_data['multiplier'] *= 2  # Double the score multiplier
    
    return jsonify({
        'state': get_game_state(game_id),
        'announcement': 'No 90'
    })

@app.route('/announce_no_60', methods=['POST'])
def announce_no_60():
    """Announce No 60."""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Check if it's the player's turn
    if game.current_player != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Check if No 90 has been announced
    if not game_data.get('no_90_announced', False):
        return jsonify({'error': 'You must announce No 90 first'}), 400
    
    # Check if the player is on the team that made the initial announcement
    player_team = game.teams[0].name
    if (game_data.get('re_announced', False) and player_team != 'RE') or \
       (game_data.get('contra_announced', False) and player_team != 'KONTRA'):
        return jsonify({'error': 'Only the team that made the initial announcement can announce No 60'}), 400
    
    # Check if No 60 has already been announced
    if game_data.get('no_60_announced', False):
        return jsonify({'error': 'No 60 has already been announced'}), 400
    
    # Announce No 60
    game_data['no_60_announced'] = True
    game_data['multiplier'] *= 2  # Double the score multiplier
    
    return jsonify({
        'state': get_game_state(game_id),
        'announcement': 'No 60'
    })

@app.route('/announce_no_30', methods=['POST'])
def announce_no_30():
    """Announce No 30."""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Check if it's the player's turn
    if game.current_player != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Check if No 60 has been announced
    if not game_data.get('no_60_announced', False):
        return jsonify({'error': 'You must announce No 60 first'}), 400
    
    # Check if the player is on the team that made the initial announcement
    player_team = game.teams[0].name
    if (game_data.get('re_announced', False) and player_team != 'RE') or \
       (game_data.get('contra_announced', False) and player_team != 'KONTRA'):
        return jsonify({'error': 'Only the team that made the initial announcement can announce No 30'}), 400
    
    # Check if No 30 has already been announced
    if game_data.get('no_30_announced', False):
        return jsonify({'error': 'No 30 has already been announced'}), 400
    
    # Announce No 30
    game_data['no_30_announced'] = True
    game_data['multiplier'] *= 2  # Double the score multiplier
    
    return jsonify({
        'state': get_game_state(game_id),
        'announcement': 'No 30'
    })

if __name__ == '__main__':
    print("Starting Doppelkopf final card scenario...")
    args = parse_arguments()
    print(f"Using model: {args.model}")
    print(f"Scenario: {args.scenario}")
    print("Open your browser and navigate to http://localhost:5008")
    socketio.run(app, debug=True, port=5008)
