"""
Session handling functions for the Doppelkopf game.
"""
from flask import session, jsonify

def get_game_id_from_session():
    """
    Get the game ID from the session.
    
    Returns:
        str: The game ID or None if not found.
    """
    return session.get('game_id')

def set_game_id_in_session(game_id):
    """
    Store the game ID in the session.
    
    Args:
        game_id (str): The game ID to store.
    """
    session['game_id'] = game_id

def clear_game_id_from_session():
    """
    Remove the game ID from the session.
    """
    if 'game_id' in session:
        del session['game_id']

def check_session_route():
    """
    Check if there's an active game session.
    
    Returns:
        JSON: Session information.
    """
    game_id = get_game_id_from_session()
    
    if game_id:
        return jsonify({
            'has_session': True,
            'game_id': game_id,
            'player_idx': 0  # Human player is always at index 0
        })
    else:
        return jsonify({
            'has_session': False
        })
