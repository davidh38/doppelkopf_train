#!/usr/bin/env python3
"""
Route handler functions for the Doppelkopf web application.
These functions contain the business logic for the HTTP routes.
"""

import os
from flask import render_template, jsonify

from src.backend.game.doppelkopf import (
    SUIT_CLUBS, SUIT_SPADES, SUIT_HEARTS, SUIT_DIAMONDS,
    RANK_NINE, RANK_JACK, RANK_QUEEN, RANK_KING, RANK_TEN, RANK_ACE,
    TEAM_RE, TEAM_KONTRA, TEAM_UNKNOWN,
    VARIANT_NORMAL, VARIANT_HOCHZEIT, VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_FLESHLESS, VARIANT_KING_SOLO,
    SUIT_NAMES, RANK_NAMES, TEAM_NAMES, VARIANT_NAMES,
    create_card, create_game_state, get_legal_actions, play_card, announce, set_variant, has_hochzeit,
    get_card_value
)
from src.backend.card_utils import cards_equal
from config import games, scoreboard, MODEL_PATH
from game_state import (
    get_game_state, check_for_hochzeit, card_to_dict, 
    generate_game_summary, update_scoreboard_for_game_over,
    check_team_revelation
)
from ai_logic import ai_play_turn, initialize_ai_agents, handle_trick_completion

def index():
    """Render the main game page."""
    return render_template('index.html')

