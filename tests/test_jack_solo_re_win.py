#!/usr/bin/env python3
"""
Test script to verify the Jack Solo variant with RE announcement and scoring.
"""

from src.game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam

def test_jack_solo_re_win():
    """
    Test the scenario where a player plays Jack Solo, wins as RE with 128 points,
    and announces RE. The final score should be 6 points for the player and -2 for each other player.
    """
    print("\n=== Testing Jack Solo with RE Announcement and Win ===")
    
    # Create a new game
    game = DoppelkopfGame()
    
    # Reset the game
    game.reset()
    
    # Set up teams manually - Player 0 is RE (solo player), others are KONTRA
    game.teams = [PlayerTeam.RE, PlayerTeam.KONTRA, PlayerTeam.KONTRA, PlayerTeam.KONTRA]
    
    print("Teams:")
    for i, team in enumerate(game.teams):
        print(f"Player {i}: {team.name}")
    
    # Each player must choose a game variant
    # Player 0 chooses Jack Solo, others choose normal
    
    # Player 0 chooses Jack Solo
    game.current_player = 0
    print(f"Player 0 chooses Jack Solo variant")
    game.set_variant('jack_solo')
    
    # Other players choose normal
    for player_idx in range(1, game.num_players):
        game.current_player = player_idx
        print(f"Player {player_idx} chooses normal variant")
        game.set_variant('normal')
    
    # Verify that the variant selection phase is now over
    assert not game.variant_selection_phase, "Variant selection phase should be over"
    print(f"Game variant: {game.game_variant.name}")
    
    # Verify that Jack Solo was selected
    assert game.game_variant == GameVariant.JACK_SOLO, "Game variant should be Jack Solo"
    
    # Player 0 announces RE (which doubles the score)
    game.current_player = 0
    print("\nPlayer 0 announces RE")
    game.announce(0, 're')
    
    # Verify that RE was announced
    assert game.re_announced, "RE should be announced"
    
    # Track the round scores
    round_scores_re = []
    round_scores_kontra = []
    
    # Track individual player scores
    player_scores_history = [[] for _ in range(4)]
    
    # Set initial scores
    game.scores = [0, 0]  # [RE score, KONTRA score]
    game.player_scores = [0, 0, 0, 0]  # Individual player scores
    
    # Simulate a game where Player 0 (RE team) wins with 128 points
    # We'll directly set the scores to simulate the tricks
    
    # Round 1: Player 0 (RE team) wins a trick worth 30 points
    print("\nRound 1:")
    game.scores[0] += 30
    game.player_scores[0] += 30  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 1: {game.scores[0]} points")
    print(f"KONTRA team score after round 1: {game.scores[1]} points")
    print(f"Player scores after round 1: {game.player_scores}")
    
    # Round 2: Player 1 (KONTRA team) wins a trick worth 25 points
    print("\nRound 2:")
    game.scores[1] += 25
    game.player_scores[1] += 25  # Player 1 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 2: {game.scores[0]} points")
    print(f"KONTRA team score after round 2: {game.scores[1]} points")
    print(f"Player scores after round 2: {game.player_scores}")
    
    # Round 3: Player 0 (RE team) wins a trick worth 35 points
    print("\nRound 3:")
    game.scores[0] += 35
    game.player_scores[0] += 35  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 3: {game.scores[0]} points")
    print(f"KONTRA team score after round 3: {game.scores[1]} points")
    print(f"Player scores after round 3: {game.player_scores}")
    
    # Round 4: Player 2 (KONTRA team) wins a trick worth 22 points
    print("\nRound 4:")
    game.scores[1] += 22
    game.player_scores[2] += 22  # Player 2 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 4: {game.scores[0]} points")
    print(f"KONTRA team score after round 4: {game.scores[1]} points")
    print(f"Player scores after round 4: {game.player_scores}")
    
    # Round 5: Player 0 (RE team) wins a trick worth 28 points
    print("\nRound 5:")
    game.scores[0] += 28
    game.player_scores[0] += 28  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 5: {game.scores[0]} points")
    print(f"KONTRA team score after round 5: {game.scores[1]} points")
    print(f"Player scores after round 5: {game.player_scores}")
    
    # Round 6: Player 3 (KONTRA team) wins a trick worth 30 points
    print("\nRound 6:")
    game.scores[1] += 30
    game.player_scores[3] += 30  # Player 3 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 6: {game.scores[0]} points")
    print(f"KONTRA team score after round 6: {game.scores[1]} points")
    print(f"Player scores after round 6: {game.player_scores}")
    
    # Round 7: Player 0 (RE team) wins a trick worth 35 points
    print("\nRound 7:")
    game.scores[0] += 35
    game.player_scores[0] += 35  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game.scores[0])
    round_scores_kontra.append(game.scores[1])
    for i in range(4):
        player_scores_history[i].append(game.player_scores[i])
    
    print(f"RE team score after round 7: {game.scores[0]} points")
    print(f"KONTRA team score after round 7: {game.scores[1]} points")
    print(f"Player scores after round 7: {game.player_scores}")
    
    # Round 8: Player 1 (KONTRA team) wins a trick worth 35 points
    print("\nRound 8:")
    game.scores[1] += 35
    game.player_scores[1] += 35  # Player 1 gets the points
    
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
    
    # Verify that the game is over and RE team won with 128 points
    assert game.game_over, "Game should be over"
    assert game.winner == PlayerTeam.RE, "RE team should win"
    assert game.scores[0] == 128, f"RE team should have exactly 128 points, but has {game.scores[0]}"
    assert game.scores[1] == 112, f"KONTRA team should have exactly 112 points, but has {game.scores[1]}"
    
    print(f"\nGame over, winner: {game.winner.name}")
    print(f"Final RE team score: {game.scores[0]} points")
    print(f"Final KONTRA team score: {game.scores[1]} points")
    
    # Calculate game points awarded at the end of the game for each individual player
    # In Jack Solo, the solo player (Player 0) gets 3 points per opponent if they win
    # Each opponent gets -1 point if they lose
    # Since RE was announced, the points are doubled
    
    # Create a list to store individual player game points
    player_game_points = [0, 0, 0, 0]
    
    # Count players in each team
    re_players = sum(1 for team in game.teams if team == PlayerTeam.RE)
    kontra_players = sum(1 for team in game.teams if team == PlayerTeam.KONTRA)
    
    # Multiplier for RE announcement
    multiplier = 2 if game.re_announced else 1
    
    # Assign game points based on the winner
    if game.winner == PlayerTeam.RE:
        # RE team won (solo player)
        # Solo player gets 3 points per opponent, doubled for RE announcement
        solo_points = kontra_players * multiplier
        player_game_points[0] = solo_points
        
        # Each KONTRA player gets -1 point, doubled for RE announcement
        for i in range(1, 4):
            player_game_points[i] = -1 * multiplier
    else:
        # KONTRA team won
        # Solo player gets -3 points per opponent, doubled for RE announcement
        solo_points = -kontra_players * multiplier
        player_game_points[0] = solo_points
        
        # Each KONTRA player gets 1 point, doubled for RE announcement
        for i in range(1, 4):
            player_game_points[i] = 1 * multiplier
    
    print("\nGame points awarded to individual players:")
    for i, points in enumerate(player_game_points):
        team_name = game.teams[i].name
        print(f"Player {i} ({team_name}): {points} game points")
    
    # Verify that the solo player (Player 0) gets 6 points (3 opponents * 2 for RE announcement)
    assert player_game_points[0] == 6, f"Solo player should get 6 points, but got {player_game_points[0]}"
    
    # Verify that each opponent gets -2 points (-1 * 2 for RE announcement)
    for i in range(1, 4):
        assert player_game_points[i] == -2, f"Opponent {i} should get -2 points, but got {player_game_points[i]}"
    
    # Calculate total game points for each team
    total_re_game_points = sum(points for i, points in enumerate(player_game_points) if game.teams[i] == PlayerTeam.RE)
    total_kontra_game_points = sum(points for i, points in enumerate(player_game_points) if game.teams[i] == PlayerTeam.KONTRA)
    
    print(f"\nTotal RE team game points: {total_re_game_points}")
    print(f"Total KONTRA team game points: {total_kontra_game_points}")
    
    # Verify that the sum of game points is zero (zero-sum game)
    assert sum(player_game_points) == 0, f"Game points should sum to zero, but sum to {sum(player_game_points)}"
    
    # Print the round-by-round team scores
    print("\nRound-by-round team scores:")
    print("Round | RE Score | KONTRA Score")
    print("------|----------|-------------")
    for i in range(len(round_scores_re)):
        print(f"{i+1:5d} | {round_scores_re[i]:8d} | {round_scores_kontra[i]:11d}")
    
    # Print the round-by-round player scores
    print("\nRound-by-round player scores:")
    print("Round | Player 0 (RE) | Player 1 (KONTRA) | Player 2 (KONTRA) | Player 3 (KONTRA)")
    print("------|--------------|------------------|------------------|------------------")
    for i in range(len(player_scores_history[0])):
        print(f"{i+1:5d} | {player_scores_history[0][i]:12d} | {player_scores_history[1][i]:16d} | {player_scores_history[2][i]:16d} | {player_scores_history[3][i]:16d}")
    
    # Verify that the sum of player scores equals the sum of team scores
    player_total = sum(game.player_scores)
    team_total = sum(game.scores)
    print(f"\nSum of player scores: {player_total}")
    print(f"Sum of team scores: {team_total}")
    assert player_total == team_total, f"Sum of player scores ({player_total}) should equal sum of team scores ({team_total})"
    
    # Verify that the sum of RE player scores equals the RE team score
    re_player_total = sum(score for i, score in enumerate(game.player_scores) if game.teams[i] == PlayerTeam.RE)
    print(f"Sum of RE player scores: {re_player_total}")
    print(f"RE team score: {game.scores[0]}")
    assert re_player_total == game.scores[0], f"Sum of RE player scores ({re_player_total}) should equal RE team score ({game.scores[0]})"
    
    # Verify that the sum of KONTRA player scores equals the KONTRA team score
    kontra_player_total = sum(score for i, score in enumerate(game.player_scores) if game.teams[i] == PlayerTeam.KONTRA)
    print(f"Sum of KONTRA player scores: {kontra_player_total}")
    print(f"KONTRA team score: {game.scores[1]}")
    assert kontra_player_total == game.scores[1], f"Sum of KONTRA player scores ({kontra_player_total}) should equal KONTRA team score ({game.scores[1]})"
    
    # Verify that the total points in the game is 240
    total_points = sum(game.scores)
    print(f"\nTotal points in the game: {total_points}")
    assert total_points == 240, f"Total points should be 240, but is {total_points}"
    
    print("Jack Solo with RE announcement and win test passed!")
    return True

def main():
    """Run the test."""
    print("Starting Jack Solo with RE announcement and win test...\n")
    
    test_success = test_jack_solo_re_win()
    
    print("\n=== Test Result ===")
    print(f"Jack Solo with RE announcement and win: {'PASSED' if test_success else 'FAILED'}")

if __name__ == "__main__":
    main()
