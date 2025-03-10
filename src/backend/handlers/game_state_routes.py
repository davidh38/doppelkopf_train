#!/usr/bin/env python3
"""
Game state route handlers for the Doppelkopf web application.
These include getting trick data and game summary.
"""

from flask import render_template, jsonify

from src.backend.game.doppelkopf import (
    TEAM_NAMES, TEAM_RE, TEAM_KONTRA
)
from src.backend.config import games, scoreboard
from src.backend.game_state import card_to_dict

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

def get_ai_hands(game_id):
    """Get the hands of AI players for debugging purposes."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Get the AI hands (players 1, 2, and 3)
    ai_hands = {
        'player1': [card_to_dict(card) for card in game['hands'][1]],
        'player2': [card_to_dict(card) for card in game['hands'][2]],
        'player3': [card_to_dict(card) for card in game['hands'][3]]
    }
    
    return jsonify(ai_hands)