def game_summary(game_id):
    """Render the game summary page."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
        
    game_data = games[game_id]
    game = game_data['game']
    
    # Determine the winner team and color
    winner_team = TEAM_NAMES[game['winner']] if 'winner' in game else "Unknown"
    winner_color = "#2ecc71" if winner_team == "RE" else "#e74c3c"
    
    # Get the game summary
    game_summary = game_data.get('game_summary', '')
    
    # Get the scores
    re_score = game['scores'][0] if 'scores' in game else 0
    kontra_score = game['scores'][1] if 'scores' in game else 0
    
    # Get the announcements
    re_announced = game_data.get('re_announced', False)
    contra_announced = game_data.get('contra_announced', False)
    no90_announced = game_data.get('no90_announced', False)
    no60_announced = game_data.get('no60_announced', False)
    no30_announced = game_data.get('no30_announced', False)
    black_announced = game_data.get('black_announced', False)
    
    # Get the multiplier
    multiplier = game_data.get('multiplier', 1)
    
    # Get the player scores
    player_scores = scoreboard['player_scores']
    
    # Calculate player scores based on special achievements
    player_achievement_scores = []
    
    # Calculate total achievement points for each team
    re_achievement_points = 0
    kontra_achievement_points = 0
    
    # Base points for winning
    if winner_team == "RE":
        re_achievement_points += 1  # RE team wins
    else:
        kontra_achievement_points += 1  # KONTRA team wins
    
    # Check for no 90 achievement
    if winner_team == "RE" and kontra_score < 90:
        re_achievement_points += 1  # RE plays no 90
    elif winner_team == "KONTRA" and re_score < 90:
        kontra_achievement_points += 1  # KONTRA plays no 90
    
    # Check for no 60 achievement
    if winner_team == "RE" and kontra_score < 60:
        re_achievement_points += 1  # RE plays no 60
    elif winner_team == "KONTRA" and re_score < 60:
        kontra_achievement_points += 1  # KONTRA plays no 60
    
    # Check for no 30 achievement
    if winner_team == "RE" and kontra_score < 30:
        re_achievement_points += 1  # RE plays no 30
    elif winner_team == "KONTRA" and re_score < 30:
        kontra_achievement_points += 1  # KONTRA plays no 30
    
    # Check for black achievement
    if winner_team == "RE" and kontra_score == 0:
        re_achievement_points += 1  # RE plays black
    elif winner_team == "KONTRA" and re_score == 0:
        kontra_achievement_points += 1  # KONTRA plays black
    
    # Add Diamond Ace captures if available
    diamond_ace_re_points = 0
    diamond_ace_kontra_points = 0
    if 'diamond_ace_captured' in game:
        diamond_ace_captures = [capture for capture in game['diamond_ace_captured'] if capture.get('type') == 'diamond_ace' or not capture.get('type')]
        for capture in diamond_ace_captures:
            if capture['winner_team'] == 'RE':
                diamond_ace_re_points += 1
            else:
                diamond_ace_kontra_points += 1
    
    # Add 40+ point tricks if available
    forty_plus_re_points = 0
    forty_plus_kontra_points = 0
    if 'diamond_ace_captured' in game:
        forty_plus_tricks = [capture for capture in game['diamond_ace_captured'] if capture.get('type') == 'forty_plus']
        for trick in forty_plus_tricks:
            if trick['winner_team'] == 'RE':
                forty_plus_re_points += 1
            else:
                forty_plus_kontra_points += 1
    
    # Add all special points
    re_achievement_points += diamond_ace_re_points + forty_plus_re_points
    kontra_achievement_points += diamond_ace_kontra_points + forty_plus_kontra_points
    
    # Apply multiplier
    re_achievement_points_with_multiplier = re_achievement_points * multiplier
    kontra_achievement_points_with_multiplier = kontra_achievement_points * multiplier
    
    # Calculate player achievement scores
    for i, team in enumerate(game['teams']):
        player_name = "You" if i == 0 else f"Player {i}"
        if team == TEAM_RE:
            points = re_achievement_points_with_multiplier - kontra_achievement_points_with_multiplier
            details = {
                'name': player_name,
                'team': 'RE',
                'points': points,
                're_points': re_achievement_points_with_multiplier,
                'kontra_points': -kontra_achievement_points_with_multiplier,
                'total': player_scores[i]
            }
        else:  # KONTRA team
            points = kontra_achievement_points_with_multiplier - re_achievement_points_with_multiplier
            details = {
                'name': player_name,
                'team': 'KONTRA',
                'points': points,
                're_points': -re_achievement_points_with_multiplier,
                'kontra_points': kontra_achievement_points_with_multiplier,
                'total': player_scores[i]
            }
        player_achievement_scores.append(details)
    
    # Create a detailed score calculation details HTML that includes special achievements
    score_calculation_details = f"""
    <table>
        <tr>
            <th>Team</th>
            <th>Points</th>
            <th>Result</th>
        </tr>
        <tr class="team-re">
            <td>RE</td>
            <td>{re_score}</td>
            <td>{"Win" if winner_team == "RE" else "Loss"}</td>
        </tr>
        <tr class="team-kontra">
            <td>KONTRA</td>
            <td>{kontra_score}</td>
            <td>{"Win" if winner_team == "KONTRA" else "Loss"}</td>
        </tr>
    </table>
    
    <h4>Special Achievements</h4>
    <table>
        <tr>
            <th>Achievement</th>
            <th>Points</th>
        </tr>
    """
    
    # Add special achievements based on the game results
    if winner_team == "RE":
        score_calculation_details += f"""
        <tr style="font-weight: bold; background-color: rgba(46, 204, 113, 0.2);">
            <td>🏆 RE Wins (Special Achievement)</td>
            <td>+1</td>
        </tr>
        """
        # Check for no 90 achievement
        if kontra_score < 90:
            score_calculation_details += f"""
            <tr>
                <td>No 90 (KONTRA got {kontra_score} points)</td>
                <td>+1</td>
            </tr>
            """
        # Check for no 60 achievement
        if kontra_score < 60:
            score_calculation_details += f"""
            <tr>
                <td>No 60 (KONTRA got {kontra_score} points)</td>
                <td>+1</td>
            </tr>
            """
        # Check for no 30 achievement
        if kontra_score < 30:
            score_calculation_details += f"""
            <tr>
                <td>No 30 (KONTRA got {kontra_score} points)</td>
                <td>+1</td>
            </tr>
            """
        # Check for black achievement
        if kontra_score == 0:
            score_calculation_details += f"""
            <tr>
                <td>Black (KONTRA got 0 points)</td>
                <td>+1</td>
            </tr>
            """
    else:  # KONTRA wins
        score_calculation_details += f"""
        <tr style="font-weight: bold; background-color: rgba(231, 76, 60, 0.2);">
            <td>🏆 KONTRA Wins (Special Achievement)</td>
            <td>+1</td>
        </tr>
        """
        # Check for no 90 achievement
        if re_score < 90:
            score_calculation_details += f"""
            <tr>
                <td>No 90 (RE got {re_score} points)</td>
                <td>+1</td>
            </tr>
            """
        # Check for no 60 achievement
        if re_score < 60:
            score_calculation_details += f"""
            <tr>
                <td>No 60 (RE got {re_score} points)</td>
                <td>+1</td>
            </tr>
            """
        # Check for no 30 achievement
        if re_score < 30:
            score_calculation_details += f"""
            <tr>
                <td>No 30 (RE got {re_score} points)</td>
                <td>+1</td>
            </tr>
            """
        # Check for black achievement
        if re_score == 0:
            score_calculation_details += f"""
            <tr>
                <td>Black (RE got 0 points)</td>
                <td>+1</td>
            </tr>
            """
    
    # Add Diamond Ace captures if available
    if 'diamond_ace_captured' in game:
        diamond_ace_captures = [capture for capture in game['diamond_ace_captured'] if capture.get('type') == 'diamond_ace' or not capture.get('type')]
        if diamond_ace_captures:
            for capture in diamond_ace_captures:
                winner_team = capture['winner_team']
                score_calculation_details += f"""
                <tr>
                    <td>Diamond Ace Capture ({winner_team})</td>
                    <td>+1</td>
                </tr>
                """
    
    # Add 40+ point tricks if available
    if 'diamond_ace_captured' in game:
        forty_plus_tricks = [capture for capture in game['diamond_ace_captured'] if capture.get('type') == 'forty_plus']
        if forty_plus_tricks:
            for trick in forty_plus_tricks:
                winner_team = trick['winner_team']
                points = trick['points']
                score_calculation_details += f"""
                <tr>
                    <td>40+ Point Trick ({winner_team}, {points} points)</td>
                    <td>+1</td>
                </tr>
                """
    
    # Close the table and add multiplier
    score_calculation_details += f"""
    </table>
    <div class="total">
        Multiplier: {multiplier}x
    </div>
    """
    
    return render_template('game-summary.html',
                          winner_team=winner_team,
                          winner_color=winner_color,
                          game_summary=game_summary,
                          re_score=re_score,
                          kontra_score=kontra_score,
                          re_announced=re_announced,
                          contra_announced=contra_announced,
                          no90_announced=no90_announced,
                          no60_announced=no60_announced,
                          no30_announced=no30_announced,
                          black_announced=black_announced,
                          multiplier=multiplier,
                          player_scores=player_scores,
                          player_achievement_scores=player_achievement_scores,
                          score_calculation_details=score_calculation_details)

def model_info():
    """Get information about the model being used."""
    return jsonify({
        'model_path': MODEL_PATH
    })

def new_game(socketio):
    """Start a new game."""
    # Generate a unique game ID
    game_id = os.urandom(8).hex()
    
    # Initialize game
    game = create_game_state()
    
    # Set the starting player based on the last game's starting player
    next_starting_player = (scoreboard['last_starting_player'] + 1) % 4
    game['current_player'] = next_starting_player
    
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
    while game['variant_selection_phase'] and game['current_player'] != 0:
        current_player = game['current_player']
        set_variant(game, 'normal', current_player)
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
    if game['current_player'] != 0:
        ai_play_turn(socketio, game_id)
    else:
        # Set legal actions for the player if it's their turn
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player in new game: {game['legal_actions']}")
    
    # Return initial game state
    return jsonify({
        'game_id': game_id,
        'state': get_game_state(game_id)
    })

def set_variant_route(socketio, data):
    """Set the game variant."""
    game_id = data.get('game_id')
    variant = data.get('variant')
    player_idx = data.get('player_idx', 0)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Set the variant for the player
    result = set_variant(game, variant, player_idx)
    
    if not result:
        return jsonify({'error': 'Invalid variant or not in variant selection phase'}), 400
    
    # Store the player's variant selection
    if 'player_variants' not in games[game_id]:
        games[game_id]['player_variants'] = {}
    
    games[game_id]['player_variants'][player_idx] = variant
    
    # If the variant selection phase is over, have AI play if it's not the player's turn
    if not game['variant_selection_phase'] and game['current_player'] != 0:
        ai_play_turn(socketio, game_id)
    
    # If we're still in variant selection phase, have AI players make their choices
    elif game['variant_selection_phase'] and game['current_player'] != 0:
        # Have AI players choose variants until it's the human's turn again or the phase is over
        while game['variant_selection_phase'] and game['current_player'] != 0:
            current_player = game['current_player']
            set_variant(game, 'normal', current_player)
            
            if 'player_variants' not in games[game_id]:
                games[game_id]['player_variants'] = {}
            games[game_id]['player_variants'][current_player] = 'normal'
        
        # If the variant selection phase is now over, have AI play if it's not the player's turn
        if not game['variant_selection_phase'] and game['current_player'] != 0:
            ai_play_turn(socketio, game_id)
    
    # Set legal actions for the player if it's their turn
    if not game['variant_selection_phase'] and game['current_player'] == 0:
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player: {game['legal_actions']}")
    
    return jsonify({
        'state': get_game_state(game_id),
        'variant_selection_phase': game['variant_selection_phase'],
        'current_player': game['current_player'],
        'game_variant': VARIANT_NAMES[game['game_variant']]
    })

def play_card_route(socketio, data):
    """Play a card."""
    game_id = data.get('game_id')
    card_id = data.get('card_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Check if it's the player's turn
    if game['current_player'] != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Find the card in the player's hand
    card_parts = card_id.split('_')
    suit_name = card_parts[0]
    rank_name = card_parts[1]
    is_second = card_parts[2] == '1'
    
    # Convert suit and rank names to constants
    suit_map = {name: const for const, name in SUIT_NAMES.items()}
    rank_map = {name: const for const, name in RANK_NAMES.items()}
    
    suit = suit_map[suit_name]
    rank = rank_map[rank_name]
    
    # Create the card
    selected_card = create_card(suit, rank, is_second)
    
    # Find the card in the legal actions
    legal_actions = get_legal_actions(game, 0)
    if not any(cards_equal(selected_card, legal_card) for legal_card in legal_actions):
        return jsonify({'error': 'Invalid card or not a legal move'}), 400
    
    # Play the card
    play_card(game, 0, selected_card)
    
    # Check if the player revealed their team by playing a Queen of Clubs
    check_team_revelation(game, 0, selected_card, games[game_id])
    
    # Check if a trick was completed
    trick_completed = game.get('trick_winner') is not None
    trick_winner = game.get('trick_winner')
    trick_points = 0
    
    # If a trick was completed, handle it before AI plays
    if trick_completed:
        # Store the trick winner before handling the trick completion
        trick_winner = game['trick_winner']
        
        # Calculate points for the trick before handling the trick completion
        trick_points = sum(get_card_value(card) for card in game['current_trick'])
        
        # Handle trick completion
        handle_trick_completion(socketio, game_id, game)
    
    # Have AI players take their turns
    ai_play_turn(socketio, game_id)
    
    # Set legal actions for the player if it's their turn
    if game['current_player'] == 0:
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player after AI turns: {game['legal_actions']}")
    
    # Check if game is over and update scoreboard
    if game['game_over']:
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
    if game['game_over']:
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

def get_current_trick(game_id):
    """Get the current trick data for debugging."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Get the current trick data
    current_trick = [card_to_dict(card) for card in game['current_trick']]
    
    # Calculate the starting player for this trick
    starting_player = (game['current_player'] - len(game['current_trick'])) % game['num_players']
    
    # Add player information to each card in the trick
    trick_players = []
    for i in range(len(game['current_trick'])):
        player_idx = (starting_player + i) % game['num_players']
        trick_players.append({
            'name': "You" if player_idx == 0 else f"Player {player_idx}",
            'idx': player_idx,
            'is_current': player_idx == game['current_player']
        })
    
    return jsonify({
        'current_trick': current_trick,
        'trick_players': trick_players,
        'current_player': game['current_player'],
        'starting_player': starting_player
    })

