#!/usr/bin/env python3
"""
HTTP route handlers for the Doppelkopf web application.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import request

from src.backend.route_handlers import (
    index, game_summary, model_info, new_game, set_variant_route,
    play_card_route, get_current_trick, get_last_trick, announce_route
)
from src.backend.card_utils import cards_equal
from config import games, scoreboard

def register_routes(app, socketio):
    """Register all HTTP route handlers."""
    
    @app.route('/')
    def index_route():
        """Render the main game page."""
        return index()
        
    @app.route('/game-summary/<game_id>')
    def game_summary_route(game_id):
        """Render the game summary page."""
        return game_summary(game_id)

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
    def get_ai_hands():
        """Get the hands of AI players for debugging purposes."""
        from src.backend.game_state import card_to_dict
        
        game_id = request.args.get('game_id')
        
        if game_id not in games:
            return {'error': 'Game not found'}, 404
        
        game = games[game_id]['game']
        
        # Get the AI hands (players 1, 2, and 3)
        ai_hands = {
            'player1': [card_to_dict(card) for card in game['hands'][1]],
            'player2': [card_to_dict(card) for card in game['hands'][2]],
            'player3': [card_to_dict(card) for card in game['hands'][3]]
        }
        
        return ai_hands

    @app.route('/get_scoreboard', methods=['GET'])
    def get_scoreboard():
        """Get the current scoreboard."""
        from flask import jsonify
        return jsonify(scoreboard)
