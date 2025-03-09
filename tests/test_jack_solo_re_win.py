#!/usr/bin/env python3
"""
Test script to verify the Jack Solo variant with RE announcement and scoring.
"""

import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.game.doppelkopf import (
    create_game_state, create_card, set_variant, announce, end_game, get_card_order_value,
    SUIT_CLUBS, SUIT_SPADES, SUIT_HEARTS, SUIT_DIAMONDS,
    RANK_NINE, RANK_JACK, RANK_QUEEN, RANK_KING, RANK_TEN, RANK_ACE,
    TEAM_RE, TEAM_KONTRA, TEAM_UNKNOWN,
    VARIANT_NORMAL, VARIANT_HOCHZEIT, VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_FLESHLESS
)

def test_jack_solo_re_win():
    """
    Test the scenario where a player plays Jack Solo, wins as RE with 128 points,
    and announces RE. The final score should be 6 points for the player and -2 for each other player.
    """
    print("\n=== Testing Jack Solo with RE Announcement and Win ===")
    
    # Create a new game
    game = create_game_state()
    
    # Set up teams manually - Player 0 is RE (solo player), others are KONTRA
    game['teams'] = [TEAM_RE, TEAM_KONTRA, TEAM_KONTRA, TEAM_KONTRA]
    
    print("Teams:")
    for i, team in enumerate(game['teams']):
        print(f"Player {i}: {'RE' if team == TEAM_RE else 'KONTRA'}")
    
    # Each player must choose a game variant
    # Player 0 chooses Jack Solo, others choose normal
    
    # Player 0 chooses Jack Solo
    game['current_player'] = 0
    print(f"Player 0 chooses Jack Solo variant")
    set_variant(game, 'jack_solo', 0)
    
    # Other players choose normal
    for player_idx in range(1, game['num_players']):
        game['current_player'] = player_idx
        print(f"Player {player_idx} chooses normal variant")
        set_variant(game, 'normal', player_idx)
    
    # Verify that the variant selection phase is now over
    assert not game['variant_selection_phase'], "Variant selection phase should be over"
    print(f"Game variant: {game['game_variant']}")
    
    # Verify that Jack Solo was selected
    assert game['game_variant'] == VARIANT_JACK_SOLO, "Game variant should be Jack Solo"
    
    # Player 0 announces RE (which doubles the score)
    game['current_player'] = 0
    print("\nPlayer 0 announces RE")
    announce(game, 0, 're')
    
    # Verify that RE was announced
    assert game.get('re_announced', False), "RE should be announced"
    
    # Track the round scores
    round_scores_re = []
    round_scores_kontra = []
    
    # Track individual player scores
    player_scores_history = [[] for _ in range(4)]
    
    # Set initial scores
    game['scores'] = [0, 0]  # [RE score, KONTRA score]
    game['player_scores'] = [0, 0, 0, 0]  # Individual player scores
    
    # Simulate a game where Player 0 (RE team) wins with 128 points
    # We'll directly set the scores to simulate the tricks
    
    # Round 1: Player 0 (RE team) wins a trick worth 30 points
    print("\nRound 1:")
    game['scores'][0] += 30
    game['player_scores'][0] += 30  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 1: {game['scores'][0]} points")
    print(f"KONTRA team score after round 1: {game['scores'][1]} points")
    print(f"Player scores after round 1: {game['player_scores']}")
    
    # Round 2: Player 1 (KONTRA team) wins a trick worth 25 points
    print("\nRound 2:")
    game['scores'][1] += 25
    game['player_scores'][1] += 25  # Player 1 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 2: {game['scores'][0]} points")
    print(f"KONTRA team score after round 2: {game['scores'][1]} points")
    print(f"Player scores after round 2: {game['player_scores']}")
    
    # Round 3: Player 0 (RE team) wins a trick worth 35 points
    print("\nRound 3:")
    game['scores'][0] += 35
    game['player_scores'][0] += 35  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 3: {game['scores'][0]} points")
    print(f"KONTRA team score after round 3: {game['scores'][1]} points")
    print(f"Player scores after round 3: {game['player_scores']}")
    
    # Round 4: Player 2 (KONTRA team) wins a trick worth 22 points
    print("\nRound 4:")
    game['scores'][1] += 22
    game['player_scores'][2] += 22  # Player 2 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 4: {game['scores'][0]} points")
    print(f"KONTRA team score after round 4: {game['scores'][1]} points")
    print(f"Player scores after round 4: {game['player_scores']}")
    
    # Round 5: Player 0 (RE team) wins a trick worth 28 points
    print("\nRound 5:")
    game['scores'][0] += 28
    game['player_scores'][0] += 28  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 5: {game['scores'][0]} points")
    print(f"KONTRA team score after round 5: {game['scores'][1]} points")
    print(f"Player scores after round 5: {game['player_scores']}")
    
    # Round 6: Player 3 (KONTRA team) wins a trick worth 30 points
    print("\nRound 6:")
    game['scores'][1] += 30
    game['player_scores'][3] += 30  # Player 3 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 6: {game['scores'][0]} points")
    print(f"KONTRA team score after round 6: {game['scores'][1]} points")
    print(f"Player scores after round 6: {game['player_scores']}")
    
    # Round 7: Player 0 (RE team) wins a trick worth 35 points
    print("\nRound 7:")
    game['scores'][0] += 35
    game['player_scores'][0] += 35  # Player 0 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 7: {game['scores'][0]} points")
    print(f"KONTRA team score after round 7: {game['scores'][1]} points")
    print(f"Player scores after round 7: {game['player_scores']}")
    
    # Round 8: Player 1 (KONTRA team) wins a trick worth 35 points
    print("\nRound 8:")
    game['scores'][1] += 35
    game['player_scores'][1] += 35  # Player 1 gets the points
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 8: {game['scores'][0]} points")
    print(f"KONTRA team score after round 8: {game['scores'][1]} points")
    print(f"Player scores after round 8: {game['player_scores']}")
    
    # Round 9: Player 0 (RE team) wins a trick worth 0 points
    print("\nRound 9:")
    # No points in this trick
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 9: {game['scores'][0]} points")
    print(f"KONTRA team score after round 9: {game['scores'][1]} points")
    print(f"Player scores after round 9: {game['player_scores']}")
    
    # Round 10: Player 2 (KONTRA team) wins a trick worth 0 points
    print("\nRound 10:")
    # No points in this trick
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 10: {game['scores'][0]} points")
    print(f"KONTRA team score after round 10: {game['scores'][1]} points")
    print(f"Player scores after round 10: {game['player_scores']}")
    
    # End the game
    end_game(game)
    
    # Verify that the game is over and RE team won with 128 points
    assert game['game_over'], "Game should be over"
    assert game['winner'] == TEAM_RE, "RE team should win"
    assert game['scores'][0] == 128, f"RE team should have exactly 128 points, but has {game['scores'][0]}"
    assert game['scores'][1] == 112, f"KONTRA team should have exactly 112 points, but has {game['scores'][1]}"
    
    print(f"\nGame over, winner: {'RE'}")
    print(f"Final RE team score: {game['scores'][0]} points")
    print(f"Final KONTRA team score: {game['scores'][1]} points")
    
    # Game points are now calculated in the end_game function
    # The game logic now properly implements a zero-sum approach for game points
    # Each time points are awarded to one team, corresponding points are subtracted from the other team
    
    # Get the game points calculated by the game logic
    player_game_points = game.get('player_game_points', [0, 0, 0, 0])
    
    print("\nGame points awarded to individual players:")
    for i, points in enumerate(player_game_points):
        team_name = 'RE' if game['teams'][i] == TEAM_RE else 'KONTRA'
        print(f"Player {i} ({team_name}): {points} game points")
    
    # Verify that the solo player (Player 0) gets 6 points (3 opponents * 2 for RE announcement)
    assert player_game_points[0] == 6, f"Solo player should get 6 points, but got {player_game_points[0]}"
    
    # Verify that each opponent gets -2 points (-1 * 2 for RE announcement)
    for i in range(1, 4):
        assert player_game_points[i] == -2, f"Opponent {i} should get -2 points, but got {player_game_points[i]}"
    
    # Calculate total game points for each team
    total_re_game_points = sum(points for i, points in enumerate(player_game_points) if game['teams'][i] == TEAM_RE)
    total_kontra_game_points = sum(points for i, points in enumerate(player_game_points) if game['teams'][i] == TEAM_KONTRA)
    
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
    player_total = sum(game['player_scores'])
    team_total = sum(game['scores'])
    print(f"\nSum of player scores: {player_total}")
    print(f"Sum of team scores: {team_total}")
    assert player_total == team_total, f"Sum of player scores ({player_total}) should equal sum of team scores ({team_total})"
    
    # Verify that the sum of RE player scores equals the RE team score
    re_player_total = sum(score for i, score in enumerate(game['player_scores']) if game['teams'][i] == TEAM_RE)
    print(f"Sum of RE player scores: {re_player_total}")
    print(f"RE team score: {game['scores'][0]}")
    assert re_player_total == game['scores'][0], f"Sum of RE player scores ({re_player_total}) should equal RE team score ({game['scores'][0]})"
    
    # Verify that the sum of KONTRA player scores equals the KONTRA team score
    kontra_player_total = sum(score for i, score in enumerate(game['player_scores']) if game['teams'][i] == TEAM_KONTRA)
    print(f"Sum of KONTRA player scores: {kontra_player_total}")
    print(f"KONTRA team score: {game['scores'][1]}")
    assert kontra_player_total == game['scores'][1], f"Sum of KONTRA player scores ({kontra_player_total}) should equal KONTRA team score ({game['scores'][1]})"
    
    # Verify that the total points in the game is 240
    total_points = sum(game['scores'])
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