def get_last_trick(game_id):
    """Get the last completed trick."""
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

def announce_route(socketio, data):
    """Announce Re, Contra, or additional announcements (No 90, No 60, No 30, Black)."""
    game_id = data.get('game_id')
    announcement = data.get('announcement')  # 're', 'contra', 'no90', 'no60', 'no30', 'black'
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Count cards played
    cards_played = len(game['current_trick'])
    for trick in game['tricks']:
        cards_played += len(trick)
    
    # Check if the player is in the appropriate team for the announcement
    player_team = game['teams'][0]  # Player is always index 0
    
    # Handle Hochzeit announcement
    if announcement == 'hochzeit':
        # Check if more than 5 cards have been played
        if cards_played >= 5:
            return jsonify({'error': 'Cannot announce Hochzeit after the fifth card has been played'}), 400
        
        # Check if the player has both Queens of Clubs
        if not has_hochzeit(game, 0):
            return jsonify({'error': 'You need both Queens of Clubs to announce Hochzeit'}), 400
        
        # Set the game variant to Hochzeit
        result = announce(game, 0, 'hochzeit')
        if not result:
            return jsonify({'error': 'Failed to announce Hochzeit'}), 400
        
        # Set legal actions for the player if it's their turn
        if game['current_player'] == 0:
            game['legal_actions'] = get_legal_actions(game, 0)
            print(f"Setting legal actions for player after hochzeit announcement: {game['legal_actions']}")
        
        return jsonify({
            'state': get_game_state(game_id),
            'game_variant': VARIANT_NAMES[game['game_variant']]
        })
    
    # Handle Re and Contra announcements
    elif announcement in ['re', 'contra']:
        # Check if more than 5 cards have been played
        if cards_played >= 5:
            return jsonify({'error': 'Cannot announce Re or Contra after the fifth card has been played'}), 400
        
        # Check if the player is in the appropriate team
        if announcement == 're' and player_team != TEAM_RE:
            return jsonify({'error': 'Only RE team members can announce Re'}), 400
        elif announcement == 'contra' and player_team != TEAM_KONTRA:
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
        if player_team == TEAM_RE and not game_data.get('re_announced', False):
            return jsonify({'error': 'You must announce Re before making additional announcements'}), 400
        elif player_team == TEAM_KONTRA and not game_data.get('contra_announced', False):
            return jsonify({'error': 'You must announce Contra before making additional announcements'}), 400
        
        # Check if the announcement was made within 5 cards after Re or Contra
        re_announced_card = game_data.get('re_announcement_card', -1)
        contra_announced_card = game_data.get('contra_announcement_card', -1)
        
        if player_team == TEAM_RE and (re_announced_card < 0 or cards_played > re_announced_card + 5):
            return jsonify({'error': 'Additional announcements must be made within 5 cards after Re'}), 400
        elif player_team == TEAM_KONTRA and (contra_announced_card < 0 or cards_played > contra_announced_card + 5):
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
    
    # Set legal actions for the player if it's their turn
    if game['current_player'] == 0:
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player after announcement: {game['legal_actions']}")
    
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
