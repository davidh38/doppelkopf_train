#!/usr/bin/env python3
"""
HTTP route handlers for the Doppelkopf web application.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import request

from src.backend.handlers.basic_routes import (
    index, model_info
)
from src.backend.handlers.game_management import (
    new_game, get_scoreboard
)
from src.backend.handlers.game_actions import (
    set_variant_route, play_card_route, announce_route
)
from src.backend.handlers.game_state_routes import (
    get_current_trick, get_last_trick, round_summary, get_ai_hands, get_game_state_route
)
from src.backend.handlers.session_handlers import check_session_route
from src.backend.handlers.multiplayer import join_page, join_game, get_active_games
from src.backend.card_utils import cards_equal
from src.backend.config import games, scoreboard

def register_routes(app, socketio):
    """Register all HTTP route handlers."""
    
    @app.route('/')
    def index_route():
        """Render the main game page."""
        return index()
        
    @app.route('/game-summary/<game_id>')
    def game_summary_route(game_id):
        """Render the round summary page."""
        return round_summary(game_id)

    @app.route('/model_info', methods=['GET'])
    def model_info_route():
        """Get information about the model being used."""
        return model_info()

    @app.route('/new_game', methods=['POST'])
    def new_game_route():
        """Start a new game."""
        return new_game(socketio)

    @app.route('/set_variant', methods=['POST'])
    def set_variant_route_handler():
        """Set the game variant."""
        data = request.json
        return set_variant_route(socketio, data)

    @app.route('/play_card', methods=['POST'])
    def play_card_route_handler():
        """Play a card."""
        data = request.json
        return play_card_route(socketio, data)

    @app.route('/get_current_trick', methods=['GET'])
    def get_current_trick_route():
        """Get the current trick data for debugging."""
        game_id = request.args.get('game_id')
        return get_current_trick(game_id)

    @app.route('/get_last_trick', methods=['GET'])
    def get_last_trick_route():
        """Get the last completed trick."""
        game_id = request.args.get('game_id')
        return get_last_trick(game_id)

    @app.route('/announce', methods=['POST'])
    def announce_route_handler():
        """Announce Re, Contra, or additional announcements (No 90, No 60, No 30, Black)."""
        data = request.json
        return announce_route(socketio, data)

    @app.route('/get_ai_hands', methods=['GET'])
    def get_ai_hands_route():
        """Get the hands of AI players for debugging purposes."""
        game_id = request.args.get('game_id')
        return get_ai_hands(game_id)

    @app.route('/get_scoreboard', methods=['GET'])
    def get_scoreboard_route():
        """Get the current scoreboard."""
        return get_scoreboard()
        
    @app.route('/get_game_state', methods=['GET'])
    def get_game_state_route_handler():
        """Get the full game state for the current session."""
        return get_game_state_route()
        
    @app.route('/check_session', methods=['GET'])
    def check_session_route_handler():
        """Check if there's an active game session."""
        return check_session_route()
        
    @app.route('/join', methods=['GET'])
    def join_route():
        """Render the join game page."""
        return join_page()
        
    @app.route('/join_game', methods=['POST'])
    def join_game_route():
        """Handle a request to join a game."""
        return join_game()
        
    @app.route('/get_active_games', methods=['GET'])
    def get_active_games_route():
        """Get a list of active games with available AI positions."""
        return get_active_games()
