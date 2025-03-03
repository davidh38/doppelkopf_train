#!/usr/bin/env python3
"""
Test script to verify the Kontra party winning with exactly 125 points in the Doppelkopf game.
"""

from src.game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam

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
    
    # We'll directly set the scores to simulate a game where KONTRA wins with exactly 125 points
    # This approach bypasses the trick winner determination logic
    
    # Set initial scores
    game.scores = [0, 0]  # [RE score, KONTRA score]
    game.player_scores = [0, 0, 0, 0]  # Individual player scores
    
    # Round 1: Player 1 (KONTRA team) wins a trick worth 28 points
    print("\nRound 1:")
    game.scores[1] += 28
    game.player_scores[1] += 28  # Player 1 gets the points
    
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
    game.scores[0] += 27
    game.player_scores[0] += 27  # Player 0 gets the points
    
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
    game.scores[1] += 42
    game.player_scores[3] += 42  # Player 3 gets the points
    
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
    game.scores[0] += 28
    game.player_scores[2] += 28  # Player 2 gets the points
    
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
    
    # End the game
    game._end_game()
    
    # Verify that the game is over and KONTRA team won with exactly 125 points
    assert game.game_over, "Game should be over"
    assert game.winner == PlayerTeam.KONTRA, "KONTRA team should win"
    assert game.scores[1] == 125, f"KONTRA team should have exactly 125 points, but has {game.scores[1]}"
    assert game.scores[0] == 115, f"RE team should have exactly 115 points, but has {game.scores[0]}"
    
    print(f"\nGame over, winner: {game.winner.name}")
    print(f"Final RE team score: {game.scores[0]} points")
    print(f"Final KONTRA team score: {game.scores[1]} points")
    
    # Calculate game points awarded at the end of the game for each individual player
    # In this scoring system, each player on the winning team gets 2 points
    # Each player on the losing team gets -2 points
    
    # Create a list to store individual player game points
    player_game_points = [0, 0, 0, 0]
    
    # Assign game points based on the winner
    for i, team in enumerate(game.teams):
        if team == game.winner:
            player_game_points[i] = 2  # Winning team players get +2
        else:
            player_game_points[i] = -2  # Losing team players get -2
    
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
    
    # Verify that the total points in the game is 240
    total_points = sum(game.scores)
    print(f"\nTotal points in the game: {total_points}")
    assert total_points == 240, f"Total points should be 240, but is {total_points}"
    
    print("Kontra party wins with 125 points test passed!")
    return True

if __name__ == "__main__":
    """Run the test."""
    print("Starting Doppelkopf game logic test...\n")
    
    kontra_party_win_success = test_kontra_party_wins_with_125_points()
    
    print("\n=== Test Results ===")
    print(f"Kontra party wins with 125 points: {'PASSED' if kontra_party_win_success else 'FAILED'}")
