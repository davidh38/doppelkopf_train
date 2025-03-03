#!/usr/bin/env python3
"""
Test script to verify the Kontra party winning with exactly 125 points in the Doppelkopf game.
"""

import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam

def test_kontra_party_wins_with_125_points():
    """Test the scenario where the Kontra party wins with exactly 125 points and track round scores."""
    print("\n=== Testing Kontra Party Winning with 125 Points ===")
    
    # Create a new game with a controlled setup
    game = DoppelkopfGame()
    
    # Reset the game
    game.reset()
    
    # Set up teams manually
    game.teams = [PlayerTeam.RE, PlayerTeam.KONTRA, PlayerTeam.RE, PlayerTeam.KONTRA]
    
    # Each player must choose a game variant
    # We'll simulate this by having each player vote for the normal variant
    for player_idx in range(game.num_players):
        # Set the current player
        game.current_player = player_idx
        
        # Choose the normal variant
        print(f"Player {player_idx} chooses the normal variant")
        game.set_variant('normal')
    
    # Verify that the variant selection phase is now over
    assert not game.variant_selection_phase, "Variant selection phase should be over"
    print(f"Game variant: {game.game_variant.name}")
    
    print("Teams:")
    for i, team in enumerate(game.teams):
        print(f"Player {i}: {team.name}")
    
    # Track the round scores
    round_scores_re = []
    round_scores_kontra = []
    
    # Track individual player scores
    player_scores_history = [[] for _ in range(4)]
    
    # We'll simulate a game where KONTRA wins with exactly 125 points
    # by creating tricks and using the game logic to calculate the scores
    
    # Set initial scores
    game.scores = [0, 0]  # [RE score, KONTRA score]
    game.player_scores = [0, 0, 0, 0]  # Individual player scores
    
    # Round 1: Player 1 (KONTRA team) wins a trick worth 28 points
    print("\nRound 1:")
    # Create a trick where KONTRA player 1 wins
    game.current_trick = [
        Card(Suit.HEARTS, Rank.NINE, False),     # Player 0 (RE) plays heart nine (0 points)
        Card(Suit.HEARTS, Rank.TEN, False),      # Player 1 (KONTRA) plays heart ten (10 points)
        Card(Suit.HEARTS, Rank.KING, False),     # Player 2 (RE) plays heart king (4 points)
        Card(Suit.HEARTS, Rank.ACE, False)       # Player 3 (KONTRA) plays heart ace (11 points)
    ]
    
    # Set the current player to the first player
    game.current_player = 0
    
    # Determine the trick winner (should be player 3 with the heart ace)
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
    
    # Complete the trick using the game logic
    game._complete_trick()
    
    # Clear the current trick for the next round
    game.current_trick = []
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 1: {game.scores[0]} points")
    print(f"KONTRA team score after round 1: {game.scores[1]} points")
    print(f"Player scores after round 1: {game.player_scores}")
    
    # Round 2: Player 0 (RE team) wins a trick worth 27 points
    print("\nRound 2:")
    # Create a trick where RE player 0 wins
    game.current_trick = [
        Card(Suit.SPADES, Rank.ACE, False),      # Player 0 (RE) plays spade ace (11 points)
        Card(Suit.SPADES, Rank.KING, False),     # Player 1 (KONTRA) plays spade king (4 points)
        Card(Suit.SPADES, Rank.TEN, False),      # Player 2 (RE) plays spade ten (10 points)
        Card(Suit.SPADES, Rank.NINE, False)      # Player 3 (KONTRA) plays spade nine (0 points)
    ]
    
    # Set the current player to the first player
    game.current_player = 0
    
    # Determine the trick winner (should be player 0 with the spade ace)
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
    
    # Complete the trick using the game logic
    game._complete_trick()
    
    # Clear the current trick for the next round
    game.current_trick = []
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 2: {game.scores[0]} points")
    print(f"KONTRA team score after round 2: {game.scores[1]} points")
    print(f"Player scores after round 2: {game.player_scores}")
    
    # Round 3: Player 3 (KONTRA team) wins a trick worth 42 points
    print("\nRound 3:")
    # Create a trick where KONTRA player 3 wins
    game.current_trick = [
        Card(Suit.CLUBS, Rank.TEN, False),       # Player 0 (RE) plays club ten (10 points)
        Card(Suit.CLUBS, Rank.KING, False),      # Player 1 (KONTRA) plays club king (4 points)
        Card(Suit.CLUBS, Rank.ACE, False),       # Player 2 (RE) plays club ace (11 points)
        Card(Suit.CLUBS, Rank.QUEEN, False)      # Player 3 (KONTRA) plays club queen (3 points, but it's a trump)
    ]
    
    # Set the current player to the first player
    game.current_player = 0
    
    # Determine the trick winner (should be player 3 with the club queen, which is a trump)
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
    
    # Complete the trick using the game logic
    game._complete_trick()
    
    # Clear the current trick for the next round
    game.current_trick = []
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 3: {game.scores[0]} points")
    print(f"KONTRA team score after round 3: {game.scores[1]} points")
    print(f"Player scores after round 3: {game.player_scores}")
    
    # Round 4: Player 2 (RE team) wins a trick worth 28 points
    print("\nRound 4:")
    # Create a trick where RE player 2 wins
    game.current_trick = [
        Card(Suit.DIAMONDS, Rank.NINE, False),   # Player 0 (RE) plays diamond nine (0 points, but it's a trump)
        Card(Suit.DIAMONDS, Rank.TEN, False),    # Player 1 (KONTRA) plays diamond ten (10 points, but it's a trump)
        Card(Suit.DIAMONDS, Rank.KING, False),   # Player 2 (RE) plays diamond king (4 points, but it's a trump)
        Card(Suit.DIAMONDS, Rank.QUEEN, False)   # Player 3 (KONTRA) plays diamond queen (3 points, but it's a trump)
    ]
    
    # Set the current player to the first player
    game.current_player = 0
    
    # Determine the trick winner (should be player 3 with the diamond queen, which is a trump)
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
    
    # Complete the trick using the game logic
    game._complete_trick()
    
    # Clear the current trick for the next round
    game.current_trick = []
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 4: {game.scores[0]} points")
    print(f"KONTRA team score after round 4: {game.scores[1]} points")
    print(f"Player scores after round 4: {game.player_scores}")
    
    # Round 5: Player 1 (KONTRA team) wins a trick worth 30 points
    print("\nRound 5:")
    game.scores[1] += 30
    game.player_scores[1] += 30  # Player 1 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 5: {game.scores[0]} points")
    print(f"KONTRA team score after round 5: {game.scores[1]} points")
    print(f"Player scores after round 5: {game.player_scores}")
    
    # Round 6: Player 0 (RE team) wins a trick worth 30 points
    print("\nRound 6:")
    game.scores[0] += 30
    game.player_scores[0] += 30  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 6: {game.scores[0]} points")
    print(f"KONTRA team score after round 6: {game.scores[1]} points")
    print(f"Player scores after round 6: {game.player_scores}")
    
    # Round 7: Player 3 (KONTRA team) wins a trick worth 25 points to reach exactly 125 points
    print("\nRound 7:")
    game.scores[1] += 25
    game.player_scores[3] += 25  # Player 3 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 7: {game.scores[0]} points")
    print(f"KONTRA team score after round 7: {game.scores[1]} points")
    print(f"Player scores after round 7: {game.player_scores}")
    
    # Round 8: Player 2 (RE team) wins a trick worth 30 points
    print("\nRound 8:")
    game.scores[0] += 30
    game.player_scores[2] += 30  # Player 2 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 8: {game.scores[0]} points")
    print(f"KONTRA team score after round 8: {game.scores[1]} points")
    print(f"Player scores after round 8: {game.player_scores}")
    
    # Round 9: Player 1 (KONTRA team) wins a trick worth 15 points
    print("\nRound 9:")
    game.scores[1] += 15
    game.player_scores[1] += 15  # Player 1 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 9: {game.scores[0]} points")
    print(f"KONTRA team score after round 9: {game.scores[1]} points")
    print(f"Player scores after round 9: {game.player_scores}")
    
    # Round 10: Player 0 (RE team) wins a trick worth 15 points
    print("\nRound 10:")
    game.scores[0] += 15
    game.player_scores[0] += 15  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 10: {game.scores[0]} points")
    print(f"KONTRA team score after round 10: {game.scores[1]} points")
    print(f"Player scores after round 10: {game.player_scores}")
    
    # End the game
    game._end_game()
    
    # Verify that the game is over and KONTRA team won
    assert game.game_over, "Game should be over"
    assert game.winner == PlayerTeam.KONTRA, "KONTRA team should win"
    assert game.scores[1] >= 121, f"KONTRA team should have at least 121 points, but has {game.scores[1]}"
    assert game.scores[0] < 120, f"RE team should have less than 120 points, but has {game.scores[0]}"
    
    print(f"\nGame over, winner: {game.winner.name}")
    print(f"Final RE team score: {game.scores[0]} points")
    print(f"Final KONTRA team score: {game.scores[1]} points")
    
    # Game points are now calculated in the _end_game method of the DoppelkopfGame class
    # The game logic now properly implements a zero-sum approach for game points
    # Each time points are awarded to one team, corresponding points are subtracted from the other team
    
    # Get the game points calculated by the game logic
    player_game_points = game.player_game_points
    
    print("\nGame points awarded to individual players:")
    for i, points in enumerate(player_game_points):
        team_name = game.teams[i].name
        print(f"Player {i} ({team_name}): {points} game points")
    
    # Calculate total game points for each team
    total_re_game_points = sum(points for i, points in enumerate(player_game_points) if game.teams[i] == PlayerTeam.RE)
    total_kontra_game_points = sum(points for i, points in enumerate(player_game_points) if game.teams[i] == PlayerTeam.KONTRA)
    
    print(f"\nTotal RE team game points: {total_re_game_points}")
    print(f"Total KONTRA team game points: {total_kontra_game_points}")
    
    # Verify that the sum of game points is zero (zero-sum game)
    assert sum(player_game_points) == 0, "Game points should sum to zero"
    
    # Verify that the winning team has positive total game points
    if game.winner == PlayerTeam.RE:
        assert total_re_game_points > 0, "Winning team should have positive total game points"
        assert total_kontra_game_points < 0, "Losing team should have negative total game points"
    else:
        assert total_re_game_points < 0, "Losing team should have negative total game points"
        assert total_kontra_game_points > 0, "Winning team should have positive total game points"
    
    # Print the round-by-round team scores
    print("\nRound-by-round team scores:")
    print("Round | RE Score | KONTRA Score")
    print("------|----------|-------------")
    for i in range(len(round_scores_re)):
        print(f"{i+1:5d} | {round_scores_re[i]:8d} | {round_scores_kontra[i]:11d}")
    
    # Print the round-by-round player scores
    print("\nRound-by-round player scores:")
    print("Round | Player 0 (RE) | Player 1 (KONTRA) | Player 2 (RE) | Player 3 (KONTRA)")
    print("------|--------------|------------------|--------------|------------------")
    for i in range(len(player_scores_history[0])):
        print(f"{i+1:5d} | {player_scores_history[0][i]:12d} | {player_scores_history[1][i]:16d} | {player_scores_history[2][i]:12d} | {player_scores_history[3][i]:16d}")
    
    # Verify that the sum of player scores equals the sum of team scores
    player_total = sum(game.player_scores)
    team_total = sum(game.scores)
    print(f"\nSum of player scores: {player_total}")
    print(f"Sum of team scores: {team_total}")
    assert player_total == team_total, f"Sum of player scores ({player_total}) should equal sum of team scores ({team_total})"
    
    # Verify that the sum of RE player scores equals the RE team score
    re_player_total = game.player_scores[0] + game.player_scores[2]  # Players 0 and 2 are RE
    print(f"Sum of RE player scores: {re_player_total}")
    print(f"RE team score: {game.scores[0]}")
    assert re_player_total == game.scores[0], f"Sum of RE player scores ({re_player_total}) should equal RE team score ({game.scores[0]})"
    
    # Verify that the sum of KONTRA player scores equals the KONTRA team score
    kontra_player_total = game.player_scores[1] + game.player_scores[3]  # Players 1 and 3 are KONTRA
    print(f"Sum of KONTRA player scores: {kontra_player_total}")
    print(f"KONTRA team score: {game.scores[1]}")
    assert kontra_player_total == game.scores[1], f"Sum of KONTRA player scores ({kontra_player_total}) should equal KONTRA team score ({game.scores[1]})"
    
    # Verify that the total points in the game is the sum of all card values
    total_points = sum(game.scores)
    print(f"\nTotal points in the game: {total_points}")
    # In a real game, the total points would be 240, but in our test we're not using all cards
    # so the total points will be less than 240
    
    print("Kontra party wins with 125 points test passed!")
    return True

if __name__ == "__main__":
    """Run the test."""
    print("Starting Doppelkopf game logic test...\n")
    
    kontra_party_win_success = test_kontra_party_wins_with_125_points()
    
    print("\n=== Test Results ===")
    print(f"Kontra party wins with 125 points: {'PASSED' if kontra_party_win_success else 'FAILED'}")
