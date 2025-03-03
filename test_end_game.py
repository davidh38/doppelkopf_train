#!/usr/bin/env python3
"""
Test script to create a game where the user only needs to play the last card
to see what happens after the game ends.
"""

import os
import json
import argparse
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Socket.IO event handlers
@socketio.on('join')
def on_join(data):
    """Join a game room."""
    game_id = data.get('game_id')
    if game_id:
        print(f"Client joined game room: {game_id}")
        join_room(game_id)

# Global game state
games = {}

# Global scoreboard to track wins and player scores
scoreboard = {
    'player_wins': 0,
    'ai_wins': 0,
    'player_scores': [0, 0, 0, 0],  # Individual scores for all 4 players
    'last_starting_player': 0  # Track the last player who started a game
}

def card_to_dict(card):
    """Convert a Card object to a dictionary for JSON serialization."""
    if card is None:
        return None
    
    # Emoji mappings for suits
    suit_emojis = {
        Suit.HEARTS: "♥️",
        Suit.DIAMONDS: "♦️",
        Suit.CLUBS: "♣️",
        Suit.SPADES: "♠️"
    }
    
    # Emoji mappings for ranks
    rank_emojis = {
        Rank.ACE: "🅰️",
        Rank.KING: "👑",
        Rank.QUEEN: "👸",
        Rank.JACK: "🤴",
        Rank.TEN: "🔟",
        Rank.NINE: "9️⃣"
    }
    
    return {
        'suit': card.suit.name,
        'rank': card.rank.name,
        'is_second': card.is_second,
        'suit_emoji': suit_emojis[card.suit],
        'rank_emoji': rank_emojis[card.rank],
        'display': f"{rank_emojis[card.rank]}{suit_emojis[card.suit]} {card.rank.name.capitalize()} of {card.suit.name.capitalize()}" + (" (2)" if card.is_second else ""),
        'id': f"{card.suit.name}_{card.rank.name}_{1 if card.is_second else 0}"
    }

def get_game_state(game_id, player_id=0):
    """Get the current game state for the specified player."""
    if game_id not in games:
        return None
    
    game = games[game_id]['game']
    game_data = games[game_id]
    
    # Convert game state to JSON-serializable format
    state = {
        'current_player': game.current_player,
        'is_player_turn': game.current_player == player_id,
        'player_team': game.teams[player_id].name,
        'game_variant': game.game_variant.name,
        'scores': game.scores,
        'player_scores': game.player_scores,
        'game_over': game.game_over,
        'winner': game.winner.name if game.game_over else None,
        'hand': [card_to_dict(card) for card in game.hands[player_id]],
        'legal_actions': [card_to_dict(card) for card in game.get_legal_actions(player_id)],
        'other_players': [
            {
                'id': i,
                'team': game.teams[i].name,
                'card_count': len(game.hands[i]),
                'is_current': game.current_player == i,
                'score': game.player_scores[i],
                'revealed_team': game_data['revealed_teams'][i]
            } for i in range(1, game.num_players)
        ],
        'revealed_teams': game_data['revealed_teams'],
        'player_score': game.player_scores[player_id],
        'last_trick_points': getattr(game, 'last_trick_points', 0),
        'last_trick_diamond_ace_bonus': getattr(game, 'last_trick_diamond_ace_bonus', 0),
        're_announced': game_data.get('re_announced', False),
        'contra_announced': game_data.get('contra_announced', False),
        'multiplier': game_data.get('multiplier', 1),
        'can_announce': False,  # Disable announcements for this test
        'can_announce_re': False,
        'can_announce_contra': False,
        'teams': [team.name for team in game.teams]  # Add teams for score calculation
    }
    
    # Add current trick with player information
    if game.current_trick:
        # Just send the cards directly
        state['current_trick'] = [card_to_dict(card) for card in game.current_trick]
        
        # Also send player information separately
        starting_player = (game.current_player - len(game.current_trick)) % game.num_players
        trick_players = []
        for i in range(len(game.current_trick)):
            player_idx = (starting_player + i) % game.num_players
            trick_players.append({
                'name': "You" if player_idx == 0 else f"Player {player_idx}",
                'idx': player_idx,
                'is_current': player_idx == game.current_player
            })
        state['trick_players'] = trick_players
    else:
        state['current_trick'] = []
        state['trick_players'] = []
    
    return state

