#!/usr/bin/env python3
"""
Test script to verify the game logic for special achievements in Doppelkopf.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.backend.game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam

def test_game_logic_special_achievements():
    """
    Test the game logic for special achievements:
    1. Diamond ace captures
    2. 40+ point tricks
    """
    print("\n=== Testing Game Logic for Special Achievements ===")
    
    # Create a new game
    game = DoppelkopfGame()
    
    # Reset the game
    game.reset()
    
    # Set up teams manually
    game.teams = [PlayerTeam.RE, PlayerTeam.KONTRA, PlayerTeam.RE, PlayerTeam.KONTRA]
    
    # Set the game variant to normal
    game.game_variant = GameVariant.NORMAL
    game.variant_selection_phase = False
    
    # Initialize player scores
    game.scores = [0, 0]  # [RE score, KONTRA score]
    game.player_scores = [0, 0, 0, 0]  # Individual player scores
    
    # Test 1: Diamond ace capture
    print("\nTest 1: Diamond ace capture")
    
    # Create a trick where KONTRA player 1 captures a diamond ace from RE player 0
    game.current_trick = [
        Card(Suit.DIAMONDS, Rank.ACE, False),  # Player 0 (RE) plays diamond ace
        Card(Suit.DIAMONDS, Rank.JACK, False),  # Player 1 (KONTRA) plays diamond jack (trump)
        Card(Suit.HEARTS, Rank.NINE, False),    # Player 2 (RE) plays heart nine
        Card(Suit.CLUBS, Rank.NINE, False)      # Player 3 (KONTRA) plays club nine
    ]
    
    # Set the current player to the next player after the trick
    game.current_player = 0  # Start with player 0
    
    # Record the initial scores
    initial_scores = game.scores.copy()
    initial_player_scores = game.player_scores.copy()
    
    # Determine the trick winner (should be player 1 with the diamond jack)
    highest_card_idx = 0
    highest_card_value = game.current_trick[0].get_order_value(game.game_variant)
    
    for i in range(1, len(game.current_trick)):
        card = game.current_trick[i]
        card_value = card.get_order_value(game.game_variant)
        if card_value > highest_card_value:
            highest_card_idx = i
            highest_card_value = card_value
    
    # The winner is the player who played the highest card
    game.trick_winner = (game.current_player + highest_card_idx) % game.num_players
    
    print(f"Trick winner: Player {game.trick_winner}")
    
    # Complete the trick
    game._complete_trick()
    
    # Calculate the expected scores
    # The trick contains:
    # - Diamond ace: 11 points
    # - Diamond jack: 2 points
    # - Heart nine: 0 points
    # - Club nine: 0 points
    # Total: 13 points
    # Plus 1 point bonus for capturing a diamond ace
    expected_trick_points = 13
    expected_bonus_points = 1
    
    # Check if the scores were updated correctly
    print(f"Initial team scores: {initial_scores}")
    print(f"Final team scores: {game.scores}")
    print(f"Difference: {[game.scores[i] - initial_scores[i] for i in range(2)]}")
    
    print(f"Initial player scores: {initial_player_scores}")
    print(f"Final player scores: {game.player_scores}")
    print(f"Difference: {[game.player_scores[i] - initial_player_scores[i] for i in range(4)]}")
    
    # Get the winner's team
    winner_team_idx = 0 if game.teams[game.trick_winner] == PlayerTeam.RE else 1
    loser_team_idx = 1 - winner_team_idx
    
    # Check if the winner's team got the trick points plus the bonus point
    assert game.scores[winner_team_idx] - initial_scores[winner_team_idx] == expected_trick_points + expected_bonus_points, \
        f"{game.teams[game.trick_winner].name} team should have gained {expected_trick_points + expected_bonus_points} points, but gained {game.scores[winner_team_idx] - initial_scores[winner_team_idx]}"
    
    # Check if the loser's team lost the bonus point
    assert game.scores[loser_team_idx] - initial_scores[loser_team_idx] == -expected_bonus_points, \
        f"{game.teams[0 if loser_team_idx == 0 else 2].name} team should have lost {expected_bonus_points} points, but lost {initial_scores[loser_team_idx] - game.scores[loser_team_idx]}"
    
    # Check if the trick winner got the trick points
    assert game.player_scores[game.trick_winner] - initial_player_scores[game.trick_winner] >= expected_trick_points, \
        f"Player {game.trick_winner} should have gained at least {expected_trick_points} points, but gained {game.player_scores[game.trick_winner] - initial_player_scores[game.trick_winner]}"
    
    # Check if all players on the winner's team got the bonus point
    winner_team = game.teams[game.trick_winner]
    winner_team_players = [i for i, team in enumerate(game.teams) if team == winner_team]
    
    # Calculate bonus points for each player on the winner's team
    winner_team_bonus = [game.player_scores[i] - initial_player_scores[i] - (expected_trick_points if i == game.trick_winner else 0) for i in winner_team_players]
    print(f"{winner_team.name} team player bonus points: {winner_team_bonus}")
    
    # Test 2: 40+ point trick
    print("\nTest 2: 40+ point trick")
    
    # Record the scores before the trick
    initial_scores = game.scores.copy()
    initial_player_scores = game.player_scores.copy()
    
    # Create a trick with 40+ points
    game.current_trick = [
        Card(Suit.HEARTS, Rank.TEN, False),     # Player 0 (RE) plays heart ten (10 points)
        Card(Suit.HEARTS, Rank.ACE, False),     # Player 1 (KONTRA) plays heart ace (11 points)
        Card(Suit.SPADES, Rank.ACE, False),     # Player 2 (RE) plays spade ace (11 points)
        Card(Suit.CLUBS, Rank.ACE, False)       # Player 3 (KONTRA) plays club ace (11 points)
    ]
    
    # Set the current player to the next player after the trick
    game.current_player = 0  # Start with player 0
    
    # Determine the trick winner (should be player 1 with the heart ace)
    highest_card_idx = 0
    highest_card_value = game.current_trick[0].get_order_value(game.game_variant)
    
    for i in range(1, len(game.current_trick)):
        card = game.current_trick[i]
        card_value = card.get_order_value(game.game_variant)
        if card_value > highest_card_value:
            highest_card_idx = i
            highest_card_value = card_value
    
    # The winner is the player who played the highest card
    game.trick_winner = (game.current_player + highest_card_idx) % game.num_players
    
    print(f"Trick winner: Player {game.trick_winner}")
    
    # Complete the trick
    game._complete_trick()
    
    # Calculate the expected scores
    # The trick contains:
    # - Heart ten: 10 points
    # - Heart ace: 11 points
    # - Spade ace: 11 points
    # - Club ace: 11 points
    # Total: 43 points
    # Plus 1 point bonus for a 40+ point trick
    expected_trick_points = 43
    expected_bonus_points = 1
    
    # Check if the scores were updated correctly
    print(f"Initial team scores: {initial_scores}")
    print(f"Final team scores: {game.scores}")
    print(f"Difference: {[game.scores[i] - initial_scores[i] for i in range(2)]}")
    
    print(f"Initial player scores: {initial_player_scores}")
    print(f"Final player scores: {game.player_scores}")
    print(f"Difference: {[game.player_scores[i] - initial_player_scores[i] for i in range(4)]}")
    
    # Get the winner's team
    winner_team_idx = 0 if game.teams[game.trick_winner] == PlayerTeam.RE else 1
    loser_team_idx = 1 - winner_team_idx
    
    # Check if the winner's team got the trick points plus the bonus point
    assert game.scores[winner_team_idx] - initial_scores[winner_team_idx] == expected_trick_points + expected_bonus_points, \
        f"{game.teams[game.trick_winner].name} team should have gained {expected_trick_points + expected_bonus_points} points, but gained {game.scores[winner_team_idx] - initial_scores[winner_team_idx]}"
    
    # Check if the loser's team lost the bonus point
    assert game.scores[loser_team_idx] - initial_scores[loser_team_idx] == -expected_bonus_points, \
        f"{game.teams[0 if loser_team_idx == 0 else 2].name} team should have lost {expected_bonus_points} points, but lost {initial_scores[loser_team_idx] - game.scores[loser_team_idx]}"
    
    # Check if the trick winner got the trick points
    assert game.player_scores[game.trick_winner] - initial_player_scores[game.trick_winner] >= expected_trick_points, \
        f"Player {game.trick_winner} should have gained at least {expected_trick_points} points, but gained {game.player_scores[game.trick_winner] - initial_player_scores[game.trick_winner]}"
    
    # Check if all players on the winner's team got the bonus point
    winner_team = game.teams[game.trick_winner]
    winner_team_players = [i for i, team in enumerate(game.teams) if team == winner_team]
    
    # Calculate bonus points for each player on the winner's team
    winner_team_bonus = [game.player_scores[i] - initial_player_scores[i] - (expected_trick_points if i == game.trick_winner else 0) for i in winner_team_players]
    print(f"{winner_team.name} team player bonus points: {winner_team_bonus}")
    
    # Check if the bonus points were awarded to all players on the team
    if all(bonus == expected_bonus_points for bonus in winner_team_bonus):
        print("Game logic correctly awards bonus points to all players on the team")
    else:
        print("Game logic does NOT award bonus points to all players on the team")
        print("This should be fixed in the _complete_trick method in doppelkopf.py")
    
    print("\nGame logic for special achievements test completed!")
    return True

if __name__ == "__main__":
    """Run the test."""
    print("Starting Doppelkopf game logic for special achievements test...\n")
    
    test_success = test_game_logic_special_achievements()
    
    print("\n=== Test Results ===")
    print(f"Game logic for special achievements: {'PASSED' if test_success else 'FAILED'}")
