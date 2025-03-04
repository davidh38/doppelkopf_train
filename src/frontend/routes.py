"""
Routes module for the Doppelkopf game frontend.

This module defines routes that can be used by both the frontend and backend components.
It serves as a bridge between the two, allowing for consistent URL handling.
"""

# Define route constants that can be imported and used by both frontend and backend
class Routes:
    # Page routes
    INDEX = '/'
    
    # API routes
    NEW_GAME = '/new_game'
    SET_VARIANT = '/set_variant'
    PLAY_CARD = '/play_card'
    ANNOUNCE = '/announce'
    GET_CURRENT_TRICK = '/get_current_trick'
    GET_LAST_TRICK = '/get_last_trick'
    GET_AI_HANDS = '/get_ai_hands'
    GET_SCOREBOARD = '/get_scoreboard'
    MODEL_INFO = '/model_info'
    
    # Socket.IO events
    SOCKET_JOIN = 'join'
    SOCKET_GAME_UPDATE = 'game_update'
    SOCKET_TRICK_COMPLETED = 'trick_completed'
    SOCKET_PROGRESS_UPDATE = 'progress_update'

# Function to get the full URL for a route
def get_url(route, base_url=''):
    """
    Get the full URL for a route.
    
    Args:
        route: The route to get the URL for
        base_url: The base URL to prepend to the route (default: '')
    
    Returns:
        The full URL for the route
    """
    return f"{base_url}{route}"

# Function to get the Socket.IO event name
def get_socket_event(event):
    """
    Get the Socket.IO event name.
    
    Args:
        event: The event to get the name for
    
    Returns:
        The Socket.IO event name
    """
    return event