def setup_almost_finished_game():
    """Set up a game that is almost finished, with only one card left for the player to play."""
    game = DoppelkopfGame()
    game.reset()
    
    # Set up teams - make player (0) and player 2 on RE team, players 1 and 3 on KONTRA team
    game.teams = [PlayerTeam.RE, PlayerTeam.KONTRA, PlayerTeam.RE, PlayerTeam.KONTRA]
    
    # Clear all hands
    for i in range(4):
        game.hands[i] = []
    
    # Give player one card to play (a high trump to ensure they win)
    player_card = Card(Suit.CLUBS, Rank.QUEEN, False)  # Queen of Clubs (highest trump)
    game.hands[0] = [player_card]
    
    # Set up the current trick with cards from other players
    game.current_trick = [
        Card(Suit.HEARTS, Rank.NINE, False),  # Player 1 (KONTRA)
        Card(Suit.HEARTS, Rank.TEN, False),   # Player 2 (RE)
        Card(Suit.HEARTS, Rank.KING, False)   # Player 3 (KONTRA)
    ]
    
    # Set the current player to the human player (0)
    game.current_player = 0
    
    # Set up the game state to be almost finished
    # We'll say 9 tricks have been played (36 cards), and this is the last trick (4 cards)
    
    # Set up the tricks list with 9 completed tricks
    game.tricks = []
    for _ in range(9):
        trick = [
            Card(Suit.SPADES, Rank.NINE, False),
            Card(Suit.SPADES, Rank.TEN, False),
            Card(Suit.SPADES, Rank.KING, False),
            Card(Suit.SPADES, Rank.ACE, False)
        ]
        game.tricks.append(trick)
    
    # Set up scores to make it interesting - RE team is winning but not by much
    game.scores = [120, 120]  # 120 points each, so the last trick will determine the winner
    
    # Set up player scores
    game.player_scores = [0, 0, 0, 0]
    
    # Set up the game variant
    game.game_variant = GameVariant.NORMAL
    
    # Set up the game ID
    game_id = "test_end_game"
    
    # Store the game
    games[game_id] = {
        'game': game,
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
        'multiplier': 1,
        'starting_player': 0,
        'player_variants': {0: 'normal', 1: 'normal', 2: 'normal', 3: 'normal'},
        'revealed_teams': [True, True, True, True]  # All teams are revealed for this test
    }
    
    return game_id

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')

@app.route('/model_info', methods=['GET'])
def model_info():
    """Get information about the model being used."""
    return jsonify({
        'model_path': 'test_end_game'
    })

@app.route('/new_game', methods=['POST'])
def new_game():
    """Start a new test game that is almost finished."""
    # Set up the almost finished game
    game_id = setup_almost_finished_game()
    
    # Return initial game state
    return jsonify({
        'game_id': game_id,
        'state': get_game_state(game_id),
        'has_hochzeit': False
    })

@app.route('/set_variant', methods=['POST'])
def set_variant():
    """Set the game variant (not used in this test)."""
    data = request.json
    game_id = data.get('game_id')
    variant = data.get('variant')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    # Just return the current state
    return jsonify({
        'state': get_game_state(game_id),
        'variant_selection_phase': False,
        'current_player': games[game_id]['game'].current_player,
        'game_variant': games[game_id]['game'].game_variant.name
    })

@app.route('/play_card', methods=['POST'])
def play_card():
    """Play a card and end the game."""
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
    
    # The trick is now complete, so determine the winner
    trick_winner = game.determine_trick_winner(game.current_trick, 0)
    trick_points = sum(card.get_value() for card in game.current_trick)
    
    # Update the scores
    if trick_winner == 0 or trick_winner == 2:  # RE team
        game.scores[0] += trick_points
    else:  # KONTRA team
        game.scores[1] += trick_points
    
    # Store the last trick
    games[game_id]['last_trick'] = [card_to_dict(card) for card in game.current_trick]
    games[game_id]['last_trick_winner'] = trick_winner
    games[game_id]['last_trick_points'] = trick_points
    
    # Clear the current trick
    game.current_trick = []
    
    # Set the current player to the trick winner
    game.current_player = trick_winner
    
    # End the game
    game.game_over = True
    
    # Determine the winner
    if game.scores[0] > game.scores[1]:
        game.winner = PlayerTeam.RE
    else:
        game.winner = PlayerTeam.KONTRA
    
    # Update player scores
    re_players = sum(1 for team in game.teams if team == PlayerTeam.RE)
    kontra_players = sum(1 for team in game.teams if team == PlayerTeam.KONTRA)
    
    if game.winner == PlayerTeam.RE:
        # RE team won
        re_points = kontra_players  # Each RE player gets +kontra_players
        kontra_points = -re_players  # Each KONTRA player gets -re_players
        
        for i in range(len(game.teams)):
            if game.teams[i] == PlayerTeam.RE:
                game.player_scores[i] += re_points
            else:  # KONTRA team
                game.player_scores[i] += kontra_points
    else:
        # KONTRA team won
        re_points = -kontra_players  # Each RE player gets -kontra_players
        kontra_points = re_players  # Each KONTRA player gets +re_players
        
        for i in range(len(game.teams)):
            if game.teams[i] == PlayerTeam.RE:
                game.player_scores[i] += re_points
            else:  # KONTRA team
                game.player_scores[i] += kontra_points
    
    # Update the scoreboard
    for i in range(4):
        scoreboard['player_scores'][i] = game.player_scores[i]
    
    # Return the updated game state
    return jsonify({
        'state': get_game_state(game_id),
        'trick_completed': True,
        'trick_winner': trick_winner,
        'is_player_winner': trick_winner == 0,
        'trick_points': trick_points,
        'scoreboard': scoreboard
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
        'winner': game_data['last_trick_winner'],
        'trick_points': game_data['last_trick_points']
    })

@app.route('/get_ai_hands', methods=['GET'])
def get_ai_hands():
    """Get the hands of AI players (empty in this test)."""
    game_id = request.args.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    # Return empty hands for AI players
    return jsonify({
        'player1': [],
        'player2': [],
        'player3': []
    })

@app.route('/announce', methods=['POST'])
def announce():
    """Make an announcement (not used in this test)."""
    return jsonify({
        'error': 'Announcements are disabled in this test'
    }), 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run test end game')
    parser.add_argument('--port', type=int, default=5011, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"Starting test end game server on port {args.port}")
    print("This will create a game where you only need to play the last card to see what happens after the game ends.")
    print("Open http://localhost:{}/".format(args.port))
    
    socketio.run(app, debug=True, port=args.port)
