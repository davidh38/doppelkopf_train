"""
Game state route handlers for the Doppelkopf game.
"""
from flask import jsonify, request
from src.backend.game_state import get_game_state
from src.backend.handlers.session_handlers import get_game_id_from_session

def get_game_state_route():
    """
    Get the full game state for the current session.
    
    Returns:
        JSON: The full game state.
    """
    # Get the game ID from the session
    game_id = get_game_id_from_session()
    
    if not game_id:
        return jsonify({
            'success': False,
            'error': 'No game ID found in session'
        }), 400
    
    # Get the game state
    game_state = get_game_state(game_id)
    
    if not game_state:
        return jsonify({
            'success': False,
            'error': 'Game not found'
        }), 404
    
    # Return the full game state
    return jsonify({
        'success': True,
        'state': game_state
    })
