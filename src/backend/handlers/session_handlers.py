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

def get_player_idx_from_session():
    """
    Get the player index from the session.
    
    Returns:
        int: The player index or 0 if not found.
    """
    return session.get('player_idx', 0)

def set_game_id_in_session(game_id):
    """
    Store the game ID in the session.
    
    Args:
        game_id (str): The game ID to store.
    """
    session['game_id'] = game_id

def set_player_idx_in_session(player_idx):
    """
    Store the player index in the session.
    
    Args:
        player_idx (int): The player index to store.
    """
    session['player_idx'] = player_idx

def clear_game_id_from_session():
    """
    Remove the game ID from the session.
    """
    if 'game_id' in session:
        del session['game_id']

def clear_player_idx_from_session():
    """
    Remove the player index from the session.
    """
    if 'player_idx' in session:
        del session['player_idx']

def clear_session():
    """
    Clear all game-related data from the session.
    """
    clear_game_id_from_session()
    clear_player_idx_from_session()

def check_session_route():
    """
    Check if there's an active game session.
    
    Returns:
        JSON: Session information.
    """
    game_id = get_game_id_from_session()
    player_idx = get_player_idx_from_session()
    
    if game_id:
        return jsonify({
            'has_session': True,
            'game_id': game_id,
            'player_idx': player_idx
        })
    else:
        return jsonify({
            'has_session': False
        })
