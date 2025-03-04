#!/usr/bin/env python3
"""
Game state management functions for the Doppelkopf web application.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.backend.game.doppelkopf import Card, Suit, Rank, PlayerTeam
from config import games, scoreboard

def print_scoreboard(label, game=None):
    """Print the current scoreboard with a label."""
    print(f"\n=== SCOREBOARD ({label}) ===")
    print(f"Player Wins: {scoreboard['player_wins']}")
    print(f"AI Wins: {scoreboard['ai_wins']}")
    print(f"Player Scores: {scoreboard['player_scores']}")
    if game:
        print(f"Game Scores: {game.scores}")
        print(f"Player Game Scores: {game.player_scores}")
    print("=" * (len(label) + 25) + "\n")

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
        # Can announce until the fifth card is played
        'can_announce': (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5,
        'can_announce_re': game.teams[player_id] == PlayerTeam.RE and (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5,
        'can_announce_contra': game.teams[player_id] == PlayerTeam.KONTRA and (len(game.current_trick) + sum(len(trick) for trick in game.tricks)) < 5
    }
    
    # If the game is over, include the game summary
    if game.game_over and 'game_summary' in game_data:
        state['game_summary'] = game_data['game_summary']
    
    # Add Diamond Ace capture information if available
    if hasattr(game, 'diamond_ace_captured'):
        state['diamond_ace_captured'] = game.diamond_ace_captured
    
    # Add player variant selections if available
    if 'player_variants' in game_data:
        state['player_variants'] = game_data['player_variants']
    
    # Add announcements if available
    if 're_announced' in game_data or 'contra_announced' in game_data:
        state['announcements'] = {
            're': game_data.get('re_announced', False),
            'contra': game_data.get('contra_announced', False),
            'no90': game_data.get('no90_announced', False),
            'no60': game_data.get('no60_announced', False),
            'no30': game_data.get('no30_announced', False),
            'black': game_data.get('black_announced', False)
        }
    
    # Calculate if additional announcements are allowed
    cards_played = len(game.current_trick) + sum(len(trick) for trick in game.tricks)
    
    # Check if player can announce additional announcements (No 90, No 60, No 30, Black)
    # These can only be announced within 5 cards after Re or Contra
    re_announced_card = game_data.get('re_announcement_card', -1)
    contra_announced_card = game_data.get('contra_announcement_card', -1)
    
    # Player can announce additional announcements if:
    # 1. They are on team RE and have announced Re, or they are on team KONTRA and have announced Contra
    # 2. The announcement was made within the last 5 cards
    can_announce_additional_re = (game.teams[player_id] == PlayerTeam.RE and 
                                 game_data.get('re_announced', False) and 
                                 re_announced_card >= 0 and 
                                 cards_played <= re_announced_card + 5)
    
    can_announce_additional_contra = (game.teams[player_id] == PlayerTeam.KONTRA and 
                                     game_data.get('contra_announced', False) and 
                                     contra_announced_card >= 0 and 
                                     cards_played <= contra_announced_card + 5)
    
    # Add flags for additional announcements
    state['can_announce_no90'] = (can_announce_additional_re or can_announce_additional_contra) and not game_data.get('no90_announced', False)
    state['can_announce_no60'] = (can_announce_additional_re or can_announce_additional_contra) and game_data.get('no90_announced', False) and not game_data.get('no60_announced', False)
    state['can_announce_no30'] = (can_announce_additional_re or can_announce_additional_contra) and game_data.get('no60_announced', False) and not game_data.get('no30_announced', False)
    state['can_announce_black'] = (can_announce_additional_re or can_announce_additional_contra) and game_data.get('no30_announced', False) and not game_data.get('black_announced', False)
    
    # Add current trick with player information - VERY simplified approach
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
        
        # Debug output to help diagnose issues
        print(f"Current trick: {game.current_trick}")
        print(f"Current player: {game.current_player}")
        print(f"Calculated starting player: {starting_player}")
        print(f"Trick players: {trick_players}")
    else:
        state['current_trick'] = []
        state['trick_players'] = []
    
    # Add completed tricks if available
    if hasattr(game, 'tricks') and game.tricks:
        state['last_trick'] = [card_to_dict(card) for card in game.tricks[-1]] if game.tricks else []
        state['trick_winner'] = game.trick_winner
    
    return state

def check_for_hochzeit(hand):
    """Check if the player has both Queens of Clubs."""
    queens_of_clubs = [Card(Suit.CLUBS, Rank.QUEEN, False), Card(Suit.CLUBS, Rank.QUEEN, True)]
    return all(queen in hand for queen in queens_of_clubs)

def check_team_revelation(game, player, card, game_data):
    """Check if a player revealed their team by playing a Queen of Clubs."""
    if card.suit == Suit.CLUBS and card.rank == Rank.QUEEN:
        print(f"Player {player} revealed team by playing Queen of Clubs")
        game_data['revealed_teams'][player] = True

def generate_game_summary(game_id):
    """Generate a detailed game summary."""
    game_data = games[game_id]
    game = game_data['game']
    multiplier = game_data.get('multiplier', 1)
    
    # Count players in each team
    re_players = sum(1 for team in game.teams if team.name == 'RE')
    kontra_players = sum(1 for team in game.teams if team.name == 'KONTRA')
    
    # Calculate points for each team
    if game.winner.name == 'RE':
        # RE team won
        re_points = kontra_players  # Each RE player gets +kontra_players
        kontra_points = -re_players  # Each KONTRA player gets -re_players
    else:
        # KONTRA team won
        re_points = -kontra_players  # Each RE player gets -kontra_players
        kontra_points = re_players  # Each KONTRA player gets +re_players
    
    # Apply multiplier
    re_points_with_multiplier = re_points * multiplier
    kontra_points_with_multiplier = kontra_points * multiplier
    
    # Create summary text
    summary_text = f"Game Over! {game.winner.name} team wins!\n\n"
    
    # Add team composition
    summary_text += "Team Composition:\n"
    for i, team in enumerate(game.teams):
        player_name = "You" if i == 0 else f"Player {i}"
        summary_text += f"- {player_name}: {team.name}\n"
    
    # Add trick points information
    summary_text += "\nTrick Points:\n"
    summary_text += f"- RE team: {game.scores[0]} points\n"
    summary_text += f"- KONTRA team: {game.scores[1]} points\n"
    summary_text += f"- Total: {game.scores[0] + game.scores[1]} points\n"
    
    # Check if there were any special bonuses
    if hasattr(game, 'diamond_ace_captured'):
        diamond_ace_captures = [capture for capture in game.diamond_ace_captured if capture.get('type') == 'diamond_ace' or not capture.get('type')]
        forty_plus_captures = [capture for capture in game.diamond_ace_captured if capture.get('type') == 'forty_plus']
        
        if diamond_ace_captures:
            summary_text += "\nDiamond Ace Captures:\n"
            for capture in diamond_ace_captures:
                winner_name = "You" if capture['winner'] == 0 else f"Player {capture['winner']}"
                loser_name = "You" if capture['loser'] == 0 else f"Player {capture['loser']}"
                summary_text += f"- {winner_name} ({capture['winner_team']}) captured a Diamond Ace from {loser_name} ({capture['loser_team']})\n"
            summary_text += f"  This adds/subtracts 1 point per capture to the trick points\n"
        
        if forty_plus_captures:
            summary_text += "\n40+ Point Tricks:\n"
            for capture in forty_plus_captures:
                winner_name = "You" if capture['winner'] == 0 else f"Player {capture['winner']}"
                summary_text += f"- {winner_name} ({capture['winner_team']}) won a trick worth {capture['points']} points\n"
            summary_text += f"  This adds/subtracts 1 point per 40+ trick to the trick points\n"
    
    # Check for special achievements (no 90, no 60, no 30, black)
    re_score = game.scores[0]
    kontra_score = game.scores[1]
    
    # Add special achievements section
    summary_text += "\nSpecial Achievements:\n"
    
    # Base points for winning
    if game.winner.name == 'RE':
        summary_text += f"- RE wins: +1\n"
    else:
        summary_text += f"- KONTRA wins: +1\n"
    
    # Check for no 90 achievement (opponent got less than 90 points)
    if game.winner.name == 'RE' and kontra_score < 90:
        summary_text += f"- RE plays no 90: +1 (KONTRA got {kontra_score} points)\n"
    elif game.winner.name == 'KONTRA' and re_score < 90:
        summary_text += f"- KONTRA plays no 90: +1 (RE got {re_score} points)\n"
    
    # Check for no 60 achievement (opponent got less than 60 points)
    if game.winner.name == 'RE' and kontra_score < 60:
        summary_text += f"- RE plays no 60: +1 (KONTRA got {kontra_score} points)\n"
    elif game.winner.name == 'KONTRA' and re_score < 60:
        summary_text += f"- KONTRA plays no 60: +1 (RE got {re_score} points)\n"
    
    # Check for no 30 achievement (opponent got less than 30 points)
    if game.winner.name == 'RE' and kontra_score < 30:
        summary_text += f"- RE plays no 30: +1 (KONTRA got {kontra_score} points)\n"
    elif game.winner.name == 'KONTRA' and re_score < 30:
        summary_text += f"- KONTRA plays no 30: +1 (RE got {re_score} points)\n"
    
    # Check for black achievement (opponent got 0 points)
    if game.winner.name == 'RE' and kontra_score == 0:
        summary_text += f"- RE plays black: +1 (KONTRA got 0 points)\n"
    elif game.winner.name == 'KONTRA' and re_score == 0:
        summary_text += f"- KONTRA plays black: +1 (RE got 0 points)\n"
    
    summary_text += "\nScore Calculation:\n"
    
    # Add announcement information if any
    if game_data.get('re_announced', False) or game_data.get('contra_announced', False):
        summary_text += "Announcements:\n"
        if game_data.get('re_announced', False):
            summary_text += "- RE announced: +1\n"
        if game_data.get('contra_announced', False):
            summary_text += "- CONTRA announced: +1\n"
        if game_data.get('no90_announced', False):
            summary_text += "- No 90 announced: +1\n"
        if game_data.get('no60_announced', False):
            summary_text += "- No 60 announced: +1\n"
        if game_data.get('no30_announced', False):
            summary_text += "- No 30 announced: +1\n"
        if game_data.get('black_announced', False):
            summary_text += "- Black announced: +1\n"
        
        summary_text += f"- Score multiplier: {multiplier}x\n\n"
    
    # Add base point calculation
    summary_text += "Base Points:\n"
    summary_text += f"- Winning team: +1 point per player\n"
    summary_text += f"- Losing team: -1 point per player\n\n"
    
    # Add multiplier effect if applicable
    if multiplier > 1:
        summary_text += "With Multiplier:\n"
        summary_text += f"- Winning team: +1 × {multiplier} = +{multiplier} points per player\n"
        summary_text += f"- Losing team: -1 × {multiplier} = -{multiplier} points per player\n\n"
    
    # Add final scores
    summary_text += "Final Scores:\n"
    for i, team in enumerate(game.teams):
        player_name = "You" if i == 0 else f"Player {i}"
        if (team.name == 'RE' and game.winner.name == 'RE') or (team.name == 'KONTRA' and game.winner.name == 'KONTRA'):
            # This player is on the winning team
            points = f"+{multiplier}"
        else:
            # This player is on the losing team
            points = f"-{multiplier}"
        total_score = scoreboard['player_scores'][i]
        summary_text += f"- {player_name}: {points} points (Total: {total_score})\n"
    
    # Store the game summary in the game data
    game_data['game_summary'] = summary_text
    
    return summary_text

def update_scoreboard_for_game_over(game_id):
    """Update the scoreboard when a game is over."""
    game_data = games[game_id]
    game = game_data['game']
    multiplier = game_data.get('multiplier', 1)
    player_team = game.teams[0]
    
    print_scoreboard("Before Game Over Update", game)
    
    # In Doppelkopf, the base score is 1 point for winning
    # The multiplier is applied for announcements (Re, Contra, No 90, etc.)
    
    # Update player scores - winners get +1, losers get -1
    if game.winner.name == 'RE':
        # RE team won
        for i in range(len(game.teams)):
            if game.teams[i].name == 'RE':
                scoreboard['player_scores'][i] += 1 * multiplier  # Winners get positive points
            else:  # KONTRA team
                scoreboard['player_scores'][i] -= 1 * multiplier  # Losers get negative points
    else:
        # KONTRA team won
        for i in range(len(game.teams)):
            if game.teams[i].name == 'RE':
                scoreboard['player_scores'][i] -= 1 * multiplier  # Losers get negative points
            else:  # KONTRA team
                scoreboard['player_scores'][i] += 1 * multiplier  # Winners get positive points
    
    # Update win counts
    if game.winner == player_team:
        scoreboard['player_wins'] += 1
    else:
        scoreboard['ai_wins'] += 1
    
    print_scoreboard("After Game Over Update", game)
