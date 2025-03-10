#!/usr/bin/env python3
"""
Game management route handlers for the Doppelkopf web application.
These include starting a new game and getting the scoreboard.
"""

import os
import random
from flask import jsonify

from src.backend.game.doppelkopf import (
    create_game_state, get_legal_actions, set_variant
)
from src.backend.config import games, scoreboard
from src.backend.game_state import get_game_state
from src.backend.ai_logic import ai_play_turn, initialize_ai_agents

def new_game(socketio):
    """Start a new game."""
    # Generate a unique game ID
    game_id = os.urandom(8).hex()
    
    # Initialize game
    game = create_game_state()
    
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
        'multiplier': 1,
        'starting_player': next_starting_player,
        'player_variants': player_variants,
        'revealed_teams': [False, False, False, False]
    }
    
    # If it's not the player's turn, have AI choose a variant
    if game['current_player'] != 0:
        # Have the current AI player choose a variant
        current_player = game['current_player']
        set_variant(game, 'normal', current_player)
        games[game_id]['player_variants'][current_player] = 'normal'
        
        # Move to the next player
        # We don't automatically have all AI players choose here
    else:
        # Set legal actions for the player if it's their turn
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player in new game: {game['legal_actions']}")
    
    # Return initial game state
    return jsonify({
        'game_id': game_id,
        'state': get_game_state(game_id)
    })

def get_scoreboard():
    """Get the current scoreboard."""
    return jsonify(scoreboard)
