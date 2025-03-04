#!/usr/bin/env python3
"""
Socket.IO event handlers for the Doppelkopf web application.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask_socketio import join_room

def register_socket_handlers(socketio):
    """Register all Socket.IO event handlers."""
    
    @socketio.on('join')
    def on_join(data):
        """Join a game room."""
        game_id = data.get('game_id')
        if game_id:
            print(f"Client joined game room: {game_id}")
            join_room(game_id)
