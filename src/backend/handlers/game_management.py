#!/usr/bin/env python3
"""
Game management route handlers for the Doppelkopf web application.
These include starting a new game and getting the scoreboard.
"""

import os
import random
from flask import jsonify
from src.backend.handlers.session_handlers import set_game_id_in_session, set_player_idx_in_session

from src.backend.game.doppelkopf import (
    create_game_state, get_legal_actions, set_variant
)
from src.backend.config import games, scoreboard
from src.backend.game_state import get_game_state
from src.backend.ai_logic import ai_play_turn, initialize_ai_agents

from src.backend.config import games, scoreboard, args

def new_game(socketio):
    """Start a new game with configurable number of human players."""
    # Generate a unique game ID
    game_id = os.urandom(8).hex()
    
    # Initialize game
    game = create_game_state()
    
    # Determine human player positions
    num_humans = args.human
    human_positions = []
    if args.human_settings == 'first':
        # Place human players in first positions
        human_positions = list(range(num_humans))
    else:  # random
        # Randomly place human players
        all_positions = list(range(4))
        random.shuffle(all_positions)
        human_positions = all_positions[:num_humans]
    
    # For the first game, randomly select a card giver
    if 'last_card_giver' not in scoreboard:
        card_giver = random.randint(0, 3)
        scoreboard['last_card_giver'] = card_giver
    else:
        # For subsequent games, rotate the card giver role
        card_giver = (scoreboard['last_card_giver'] + 1) % 4
        scoreboard['last_card_giver'] = card_giver
    
    # Set the card giver in the game state
    game['card_giver'] = card_giver
    
    # The player next to the card giver starts with choosing the variant
    next_starting_player = (card_giver + 1) % 4
    game['current_player'] = next_starting_player
    
    # Store the new starting player
    scoreboard['last_starting_player'] = next_starting_player
    
    # Initialize AI agents
    ai_agents = initialize_ai_agents(socketio, game, game_id)
    
    # Send progress updates
    socketio.emit('progress_update', {'step': 'game_preparation', 'message': 'Preparing game state...'})
    socketio.emit('progress_update', {'step': 'game_ready', 'message': 'Game ready!'})
    
    # Initialize player variants dictionary
    player_variants = {}
    
    # Have AI players choose variants one by one, starting with the player after the card giver
    # This ensures the game variant is shown for each player in sequence
    
    # Store game state
    games[game_id] = {
        'game': game,
        'ai_agents': ai_agents,
        'human_positions': human_positions,  # Store human player positions
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
        're_announcement_card': -1,
        'contra_announcement_card': -1,
        'starting_player': next_starting_player,
        'player_variants': player_variants,
        'revealed_teams': [False, False, False, False]
    }
    
    # If it's not any human player's turn, have AI players choose variants in sequence
    if game['current_player'] not in human_positions:
        # Have all AI players choose their variants in sequence until it's a human player's turn or phase is over
        while game['variant_selection_phase'] and game['current_player'] not in human_positions:
            current_player = game['current_player']
            
            # Emit an event to show the variant selection animation for this AI player
            socketio.emit('ai_selecting_variant', {
                'player': current_player,
                'variant': 'normal'
            })
            
            # Add a small delay to allow the animation to be visible
            import time
            time.sleep(0.5)
            
            # Set the variant for the AI player
            set_variant(game, 'normal', current_player)
            games[game_id]['player_variants'][current_player] = 'normal'
            
            # Update the game state for the client
            socketio.emit('game_update', get_game_state(game_id), room=game_id)
    else:
        # Set legal actions if it's a human player's turn
        if game['current_player'] in human_positions:
            game['legal_actions'] = get_legal_actions(game, game['current_player'])
            print(f"Setting legal actions for player {game['current_player']} in new game: {game['legal_actions']}")
    
    # Store the game ID and player index in the session
    set_game_id_in_session(game_id)
    set_player_idx_in_session(0)  # First player is always at index 0
    
    # Return initial game state
    return jsonify({
        'game_id': game_id,
        'state': get_game_state(game_id)
    })

def get_scoreboard():
    """Get the current scoreboard."""
    return jsonify(scoreboard)
