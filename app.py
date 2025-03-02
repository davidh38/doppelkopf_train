#!/usr/bin/env python3
"""
Flask web application for Doppelkopf card game.
"""

import os
import json
import argparse
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam
from agents.random_agent import select_random_action
from agents.rl_agent import RLAgent

# Parse command line arguments
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Doppelkopf web app with a trained model')
    parser.add_argument('--model', type=str, default='models/final_model.pt',
                        help='Path to a trained model')
    parser.add_argument('--port', type=int, default=5007,
                        help='Port to run the server on')
    return parser.parse_args()

# Get command line arguments
args = parse_arguments()
MODEL_PATH = args.model

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Socket.IO event handlers
@socketio.on('join')
def on_join(data):
    """Join a game room."""
    game_id = data.get('game_id')
    if game_id:
        print(f"Client joined game room: {game_id}")
        join_room(game_id)

# Global game state (in a real application, you'd use a database or session management)
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
        'display': f"{rank_emojis[card.rank]}{suit_emojis[card.suit]} {card.rank.name.capitalize()} of {card.suit.name.capitalize()}" + (" (2)" if card.is_second else ""),
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
        'multiplier': game_data.get('multiplier', 1),
        # Can announce until the fifth card is played
        'can_announce': (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5
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
        
        # Wait for 0.5 seconds after each card is played (only in web interface)
        socketio.sleep(0.5)
        
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
            
            # Pause for 0.3 seconds to show the completed trick
            socketio.sleep(0.3)
            
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
    return jsonify({
        'model_path': MODEL_PATH
    })

@app.route('/new_game', methods=['POST'])
def new_game():
    """Start a new game."""
    # Generate a unique game ID
    game_id = os.urandom(8).hex()
    
    # Initialize game
    game = DoppelkopfGame()
    game.reset()
    
    # We're now keeping the variant selection phase active
    # The phase will end after all players have chosen a variant
    
    # Set the starting player based on the last game's starting player
    # The next player (clockwise) to the one who started the last game should start
    next_starting_player = (scoreboard['last_starting_player'] + 1) % 4
    game.current_player = next_starting_player
    
    # Store the new starting player
    scoreboard['last_starting_player'] = next_starting_player
    
    # Initialize AI agents - using the trained RL model for player 1, random agents for others
    ai_agents = []
    
    # Send progress update to all clients
    socketio.emit('progress_update', {'step': 'model_loading_start', 'message': 'Loading AI model...'})
    print(f"Sending progress update: model_loading_start")
    
    # First AI player (index 1) uses the RL model
    try:
        # Send detailed progress update
        socketio.emit('progress_update', {'step': 'model_loading_details', 'message': f'Loading model from {MODEL_PATH}...'})
        print(f"Sending progress update: model_loading_details")
        
        # Create the RL agent
        rl_agent = RLAgent(game.get_state_size(), game.get_action_size())
        
        # Load the model with a timeout to prevent hanging
        print(f"Loading model from {MODEL_PATH}...")
        
        # Check if the model file exists
        if not os.path.exists(MODEL_PATH):
            print(f"Model file not found: {MODEL_PATH}")
            print("Creating a dummy model for testing...")
            
            # Create a dummy model for testing
            dummy_agent = RLAgent(game.get_state_size(), game.get_action_size())
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            dummy_agent.save(MODEL_PATH)
            print(f"Created dummy model at {MODEL_PATH}")
        
        # Set a flag to track if model loading is complete
        model_loaded = False
        
        # Define a function to load the model with a timeout
        def load_model_with_timeout():
            nonlocal model_loaded
            try:
                print(f"Thread starting to load model from {MODEL_PATH}")
                rl_agent.load(MODEL_PATH)
                model_loaded = True
                print(f"Model loading completed successfully")
                # Send success update
                socketio.emit('progress_update', {'step': 'model_loading_success', 'message': 'Model loaded successfully!'})
                print(f"Sending progress update: model_loading_success")
            except Exception as e:
                print(f"ERROR IN MODEL LOADING: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                print(f"Error details: {e}")
                import traceback
                traceback.print_exc()
                raise e
        
        # Start model loading in a separate thread
        import threading
        model_thread = threading.Thread(target=load_model_with_timeout)
        model_thread.daemon = True
        model_thread.start()
        
        # Wait for the model to load with a timeout
        model_thread.join(timeout=5)  # 5 second timeout
        
        # Check if model loading completed
        if not model_loaded:
            print("Model loading timed out after 5 seconds")
            raise TimeoutError("Model loading timed out")
        
        # Add the agent to the list
        ai_agents.append(rl_agent.select_action)
        print(f"Loaded RL model from {MODEL_PATH} for player 1")
        
        # Send success update
        socketio.emit('progress_update', {'step': 'model_loading_success', 'message': 'Model loaded successfully!'})
        print(f"Sending progress update: model_loading_success")
    except Exception as e:
        error_msg = f"Error loading RL model: {e}"
        print(error_msg)
        print("Using random agent for player 1 instead")
        ai_agents.append(select_random_action)
        
        # Send error update
        socketio.emit('progress_update', {'step': 'model_loading_error', 'message': error_msg}, room=game_id)
        socketio.emit('progress_update', {'step': 'model_loading_fallback', 'message': 'Falling back to random agent...'}, room=game_id)
    
    # Send progress update for next steps
    socketio.emit('progress_update', {'step': 'setup_other_agents', 'message': 'Setting up other AI players...'}, room=game_id)
    
    # Other AI players use random agent
    for i in range(2):
        ai_agents.append(select_random_action)
    
    # Send progress update for game preparation
    socketio.emit('progress_update', {'step': 'game_preparation', 'message': 'Preparing game state...'})
    print(f"Sending progress update: game_preparation")
    
    # Send final progress update when game is ready
    socketio.emit('progress_update', {'step': 'game_ready', 'message': 'Game ready!'})
    print(f"Sending progress update: game_ready")
    
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
        'multiplier': 1,  # Score multiplier (doubled for Re/Contra)
        'starting_player': next_starting_player  # Track the starting player for this game
    }
    
    # Return initial game state
    initial_state = get_game_state(game_id)
    
    # Print the hand for debugging
    print(f"Initial hand: {[card_to_dict(card) for card in game.hands[0]]}")
    
    # If it's not the player's turn, have AI play
    if game.current_player != 0:
        ai_play_turn(game_id)
    
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
    player_idx = data.get('player_idx', 0)  # Default to human player (0)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Set the variant for the player
    result = game.set_variant(variant, player_idx)
    
    if not result:
        return jsonify({'error': 'Invalid variant or not in variant selection phase'}), 400
    
    # If the variant selection phase is over, have AI play if it's not the player's turn
    if not game.variant_selection_phase and game.current_player != 0:
        ai_play_turn(game_id)
    
    # If we're still in variant selection phase, have AI players make their choices
    elif game.variant_selection_phase and game.current_player != 0:
        # Have AI players choose variants until it's the human's turn again or the phase is over
        while game.variant_selection_phase and game.current_player != 0:
            # AI players always choose normal for simplicity
            game.set_variant('normal', game.current_player)
        
        # If the variant selection phase is now over, have AI play if it's not the player's turn
        if not game.variant_selection_phase and game.current_player != 0:
            ai_play_turn(game_id)
    
    return jsonify({
        'state': get_game_state(game_id),
        'variant_selection_phase': game.variant_selection_phase,
        'current_player': game.current_player,
        'game_variant': game.game_variant.name
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
        
        # Store the current trick before clearing it
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
        
        # IMPORTANT: Do not clear the current trick here
        # The current trick will be cleared by the game logic after the tests check it
        # Just set the current player to the trick winner
        game.current_player = trick_winner  # Set the current player to the trick winner
    
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
        
        # Update player scores - winners get +1, losers get -1 (multiplied by team size ratio)
        if game.winner.name == 'RE':
            # RE team won
            re_points = kontra_players  # Each RE player gets +kontra_players
            kontra_points = -re_players  # Each KONTRA player gets -re_players
            
            for i in range(len(game.teams)):
                if game.teams[i].name == 'RE':
                    scoreboard['player_scores'][i] += re_points * multiplier
                else:  # KONTRA team
                    scoreboard['player_scores'][i] += kontra_points * multiplier
        else:
            # KONTRA team won
            re_points = -kontra_players  # Each RE player gets -kontra_players
            kontra_points = re_players  # Each KONTRA player gets +re_players
            
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

@app.route('/announce', methods=['POST'])
def announce():
    """Announce Re or Contra."""
    data = request.json
    game_id = data.get('game_id')
    announcement = data.get('announcement')  # 're' or 'contra'
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Check if more than 5 cards have been played
    # Count cards in completed tricks plus current trick
    cards_played = len(game.current_trick)
    for trick in game.tricks:
        cards_played += len(trick)
    
    if cards_played >= 5:
        return jsonify({'error': 'Cannot announce after the fifth card has been played'}), 400
    
    # Check if the player is in the appropriate team for the announcement
    player_team = game.teams[0]  # Player is always index 0
    
    if announcement == 're' and player_team != PlayerTeam.RE:
        return jsonify({'error': 'Only RE team members can announce Re'}), 400
    elif announcement == 'contra' and player_team != PlayerTeam.KONTRA:
        return jsonify({'error': 'Only KONTRA team members can announce Contra'}), 400
    
    # Update the game data based on the announcement
    if announcement == 're':
        game_data['re_announced'] = True
        game_data['multiplier'] *= 2
    elif announcement == 'contra':
        game_data['contra_announced'] = True
        game_data['multiplier'] *= 2
    else:
        return jsonify({'error': 'Invalid announcement'}), 400
    
    return jsonify({
        'state': get_game_state(game_id),
        're_announced': game_data['re_announced'],
        'contra_announced': game_data['contra_announced'],
        'multiplier': game_data['multiplier']
    })

@app.route('/get_scoreboard', methods=['GET'])
def get_scoreboard():
    """Get the current scoreboard."""
    return jsonify(scoreboard)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=args.port)
