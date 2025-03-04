#!/usr/bin/env python3
"""
HTTP route handlers for the Doppelkopf web application.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import render_template, request, jsonify

from src.backend.game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam
from config import games, scoreboard, MODEL_PATH
from game_state import (
    get_game_state, check_for_hochzeit, card_to_dict, 
    generate_game_summary, update_scoreboard_for_game_over,
    check_team_revelation
)
from ai_logic import ai_play_turn, initialize_ai_agents, handle_trick_completion

def register_routes(app, socketio):
    """Register all HTTP route handlers."""
    
    @app.route('/')
    def index():
        """Render the main game page."""
        return render_template('index.html')

    @app.route('/model_info', methods=['GET'])
    def model_info():
        """Get information about the model being used."""
        return jsonify({
            'model_path': MODEL_PATH
        })

    @app.route('/new_game', methods=['POST'])
    def new_game():
        """Start a new game."""
        # Generate a unique game ID
        game_id = os.urandom(8).hex()
        
        # Initialize game
        game = DoppelkopfGame()
        game.reset()
        
        # Set the starting player based on the last game's starting player
        next_starting_player = (scoreboard['last_starting_player'] + 1) % 4
        game.current_player = next_starting_player
        
        # Store the new starting player
        scoreboard['last_starting_player'] = next_starting_player
        
        # Initialize AI agents
        ai_agents = initialize_ai_agents(socketio, game, game_id)
        
        # Send progress updates
        socketio.emit('progress_update', {'step': 'game_preparation', 'message': 'Preparing game state...'})
        socketio.emit('progress_update', {'step': 'game_ready', 'message': 'Game ready!'})
        
        # Initialize player variants dictionary
        player_variants = {}
        
        # Have AI players choose variants immediately
        while game.variant_selection_phase and game.current_player != 0:
            current_player = game.current_player
            game.set_variant('normal', current_player)
            player_variants[current_player] = 'normal'
        
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
        
        # If it's not the player's turn, have AI play
        if game.current_player != 0:
            ai_play_turn(socketio, game_id)
        
        # Return initial game state
        return jsonify({
            'game_id': game_id,
            'state': get_game_state(game_id),
            'has_hochzeit': check_for_hochzeit(game.hands[0])
        })

    @app.route('/set_variant', methods=['POST'])
    def set_variant():
        """Set the game variant."""
        data = request.json
        game_id = data.get('game_id')
        variant = data.get('variant')
        player_idx = data.get('player_idx', 0)
        
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game = games[game_id]['game']
        
        # Set the variant for the player
        result = game.set_variant(variant, player_idx)
        
        if not result:
            return jsonify({'error': 'Invalid variant or not in variant selection phase'}), 400
        
        # Store the player's variant selection
        if 'player_variants' not in games[game_id]:
            games[game_id]['player_variants'] = {}
        
        games[game_id]['player_variants'][player_idx] = variant
        
        # If the variant selection phase is over, have AI play if it's not the player's turn
        if not game.variant_selection_phase and game.current_player != 0:
            ai_play_turn(socketio, game_id)
        
        # If we're still in variant selection phase, have AI players make their choices
        elif game.variant_selection_phase and game.current_player != 0:
            # Have AI players choose variants until it's the human's turn again or the phase is over
            while game.variant_selection_phase and game.current_player != 0:
                current_player = game.current_player
                game.set_variant('normal', current_player)
                
                if 'player_variants' not in games[game_id]:
                    games[game_id]['player_variants'] = {}
                games[game_id]['player_variants'][current_player] = 'normal'
            
            # If the variant selection phase is now over, have AI play if it's not the player's turn
            if not game.variant_selection_phase and game.current_player != 0:
                ai_play_turn(socketio, game_id)
        
        return jsonify({
            'state': get_game_state(game_id),
            'variant_selection_phase': game.variant_selection_phase,
            'current_player': game.current_player,
            'game_variant': game.game_variant.name
        })

    @app.route('/play_card', methods=['POST'])
    def play_card():
        """Play a card."""
        data = request.json
        game_id = data.get('game_id')
        card_id = data.get('card_id')
        
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game = games[game_id]['game']
        
        # Check if it's the player's turn
        if game.current_player != 0:
            return jsonify({'error': 'Not your turn'}), 400
        
        # Find the card in the player's hand
        card_parts = card_id.split('_')
        suit_name = card_parts[0]
        rank_name = card_parts[1]
        is_second = card_parts[2] == '1'
        
        suit = Suit[suit_name]
        rank = Rank[rank_name]
        
        # Find the card in the legal actions
        legal_actions = game.get_legal_actions(0)
        selected_card = None
        
        for card in legal_actions:
            if (card.suit.name == suit_name and 
                card.rank.name == rank_name and 
                card.is_second == is_second):
                selected_card = card
                break
        
        if selected_card is None:
            return jsonify({'error': 'Invalid card or not a legal move'}), 400
        
        # Play the card
        game.play_card(0, selected_card)
        
        # Check if the player revealed their team by playing a Queen of Clubs
        check_team_revelation(game, 0, selected_card, games[game_id])
        
        # Check if a trick was completed
        trick_completed = game.trick_winner is not None
        trick_winner = game.trick_winner
        trick_points = 0
        
        # If a trick was completed, handle it before AI plays
        if trick_completed:
            # Store the trick winner before handling the trick completion
            trick_winner = game.trick_winner
            
            # Calculate points for the trick before handling the trick completion
            trick_points = sum(card.get_value() for card in game.current_trick)
            
            # Handle trick completion
            handle_trick_completion(socketio, game_id, game)
        
        # Have AI players take their turns
        ai_play_turn(socketio, game_id)
        
        # Check if game is over and update scoreboard
        if game.game_over:
            # Generate game summary
            summary_text = generate_game_summary(game_id)
            
            # Update scoreboard
            update_scoreboard_for_game_over(game_id)
        
        # Create a response object
        response_data = {
            'state': get_game_state(game_id),
            'trick_completed': trick_completed,
            'trick_winner': trick_winner,
            'is_player_winner': trick_winner == 0 if trick_winner is not None else False,
            'trick_points': trick_points if trick_completed else 0,
            'scoreboard': scoreboard
        }
        
        # If the game is over, include the player scores in the state and add a game summary
        if game.game_over:
            # Make sure the player scores are included in the state
            response_data['state']['player_scores'] = scoreboard['player_scores']
            
            # Also include the scoreboard in the state for easy access
            response_data['state']['scoreboard'] = {
                'player_wins': scoreboard['player_wins'],
                'ai_wins': scoreboard['ai_wins'],
                'player_scores': scoreboard['player_scores']
            }
            
            # Add the game summary to the response
            response_data['game_summary'] = games[game_id]['game_summary']
        
        return jsonify(response_data)

    @app.route('/get_current_trick', methods=['GET'])
    def get_current_trick():
        """Get the current trick data for debugging."""
        game_id = request.args.get('game_id')
        
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game = games[game_id]['game']
        
        # Get the current trick data
        current_trick = [card_to_dict(card) for card in game.current_trick]
        
        # Calculate the starting player for this trick
        starting_player = (game.current_player - len(game.current_trick)) % game.num_players
        
        # Add player information to each card in the trick
        trick_players = []
        for i in range(len(game.current_trick)):
            player_idx = (starting_player + i) % game.num_players
            trick_players.append({
                'name': "You" if player_idx == 0 else f"Player {player_idx}",
                'idx': player_idx,
                'is_current': player_idx == game.current_player
            })
        
        return jsonify({
            'current_trick': current_trick,
            'trick_players': trick_players,
            'current_player': game.current_player,
            'starting_player': starting_player
        })

    @app.route('/get_last_trick', methods=['GET'])
    def get_last_trick():
        """Get the last completed trick."""
        game_id = request.args.get('game_id')
        
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game_data = games[game_id]
        
        if game_data['last_trick'] is None:
            return jsonify({'error': 'No last trick available'}), 404
        
        return jsonify({
            'last_trick': game_data['last_trick'],
            'trick_players': game_data['last_trick_players'],
            'winner': game_data['last_trick_winner'],
            'trick_points': game_data['last_trick_points']
        })

    @app.route('/announce', methods=['POST'])
    def announce():
        """Announce Re, Contra, or additional announcements (No 90, No 60, No 30, Black)."""
        data = request.json
        game_id = data.get('game_id')
        announcement = data.get('announcement')  # 're', 'contra', 'no90', 'no60', 'no30', 'black'
        
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game_data = games[game_id]
        game = game_data['game']
        
        # Count cards played
        cards_played = len(game.current_trick)
        for trick in game.tricks:
            cards_played += len(trick)
        
        # Check if the player is in the appropriate team for the announcement
        player_team = game.teams[0]  # Player is always index 0
        
        # Handle Re and Contra announcements
        if announcement in ['re', 'contra']:
            # Check if more than 5 cards have been played
            if cards_played >= 5:
                return jsonify({'error': 'Cannot announce Re or Contra after the fifth card has been played'}), 400
            
            # Check if the player is in the appropriate team
            if announcement == 're' and player_team != PlayerTeam.RE:
                return jsonify({'error': 'Only RE team members can announce Re'}), 400
            elif announcement == 'contra' and player_team != PlayerTeam.KONTRA:
                return jsonify({'error': 'Only KONTRA team members can announce Contra'}), 400
            
            # Update the game data based on the announcement
            if announcement == 're':
                game_data['re_announced'] = True
                game_data['re_announcement_card'] = cards_played  # Track when Re was announced
                game_data['multiplier'] = 2  # Set multiplier to 2 for Re
            elif announcement == 'contra':
                game_data['contra_announced'] = True
                game_data['contra_announcement_card'] = cards_played  # Track when Contra was announced
                game_data['multiplier'] = 2  # Set multiplier to 2 for Contra
        
        # Handle additional announcements (No 90, No 60, No 30, Black)
        elif announcement in ['no90', 'no60', 'no30', 'black']:
            # Check if the player has announced Re or Contra
            if player_team == PlayerTeam.RE and not game_data.get('re_announced', False):
                return jsonify({'error': 'You must announce Re before making additional announcements'}), 400
            elif player_team == PlayerTeam.KONTRA and not game_data.get('contra_announced', False):
                return jsonify({'error': 'You must announce Contra before making additional announcements'}), 400
            
            # Check if the announcement was made within 5 cards after Re or Contra
            re_announced_card = game_data.get('re_announcement_card', -1)
            contra_announced_card = game_data.get('contra_announcement_card', -1)
            
            if player_team == PlayerTeam.RE and (re_announced_card < 0 or cards_played > re_announced_card + 5):
                return jsonify({'error': 'Additional announcements must be made within 5 cards after Re'}), 400
            elif player_team == PlayerTeam.KONTRA and (contra_announced_card < 0 or cards_played > contra_announced_card + 5):
                return jsonify({'error': 'Additional announcements must be made within 5 cards after Contra'}), 400
            
            # Check if the announcements are made in the correct order
            if announcement == 'no90' and not game_data.get('no90_announced', False):
                game_data['no90_announced'] = True
                game_data['multiplier'] = 3  # Set multiplier to 3 for No 90
            elif announcement == 'no60' and game_data.get('no90_announced', False) and not game_data.get('no60_announced', False):
                game_data['no60_announced'] = True
                game_data['multiplier'] = 4  # Set multiplier to 4 for No 60
            elif announcement == 'no30' and game_data.get('no60_announced', False) and not game_data.get('no30_announced', False):
                game_data['no30_announced'] = True
                game_data['multiplier'] = 5  # Set multiplier to 5 for No 30
            elif announcement == 'black' and game_data.get('no30_announced', False) and not game_data.get('black_announced', False):
                game_data['black_announced'] = True
                game_data['multiplier'] = 6  # Set multiplier to 6 for Black
            else:
                return jsonify({'error': 'Invalid announcement order'}), 400
        else:
            return jsonify({'error': 'Invalid announcement'}), 400
        
        return jsonify({
            'state': get_game_state(game_id),
            're_announced': game_data.get('re_announced', False),
            'contra_announced': game_data.get('contra_announced', False),
            'no90_announced': game_data.get('no90_announced', False),
            'no60_announced': game_data.get('no60_announced', False),
            'no30_announced': game_data.get('no30_announced', False),
            'black_announced': game_data.get('black_announced', False),
            'multiplier': game_data.get('multiplier', 1)
        })

    @app.route('/get_ai_hands', methods=['GET'])
    def get_ai_hands():
        """Get the hands of AI players for debugging purposes."""
        game_id = request.args.get('game_id')
        
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game = games[game_id]['game']
        
        # Get the AI hands (players 1, 2, and 3)
        ai_hands = {
            'player1': [card_to_dict(card) for card in game.hands[1]],
            'player2': [card_to_dict(card) for card in game.hands[2]],
            'player3': [card_to_dict(card) for card in game.hands[3]]
        }
        
        return jsonify(ai_hands)

    @app.route('/get_scoreboard', methods=['GET'])
    def get_scoreboard():
        """Get the current scoreboard."""
        return jsonify(scoreboard)
