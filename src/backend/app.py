#!/usr/bin/env python3
"""
Flask web application for Doppelkopf card game.
"""

import os
import json
import argparse
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from src.backend.game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent

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

# Configure Flask to find templates and static files in the frontend directory
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates')),
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/static')))
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
                'score': game.player_scores[i],
                'revealed_team': game_data['revealed_teams'][i]
            } for i in range(1, game.num_players)
        ],
        'revealed_teams': game_data['revealed_teams'],
        'player_score': game.player_scores[player_id],
        'last_trick_points': getattr(game, 'last_trick_points', 0),
        'last_trick_diamond_ace_bonus': getattr(game, 'last_trick_diamond_ace_bonus', 0),
        're_announced': game_data.get('re_announced', False),
        'contra_announced': game_data.get('contra_announced', False),
        'multiplier': game_data.get('multiplier', 1),
        # Can announce until the fifth card is played
        'can_announce': (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5,
        'can_announce_re': game.teams[player_id] == PlayerTeam.RE and (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5,
        'can_announce_contra': game.teams[player_id] == PlayerTeam.KONTRA and (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5
    }
    
    # Add Diamond Ace capture information if available
    if hasattr(game, 'diamond_ace_captured'):
        state['diamond_ace_captured'] = game.diamond_ace_captured
    
    # Add player variant selections if available
    if 'player_variants' in game_data:
        state['player_variants'] = game_data['player_variants']
    
    # Add announcements if available
    if 're_announced' in game_data or 'contra_announced' in game_data:
        state['announcements'] = {
            're': game_data.get('re_announced', False),
            'contra': game_data.get('contra_announced', False),
            'no90': game_data.get('no90_announced', False),
            'no60': game_data.get('no60_announced', False),
            'no30': game_data.get('no30_announced', False),
            'black': game_data.get('black_announced', False)
        }
    
    # Calculate if additional announcements are allowed
    cards_played = len(game.current_trick) + sum(len(trick) for trick in game.tricks)
    
    # Check if player can announce additional announcements (No 90, No 60, No 30, Black)
    # These can only be announced within 5 cards after Re or Contra
    re_announced_card = game_data.get('re_announcement_card', -1)
    contra_announced_card = game_data.get('contra_announcement_card', -1)
    
    # Player can announce additional announcements if:
    # 1. They are on team RE and have announced Re, or they are on team KONTRA and have announced Contra
    # 2. The announcement was made within the last 5 cards
    can_announce_additional_re = (game.teams[player_id] == PlayerTeam.RE and 
                                 game_data.get('re_announced', False) and 
                                 re_announced_card >= 0 and 
                                 cards_played <= re_announced_card + 5)
    
    can_announce_additional_contra = (game.teams[player_id] == PlayerTeam.KONTRA and 
                                     game_data.get('contra_announced', False) and 
                                     contra_announced_card >= 0 and 
                                     cards_played <= contra_announced_card + 5)
    
    # Add flags for additional announcements
    state['can_announce_no90'] = (can_announce_additional_re or can_announce_additional_contra) and not game_data.get('no90_announced', False)
    state['can_announce_no60'] = (can_announce_additional_re or can_announce_additional_contra) and game_data.get('no90_announced', False) and not game_data.get('no60_announced', False)
    state['can_announce_no30'] = (can_announce_additional_re or can_announce_additional_contra) and game_data.get('no60_announced', False) and not game_data.get('no30_announced', False)
    state['can_announce_black'] = (can_announce_additional_re or can_announce_additional_contra) and game_data.get('no30_announced', False) and not game_data.get('black_announced', False)
    
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
    
    # Print scoreboard at the beginning of AI turns
    print("\n=== SCOREBOARD (Start of AI turns) ===")
    print(f"Player Wins: {scoreboard['player_wins']}")
    print(f"AI Wins: {scoreboard['ai_wins']}")
    print(f"Player Scores: {scoreboard['player_scores']}")
    print(f"Last Starting Player: {scoreboard['last_starting_player']}")
    print("=====================================\n")
    
    # Keep playing AI turns until it's the human's turn or game is over
    while game.current_player != 0 and not game.game_over:
        # Check if a trick has been completed but not yet cleared
        if game.trick_winner is not None:
            # A trick has been completed but not yet cleared
            # Clear the trick and set the current player to the trick winner
            trick_winner = game.trick_winner
            game.current_trick = []
            game.current_player = trick_winner
            game.trick_winner = None
            
            # Emit a game state update to reflect the cleared trick
            socketio.emit('game_update', get_game_state(game_id), room=game_id)
            
            # Print scoreboard after trick completion
            print("\n=== SCOREBOARD (After Trick Completion) ===")
            print(f"Player Wins: {scoreboard['player_wins']}")
            print(f"AI Wins: {scoreboard['ai_wins']}")
            print(f"Player Scores: {scoreboard['player_scores']}")
            print(f"Game Scores: {game.scores}")
            print(f"Player Game Scores: {game.player_scores}")
            print("==========================================\n")
            
            # If the new current player is the human player, break out of the loop
            if game.current_player == 0:
                break
        
        current_player = game.current_player
        
        # Ensure current_player is valid (1, 2, or 3)
        if current_player < 1 or current_player > 3:
            print(f"Error: Invalid current_player: {current_player}")
            break
            
        ai_idx = current_player - 1
        
        # Ensure ai_idx is valid (0, 1, or 2)
        if ai_idx < 0 or ai_idx >= len(ai_agents):
            print(f"Error: Invalid AI index: {ai_idx} (current_player: {current_player})")
            break
            
        agent = ai_agents[ai_idx]
        
        # Handle both class-based and function-based agents
        try:
            if hasattr(agent, 'select_action'):
                action_result = agent.select_action(game, current_player)
            else:
                action_result = agent(game, current_player)
            
            # Debug output to help diagnose AI actions
            print(f"AI player {current_player} selected action: {action_result}")
        except Exception as e:
            print(f"Error in AI action selection: {str(e)}")
            # Fallback to random action if there's an error
            action_result = select_random_action(game, current_player)
            print(f"Falling back to random action: {action_result}")
        
        # Handle different action types
        if isinstance(action_result, tuple) and len(action_result) == 2:
            action_type, action = action_result
            
            if action_type == 'card':
                # Play the card
                game.play_card(current_player, action)
                
                # Check if the AI player revealed their team by playing a Queen of Clubs
                if action.suit == Suit.CLUBS and action.rank == Rank.QUEEN:
                    print(f"AI player {current_player} revealed team by playing Queen of Clubs (tuple case)")
                    games[game_id]['revealed_teams'][current_player] = True
            elif action_type == 'announce':
                # Make an announcement
                game.announce(current_player, action)
                # Continue the turn after announcement
                continue
            elif action_type == 'variant':
                # Set a game variant
                game.set_variant(action, current_player)
                # Continue the turn after setting variant
                continue
        else:
            # Assume it's a card action (for backward compatibility with random agent)
            # Check if action_result is None (which can happen if the agent returns None)
            if action_result is None:
                # Fallback to random action if the agent returns None
                print(f"Warning: AI player {current_player} returned None action, falling back to random action")
                action_result = select_random_action(game, current_player)
                
            game.play_card(current_player, action_result)
            
            # Check if the AI player revealed their team by playing a Queen of Clubs
            if action_result is not None:
                # Debug output to help diagnose team revelation
                if action_result.suit == Suit.CLUBS and action_result.rank == Rank.QUEEN:
                    print(f"AI player {current_player} revealed team by playing Queen of Clubs")
                    games[game_id]['revealed_teams'][current_player] = True
        
        # Emit game state update after each AI move
        socketio.emit('game_update', get_game_state(game_id), room=game_id)
        
        # Print scoreboard after each AI move
        print("\n=== SCOREBOARD (After AI Move) ===")
        print(f"Player Wins: {scoreboard['player_wins']}")
        print(f"AI Wins: {scoreboard['ai_wins']}")
        print(f"Player Scores: {scoreboard['player_scores']}")
        print(f"Game Scores: {game.scores}")
        print(f"Player Game Scores: {game.player_scores}")
        print("=================================\n")
        
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
            
            # Check if there was a Diamond Ace capture
            diamond_ace_bonus = getattr(game, 'last_trick_diamond_ace_bonus', 0)
            diamond_ace_captured = hasattr(game, 'diamond_ace_captured')
            
            # Emit the trick completed event with points and Diamond Ace capture info
            socketio.emit('trick_completed', {
                'winner': trick_winner,
                'is_player': trick_winner == 0,
                'trick_points': trick_points,
                'diamond_ace_bonus': diamond_ace_bonus,
                'diamond_ace_captured': diamond_ace_captured
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
    
    # Initialize player variants dictionary
    player_variants = {}
    
    # Have AI players choose variants immediately
    while game.variant_selection_phase and game.current_player != 0:
        # AI players always choose normal for simplicity
        current_player = game.current_player
        game.set_variant('normal', current_player)
        
        # Store the AI player's variant selection
        player_variants[current_player] = 'normal'
    
    # Only end the variant selection phase if it's not the human player's turn
    if game.variant_selection_phase and game.current_player != 0:
        # Force the variant selection phase to end
        game.variant_selection_phase = False
        # Set a default game variant if none was selected
        if game.game_variant == GameVariant.NORMAL:
            print("Setting default game variant to NORMAL")
    
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
        'no90_announced': False,
        'no60_announced': False,
        'no30_announced': False,
        'black_announced': False,
        're_announcement_card': -1,  # Card number when Re was announced (-1 means not announced)
        'contra_announcement_card': -1,  # Card number when Contra was announced (-1 means not announced)
        'multiplier': 1,  # Score multiplier (doubled for Re/Contra and additional announcements)
        'starting_player': next_starting_player,  # Track the starting player for this game
        'player_variants': player_variants,  # Store player variant selections
        'revealed_teams': [False, False, False, False]  # Track which players have revealed their team
    }
    
    # Return initial game state
    initial_state = get_game_state(game_id)
    
    # Print the hand for debugging
    print(f"Initial hand: {[card_to_dict(card) for card in game.hands[0]]}")
    
    # If it's not the player's turn, have AI play
    if game.current_player != 0:
        print(f"GAME STATE: Starting AI turns from new_game. Current player: {game.current_player}")
        print(f"GAME STATE: Game variant: {game.game_variant.name}")
        print(f"GAME STATE: Teams: {[team.name for team in game.teams]}")
        print(f"GAME STATE: Hands: {[len(hand) for hand in game.hands]}")
        print(f"GAME STATE: AI agents: {ai_agents}")
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
    
    # Store the player's variant selection
    if 'player_variants' not in games[game_id]:
        games[game_id]['player_variants'] = {}
    
    # Store the variant selection for this player
    games[game_id]['player_variants'][player_idx] = variant
    
    # If the variant selection phase is over, have AI play if it's not the player's turn
    if not game.variant_selection_phase and game.current_player != 0:
        print(f"GAME STATE: Starting AI turns from set_variant. Current player: {game.current_player}")
        print(f"GAME STATE: Game variant: {game.game_variant.name}")
        print(f"GAME STATE: Teams: {[team.name for team in game.teams]}")
        print(f"GAME STATE: Hands: {[len(hand) for hand in game.hands]}")
        print(f"GAME STATE: AI agents: {games[game_id]['ai_agents']}")
        ai_play_turn(game_id)
    
    # If we're still in variant selection phase, have AI players make their choices
    elif game.variant_selection_phase and game.current_player != 0:
        # Have AI players choose variants until it's the human's turn again or the phase is over
        while game.variant_selection_phase and game.current_player != 0:
            # AI players always choose normal for simplicity
            current_player = game.current_player
            game.set_variant('normal', current_player)
            
            # Store the AI player's variant selection
            if 'player_variants' not in games[game_id]:
                games[game_id]['player_variants'] = {}
            games[game_id]['player_variants'][current_player] = 'normal'
        
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
    
    # Print scoreboard after player's move
    print("\n=== SCOREBOARD (After Player Move) ===")
    print(f"Player Wins: {scoreboard['player_wins']}")
    print(f"AI Wins: {scoreboard['ai_wins']}")
    print(f"Player Scores: {scoreboard['player_scores']}")
    print(f"Game Scores: {game.scores}")
    print(f"Player Game Scores: {game.player_scores}")
    print("====================================\n")
    
    # Check if the player revealed their team by playing a Queen of Clubs
    if selected_card.suit == Suit.CLUBS and selected_card.rank == Rank.QUEEN:
        games[game_id]['revealed_teams'][0] = True
    
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
        
        # Check if there was a Diamond Ace capture
        diamond_ace_bonus = getattr(game, 'last_trick_diamond_ace_bonus', 0)
        diamond_ace_captured = hasattr(game, 'diamond_ace_captured')
        
        # Emit the trick completed event with points and Diamond Ace capture info
        socketio.emit('trick_completed', {
            'winner': trick_winner,
            'is_player': trick_winner == 0,
            'trick_points': trick_points,
            'diamond_ace_bonus': diamond_ace_bonus,
            'diamond_ace_captured': diamond_ace_captured
        }, room=game_id)
        
        # Clear the current trick and set the current player to the trick winner
        game.current_trick = []
        game.current_player = trick_winner  # Set the current player to the trick winner
        game.trick_winner = None
        
        # Print scoreboard after trick completion
        print("\n=== SCOREBOARD (After Player Trick Completion) ===")
        print(f"Player Wins: {scoreboard['player_wins']}")
        print(f"AI Wins: {scoreboard['ai_wins']}")
        print(f"Player Scores: {scoreboard['player_scores']}")
        print(f"Game Scores: {game.scores}")
        print(f"Player Game Scores: {game.player_scores}")
        print("==============================================\n")
    
    # Have AI players take their turns
    ai_play_turn(game_id)
    
    # Check if game is over and update scoreboard
    if game.game_over:
        player_team = game.teams[0]
        game_data = games[game_id]
        multiplier = game_data.get('multiplier', 1)
        
        print("\n=== SCOREBOARD (Before Game Over Update) ===")
        print(f"Player Wins: {scoreboard['player_wins']}")
        print(f"AI Wins: {scoreboard['ai_wins']}")
        print(f"Player Scores: {scoreboard['player_scores']}")
        print(f"Game Scores: {game.scores}")
        print(f"Player Game Scores: {game.player_scores}")
        print("=========================================\n")
        
        # In Doppelkopf, the base score is 1 point for winning
        # The multiplier is applied for announcements (Re, Contra, No 90, etc.)
        
        # Count players in each team
        re_players = sum(1 for team in game.teams if team.name == 'RE')
        kontra_players = sum(1 for team in game.teams if team.name == 'KONTRA')
        
        # Update player scores - winners get +1, losers get -1
        if game.winner.name == 'RE':
            # RE team won
            for i in range(len(game.teams)):
                if game.teams[i].name == 'RE':
                    scoreboard['player_scores'][i] += 1 * multiplier  # Winners get positive points
                else:  # KONTRA team
                    scoreboard['player_scores'][i] -= 1 * multiplier  # Losers get negative points
        else:
            # KONTRA team won
            for i in range(len(game.teams)):
                if game.teams[i].name == 'RE':
                    scoreboard['player_scores'][i] -= 1 * multiplier  # Losers get negative points
                else:  # KONTRA team
                    scoreboard['player_scores'][i] += 1 * multiplier  # Winners get positive points
        
        # Don't modify game.scores with multiplier - they should add up to 240 (plus any bonus points)
        # The multiplier is only applied to player scores
        
        # Update win counts
        if game.winner == player_team:
            scoreboard['player_wins'] += 1
        else:
            scoreboard['ai_wins'] += 1
            
        print("\n=== SCOREBOARD (After Game Over Update) ===")
        print(f"Player Wins: {scoreboard['player_wins']}")
        print(f"AI Wins: {scoreboard['ai_wins']}")
        print(f"Player Scores: {scoreboard['player_scores']}")
        print(f"Game Scores: {game.scores}")
        print(f"Player Game Scores: {game.player_scores}")
        print("========================================\n")
    
    # Create a response object
    response_data = {
        'state': get_game_state(game_id),
        'trick_completed': trick_completed,
        'trick_winner': trick_winner,
        'is_player_winner': trick_winner == 0 if trick_winner is not None else False,
        'trick_points': trick_points if trick_completed else 0,
        'scoreboard': scoreboard
    }
    
    # If the game is over, include the player scores in the state and add a game summary
    if game.game_over:
        # Make sure the player scores are included in the state
        response_data['state']['player_scores'] = scoreboard['player_scores']
        
        # Also include the scoreboard in the state for easy access
        response_data['state']['scoreboard'] = {
            'player_wins': scoreboard['player_wins'],
            'ai_wins': scoreboard['ai_wins'],
            'player_scores': scoreboard['player_scores']
        }
        
        # Create a detailed game summary
        game_data = games[game_id]
        multiplier = game_data.get('multiplier', 1)
        
        # Count players in each team
        re_players = sum(1 for team in game.teams if team.name == 'RE')
        kontra_players = sum(1 for team in game.teams if team.name == 'KONTRA')
        
        # Calculate points for each team
        if game.winner.name == 'RE':
            # RE team won
            re_points = kontra_players  # Each RE player gets +kontra_players
            kontra_points = -re_players  # Each KONTRA player gets -re_players
        else:
            # KONTRA team won
            re_points = -kontra_players  # Each RE player gets -kontra_players
            kontra_points = re_players  # Each KONTRA player gets +re_players
        
        # Apply multiplier
        re_points_with_multiplier = re_points * multiplier
        kontra_points_with_multiplier = kontra_points * multiplier
        
        # Create summary text
        summary_text = f"Game Over! {game.winner.name} team wins!\n\n"
        
        # Add team composition
        summary_text += "Team Composition:\n"
        for i, team in enumerate(game.teams):
            player_name = "You" if i == 0 else f"Player {i}"
            summary_text += f"- {player_name}: {team.name}\n"
        
        # Add trick points information
        summary_text += "\nTrick Points:\n"
        summary_text += f"- RE team: {game.scores[0]} points\n"
        summary_text += f"- KONTRA team: {game.scores[1]} points\n"
        summary_text += f"- Total: {game.scores[0] + game.scores[1]} points\n"
        
        # Check if there were any special bonuses
        if hasattr(game, 'diamond_ace_captured'):
            diamond_ace_captures = [capture for capture in game.diamond_ace_captured if capture.get('type') == 'diamond_ace' or not capture.get('type')]
            forty_plus_captures = [capture for capture in game.diamond_ace_captured if capture.get('type') == 'forty_plus']
            
            if diamond_ace_captures:
                summary_text += "\nDiamond Ace Captures:\n"
                for capture in diamond_ace_captures:
                    winner_name = "You" if capture['winner'] == 0 else f"Player {capture['winner']}"
                    loser_name = "You" if capture['loser'] == 0 else f"Player {capture['loser']}"
                    summary_text += f"- {winner_name} ({capture['winner_team']}) captured a Diamond Ace from {loser_name} ({capture['loser_team']})\n"
                summary_text += f"  This adds/subtracts 1 point per capture to the trick points\n"
            
            if forty_plus_captures:
                summary_text += "\n40+ Point Tricks:\n"
                for capture in forty_plus_captures:
                    winner_name = "You" if capture['winner'] == 0 else f"Player {capture['winner']}"
                    summary_text += f"- {winner_name} ({capture['winner_team']}) won a trick worth {capture['points']} points\n"
                summary_text += f"  This adds/subtracts 1 point per 40+ trick to the trick points\n"
        
        # Check for special achievements (no 90, no 60, no 30, black)
        re_score = game.scores[0]
        kontra_score = game.scores[1]
        
        # Add special achievements section
        summary_text += "\nSpecial Achievements:\n"
        
        # Base points for winning
        if game.winner.name == 'RE':
            summary_text += f"- RE wins: +1\n"
        else:
            summary_text += f"- KONTRA wins: +1\n"
        
        # Check for no 90 achievement (opponent got less than 90 points)
        if game.winner.name == 'RE' and kontra_score < 90:
            summary_text += f"- RE plays no 90: +1 (KONTRA got {kontra_score} points)\n"
        elif game.winner.name == 'KONTRA' and re_score < 90:
            summary_text += f"- KONTRA plays no 90: +1 (RE got {re_score} points)\n"
        
        # Check for no 60 achievement (opponent got less than 60 points)
        if game.winner.name == 'RE' and kontra_score < 60:
            summary_text += f"- RE plays no 60: +1 (KONTRA got {kontra_score} points)\n"
        elif game.winner.name == 'KONTRA' and re_score < 60:
            summary_text += f"- KONTRA plays no 60: +1 (RE got {re_score} points)\n"
        
        # Check for no 30 achievement (opponent got less than 30 points)
        if game.winner.name == 'RE' and kontra_score < 30:
            summary_text += f"- RE plays no 30: +1 (KONTRA got {kontra_score} points)\n"
        elif game.winner.name == 'KONTRA' and re_score < 30:
            summary_text += f"- KONTRA plays no 30: +1 (RE got {re_score} points)\n"
        
        # Check for black achievement (opponent got 0 points)
        if game.winner.name == 'RE' and kontra_score == 0:
            summary_text += f"- RE plays black: +1 (KONTRA got 0 points)\n"
        elif game.winner.name == 'KONTRA' and re_score == 0:
            summary_text += f"- KONTRA plays black: +1 (RE got 0 points)\n"
        
        summary_text += "\nScore Calculation:\n"
        
        # Add announcement information if any
        if game_data.get('re_announced', False) or game_data.get('contra_announced', False):
            summary_text += "Announcements:\n"
            if game_data.get('re_announced', False):
                summary_text += "- RE announced: +1\n"
            if game_data.get('contra_announced', False):
                summary_text += "- CONTRA announced: +1\n"
            if game_data.get('no90_announced', False):
                summary_text += "- No 90 announced: +1\n"
            if game_data.get('no60_announced', False):
                summary_text += "- No 60 announced: +1\n"
            if game_data.get('no30_announced', False):
                summary_text += "- No 30 announced: +1\n"
            if game_data.get('black_announced', False):
                summary_text += "- Black announced: +1\n"
            
            summary_text += f"- Score multiplier: {multiplier}x\n\n"
        
        # Add base point calculation
        summary_text += "Base Points:\n"
        summary_text += f"- Winning team: +1 point per player\n"
        summary_text += f"- Losing team: -1 point per player\n\n"
        
        # Add multiplier effect if applicable
        if multiplier > 1:
            summary_text += "With Multiplier:\n"
            summary_text += f"- Winning team: +1 × {multiplier} = +{multiplier} points per player\n"
            summary_text += f"- Losing team: -1 × {multiplier} = -{multiplier} points per player\n\n"
        
        # Add final scores
        summary_text += "Final Scores:\n"
        for i, team in enumerate(game.teams):
            player_name = "You" if i == 0 else f"Player {i}"
            if (team.name == 'RE' and game.winner.name == 'RE') or (team.name == 'KONTRA' and game.winner.name == 'KONTRA'):
                # This player is on the winning team
                points = f"+{multiplier}"
            else:
                # This player is on the losing team
                points = f"-{multiplier}"
            total_score = scoreboard['player_scores'][i]
            summary_text += f"- {player_name}: {points} points (Total: {total_score})\n"
        
        # Add the summary to the response
        response_data['game_summary'] = summary_text
    
    return jsonify(response_data)

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
    """Announce Re, Contra, or additional announcements (No 90, No 60, No 30, Black)."""
    data = request.json
    game_id = data.get('game_id')
    announcement = data.get('announcement')  # 're', 'contra', 'no90', 'no60', 'no30', 'black'
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Count cards played
    cards_played = len(game.current_trick)
    for trick in game.tricks:
        cards_played += len(trick)
    
    # Check if the player is in the appropriate team for the announcement
    player_team = game.teams[0]  # Player is always index 0
    
    # Handle Re and Contra announcements
    if announcement in ['re', 'contra']:
        # Check if more than 5 cards have been played
        if cards_played >= 5:
            return jsonify({'error': 'Cannot announce Re or Contra after the fifth card has been played'}), 400
        
        # Check if the player is in the appropriate team
        if announcement == 're' and player_team != PlayerTeam.RE:
            return jsonify({'error': 'Only RE team members can announce Re'}), 400
        elif announcement == 'contra' and player_team != PlayerTeam.KONTRA:
            return jsonify({'error': 'Only KONTRA team members can announce Contra'}), 400
        
        # Update the game data based on the announcement
        if announcement == 're':
            game_data['re_announced'] = True
            game_data['re_announcement_card'] = cards_played  # Track when Re was announced
            game_data['multiplier'] = 2  # Set multiplier to 2 for Re
        elif announcement == 'contra':
            game_data['contra_announced'] = True
            game_data['contra_announcement_card'] = cards_played  # Track when Contra was announced
            game_data['multiplier'] = 2  # Set multiplier to 2 for Contra
    
    # Handle additional announcements (No 90, No 60, No 30, Black)
    elif announcement in ['no90', 'no60', 'no30', 'black']:
        # Check if the player has announced Re or Contra
        if player_team == PlayerTeam.RE and not game_data.get('re_announced', False):
            return jsonify({'error': 'You must announce Re before making additional announcements'}), 400
        elif player_team == PlayerTeam.KONTRA and not game_data.get('contra_announced', False):
            return jsonify({'error': 'You must announce Contra before making additional announcements'}), 400
        
        # Check if the announcement was made within 5 cards after Re or Contra
        re_announced_card = game_data.get('re_announcement_card', -1)
        contra_announced_card = game_data.get('contra_announcement_card', -1)
        
        if player_team == PlayerTeam.RE and (re_announced_card < 0 or cards_played > re_announced_card + 5):
            return jsonify({'error': 'Additional announcements must be made within 5 cards after Re'}), 400
        elif player_team == PlayerTeam.KONTRA and (contra_announced_card < 0 or cards_played > contra_announced_card + 5):
            return jsonify({'error': 'Additional announcements must be made within 5 cards after Contra'}), 400
        
        # Check if the announcements are made in the correct order
        if announcement == 'no90' and not game_data.get('no90_announced', False):
            game_data['no90_announced'] = True
            game_data['multiplier'] = 3  # Set multiplier to 3 for No 90
        elif announcement == 'no60' and game_data.get('no90_announced', False) and not game_data.get('no60_announced', False):
            game_data['no60_announced'] = True
            game_data['multiplier'] = 4  # Set multiplier to 4 for No 60
        elif announcement == 'no30' and game_data.get('no60_announced', False) and not game_data.get('no30_announced', False):
            game_data['no30_announced'] = True
            game_data['multiplier'] = 5  # Set multiplier to 5 for No 30
        elif announcement == 'black' and game_data.get('no30_announced', False) and not game_data.get('black_announced', False):
            game_data['black_announced'] = True
            game_data['multiplier'] = 6  # Set multiplier to 6 for Black
        else:
            return jsonify({'error': 'Invalid announcement order'}), 400
    else:
        return jsonify({'error': 'Invalid announcement'}), 400
    
    # Print scoreboard after announcement
    print("\n=== SCOREBOARD (After Announcement) ===")
    print(f"Player Wins: {scoreboard['player_wins']}")
    print(f"AI Wins: {scoreboard['ai_wins']}")
    print(f"Player Scores: {scoreboard['player_scores']}")
    print(f"Game Scores: {game.scores}")
    print(f"Player Game Scores: {game.player_scores}")
    print("=====================================\n")
    
    return jsonify({
        'state': get_game_state(game_id),
        're_announced': game_data.get('re_announced', False),
        'contra_announced': game_data.get('contra_announced', False),
        'no90_announced': game_data.get('no90_announced', False),
        'no60_announced': game_data.get('no60_announced', False),
        'no30_announced': game_data.get('no30_announced', False),
        'black_announced': game_data.get('black_announced', False),
        'multiplier': game_data.get('multiplier', 1)
    })

@app.route('/get_ai_hands', methods=['GET'])
def get_ai_hands():
    """Get the hands of AI players for debugging purposes."""
    game_id = request.args.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Get the AI hands (players 1, 2, and 3)
    ai_hands = {
        'player1': [card_to_dict(card) for card in game.hands[1]],
        'player2': [card_to_dict(card) for card in game.hands[2]],
        'player3': [card_to_dict(card) for card in game.hands[3]]
    }
    
    return jsonify(ai_hands)

@app.route('/get_scoreboard', methods=['GET'])
def get_scoreboard():
    """Get the current scoreboard."""
    return jsonify(scoreboard)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=args.port)
