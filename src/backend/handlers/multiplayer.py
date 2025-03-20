#!/usr/bin/env python3
"""
Multiplayer functionality for the Doppelkopf web application.
These handlers allow a second player to join an existing game and take over an AI position.
"""

from flask import render_template, jsonify, request, session
from src.backend.config import games
from src.backend.game_state import get_game_state
from src.backend.handlers.session_handlers import set_game_id_in_session

def join_page():
    """Render the join game page."""
    # Get a list of active games with available AI positions
    active_games = []
    
    for game_id, game_data in games.items():
        # Skip games that are over
        if game_data['game']['game_over']:
            continue
            
        # Get human positions
        human_positions = game_data['human_positions']
        
        # Create a positions dictionary
        positions = {}
        for i in range(4):  # 4 players in Doppelkopf
            positions[i] = i in human_positions
            
        # Add game to active games list
        active_games.append({
            'id': game_id,
            'positions': positions
        })
    
    return render_template('join.html', active_games=active_games)

def join_game():
    """Handle a request to join a game."""
    data = request.json
    game_id = data.get('game_id')
    player_position = int(data.get('player_position'))
    
    # Validate input
    if not game_id or player_position not in [1, 2, 3]:
        return jsonify({
            'success': False,
            'error': 'Invalid game ID or player position'
        }), 400
    
    # Check if game exists
    if game_id not in games:
        return jsonify({
            'success': False,
            'error': 'Game not found'
        }), 404
    
    game_data = games[game_id]
    
    # Check if game is over
    if game_data['game']['game_over']:
        return jsonify({
            'success': False,
            'error': 'Game is already over'
        }), 400
    
    # Check if position is already taken by a human player
    if player_position in game_data['human_positions']:
        return jsonify({
            'success': False,
            'error': 'Position is already taken by a human player'
        }), 400
    
    # Add the player position to human positions
    game_data['human_positions'].append(player_position)
    
    # Store the game ID and player position in the session
    session['game_id'] = game_id
    session['player_idx'] = player_position
    
    # Return success
    return jsonify({
        'success': True,
        'game_id': game_id,
        'player_position': player_position,
        'state': get_game_state(game_id, player_position)
    })

def get_active_games():
    """Get a list of active games with available AI positions."""
    active_games = []
    
    for game_id, game_data in games.items():
        # Skip games that are over
        if game_data['game']['game_over']:
            continue
            
        # Get human positions
        human_positions = game_data['human_positions']
        
        # Create a positions dictionary
        positions = {}
        for i in range(4):  # 4 players in Doppelkopf
            positions[i] = i in human_positions
            
        # Add game to active games list
        active_games.append({
            'id': game_id,
            'positions': positions
        })
    
    return jsonify({
        'success': True,
        'active_games': active_games
    })
