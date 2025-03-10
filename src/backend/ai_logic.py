#!/usr/bin/env python3
"""
AI player logic for the Doppelkopf web application.
"""

import os
import sys
import threading

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent

from src.backend.game.doppelkopf import (
    get_card_value, get_state_size, get_action_size, cards_equal
)
from src.backend.config import games, MODEL_PATH
from src.backend.game_state import print_scoreboard, check_team_revelation, get_game_state, generate_game_summary, update_scoreboard_for_game_over, card_to_dict

def handle_trick_completion(socketio, game_id, game):
    """Handle the completion of a trick."""
    if game.get('trick_winner') is None:
        return False
    
    game_data = games[game_id]
    
    # Calculate points for the trick
    trick_points = sum(get_card_value(card) for card in game['current_trick'])
    
    # Store the last trick information
    game_data['last_trick'] = [card_to_dict(card) for card in game['current_trick']]
    
    # Calculate the starting player for this trick
    starting_player = (game['current_player'] - len(game['current_trick'])) % game['num_players']
    
    # Add player information to each card in the trick
    trick_players = []
    for i in range(len(game['current_trick'])):
        player_idx = (starting_player + i) % game['num_players']
        trick_players.append({
            'name': "You" if player_idx == 0 else f"Player {player_idx}",
            'idx': player_idx,
            'is_current': player_idx == game['current_player']
        })
    
    game_data['last_trick_players'] = trick_players
    game_data['last_trick_winner'] = game['trick_winner']
    game_data['last_trick_points'] = trick_points
    
    # Check if there was a Diamond Ace capture
    diamond_ace_bonus = game.get('last_trick_diamond_ace_bonus', 0)
    diamond_ace_captured = 'diamond_ace_captured' in game
    
    # Emit the trick completed event with points and Diamond Ace capture info
    socketio.emit('trick_completed', {
        'winner': game['trick_winner'],
        'is_player': game['trick_winner'] == 0,
        'trick_points': trick_points,
        'diamond_ace_bonus': diamond_ace_bonus,
        'diamond_ace_captured': diamond_ace_captured
    }, room=game_id)
    
    # Clear the current trick and set the current player to the trick winner
    trick_winner = game['trick_winner']
    game['current_trick'] = []
    game['current_player'] = trick_winner
    game['trick_winner'] = None
    
    # Emit a game state update to reflect the cleared trick
    socketio.emit('game_update', get_game_state(game_id), room=game_id)
    
    return True

def initialize_ai_agents(socketio, game, game_id):
    """Initialize AI agents for the game."""
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
        rl_agent = RLAgent(get_state_size(), get_action_size())
        
        # Load the model with a timeout to prevent hanging
        print(f"Loading model from {MODEL_PATH}...")
        
        # Check if the model file exists
        if not os.path.exists(MODEL_PATH):
            print(f"Model file not found: {MODEL_PATH}")
            print("Creating a dummy model for testing...")
            
            # Create a dummy model for testing
            dummy_agent = RLAgent(get_state_size(), get_action_size())
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
    
    return ai_agents

def ai_play_turn(socketio, game_id):
    """Have AI players take their turns."""
    if game_id not in games:
        return
    
    game_data = games[game_id]
    game = game_data['game']
    ai_agents = game_data['ai_agents']
    
    # Print scoreboard at the beginning of AI turns
    print_scoreboard("Start of AI turns")
    print(f"Last Starting Player: {game_data.get('starting_player', 0)}")
    
    # Keep playing AI turns until it's the human's turn or game is over
    while game['current_player'] != 0 and not game['game_over']:
        # Check if a trick has been completed but not yet cleared
        if game.get('trick_winner') is not None:
            # Handle trick completion
            handle_trick_completion(socketio, game_id, game)
            
            # Print scoreboard after trick completion
            print_scoreboard("After Trick Completion", game)
            
            # If the new current player is the human player, break out of the loop
            if game['current_player'] == 0:
                break
        
        current_player = game['current_player']
        
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
                # Import play_card function
                from src.backend.game.doppelkopf import play_card
                # Play the card
                play_card(game, current_player, action)
                
                # Check if the AI player revealed their team by playing a Queen of Clubs
                check_team_revelation(game, current_player, action, game_data)
            elif action_type == 'announce':
                # Import announce function
                from src.backend.game.doppelkopf import announce
                # Make an announcement
                announce(game, current_player, action)
                # Continue the turn after announcement
                continue
            elif action_type == 'variant':
                # Import set_variant function
                from src.backend.game.doppelkopf import set_variant
                # Set a game variant
                set_variant(game, action, current_player)
                # Continue the turn after setting variant
                continue
        else:
            # Assume it's a card action (for backward compatibility with random agent)
            # Check if action_result is None (which can happen if the agent returns None)
            if action_result is None:
                # Fallback to random action if the agent returns None
                print(f"Warning: AI player {current_player} returned None action, falling back to random action")
                action_result = select_random_action(game, current_player)
            
            # Import play_card function
            from src.backend.game.doppelkopf import play_card
            # Play the card
            play_card(game, current_player, action_result)
            
            # Check if the AI player revealed their team by playing a Queen of Clubs
            if action_result is not None:
                check_team_revelation(game, current_player, action_result, game_data)
        
        # Emit game state update after each AI move
        socketio.emit('game_update', get_game_state(game_id), room=game_id)
        
        # Print scoreboard after each AI move
        print_scoreboard("After AI Move", game)
        
        # Wait for 0.5 seconds after each card is played (only in web interface)
        socketio.sleep(0.5)
        
        # If a trick was completed, pause to show it
        if game.get('trick_winner') is not None:
            # Emit the game state update with the completed trick
            socketio.emit('game_update', get_game_state(game_id), room=game_id)
            
            # Pause for 0.3 seconds to show the completed trick
            socketio.sleep(0.3)
            
            # Handle trick completion
            handle_trick_completion(socketio, game_id, game)
            
            # Check if the game is over after this trick
            if game['game_over']:
                # Generate game summary
                generate_game_summary(game_id)
                
                # Update scoreboard
                update_scoreboard_for_game_over(game_id)
            
            # Emit a game state update to reflect the cleared trick
            socketio.emit('game_update', get_game_state(game_id), room=game_id)
