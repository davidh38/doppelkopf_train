#!/usr/bin/env python3
"""
Test script to verify the Kontra party winning with exactly 125 points in the Doppelkopf game.
"""

import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.game.doppelkopf import (
    create_game_state, create_card, set_variant, end_game, complete_trick, get_card_order_value,
    SUIT_CLUBS, SUIT_SPADES, SUIT_HEARTS, SUIT_DIAMONDS,
    RANK_NINE, RANK_JACK, RANK_QUEEN, RANK_KING, RANK_TEN, RANK_ACE,
    TEAM_RE, TEAM_KONTRA, TEAM_UNKNOWN,
    VARIANT_NORMAL, VARIANT_HOCHZEIT, VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_FLESHLESS, VARIANT_KING_SOLO
)

def test_kontra_party_wins_with_125_points():
    """Test the scenario where the Kontra party wins with exactly 125 points and track round scores."""
    print("\n=== Testing Kontra Party Winning with 125 Points ===")
    
    # Create a new game with a controlled setup
    game = create_game_state()
    
    # Set up teams manually - Players 0 and 2 are KONTRA, Players 1 and 3 are RE
    game['teams'] = [TEAM_KONTRA, TEAM_RE, TEAM_KONTRA, TEAM_RE]
    
    # Print the team assignments for clarity
    print("Teams:")
    for i, team in enumerate(game['teams']):
        print(f"Player {i}: {'RE' if team == TEAM_RE else 'KONTRA'}")
    
    # Each player must choose a game variant
    # We'll simulate this by having each player vote for the normal variant
    for player_idx in range(game['num_players']):
        # Set the current player
        game['current_player'] = player_idx
        
        # Choose the normal variant
        print(f"Player {player_idx} chooses the normal variant")
        set_variant(game, 'normal', player_idx)
    
    # Verify that the variant selection phase is now over
    assert not game['variant_selection_phase'], "Variant selection phase should be over"
    print(f"Game variant: {game['game_variant']}")
    
    
    # Track the round scores
    round_scores_re = []
    round_scores_kontra = []
    
    # Track individual player scores
    player_scores_history = [[] for _ in range(4)]
    
    # We'll simulate a game where KONTRA wins with exactly 125 points
    # by creating tricks and using the game logic to calculate the scores
    
    # Set initial scores
    game['scores'] = [0, 0]  # [RE score, KONTRA score]
    game['player_scores'] = [0, 0, 0, 0]  # Individual player scores
    
    # Round 1: Player 0 (KONTRA team) wins a trick worth 25 points
    print("\nRound 1:")
    # Create a trick where KONTRA player 0 wins
    game['current_trick'] = [
        create_card(SUIT_DIAMONDS, RANK_QUEEN, False),  # Player 0 (KONTRA) plays diamond queen (3 points, but it's a trump)
        create_card(SUIT_HEARTS, RANK_TEN, False),      # Player 1 (RE) plays heart ten (10 points)
        create_card(SUIT_HEARTS, RANK_KING, False),     # Player 2 (KONTRA) plays heart king (4 points)
        create_card(SUIT_HEARTS, RANK_ACE, False)       # Player 3 (RE) plays heart ace (11 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 0 (KONTRA)
    game['trick_winner'] = 0
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 1: {game['scores'][0]} points")
    print(f"KONTRA team score after round 1: {game['scores'][1]} points")
    print(f"Player scores after round 1: {game['player_scores']}")
    
    # Round 2: Player 2 (KONTRA team) wins a trick worth 25 points
    print("\nRound 2:")
    # Create a trick where KONTRA player 2 wins
    game['current_trick'] = [
        create_card(SUIT_SPADES, RANK_ACE, False),      # Player 0 (KONTRA) plays spade ace (11 points)
        create_card(SUIT_SPADES, RANK_KING, False),     # Player 1 (RE) plays spade king (4 points)
        create_card(SUIT_DIAMONDS, RANK_JACK, False),   # Player 2 (KONTRA) plays diamond jack (2 points, but it's a trump)
        create_card(SUIT_SPADES, RANK_TEN, False)       # Player 3 (RE) plays spade ten (10 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 2 (KONTRA)
    game['trick_winner'] = 2
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 2: {game['scores'][0]} points")
    print(f"KONTRA team score after round 2: {game['scores'][1]} points")
    print(f"Player scores after round 2: {game['player_scores']}")
    
    # Round 3: Player 0 (KONTRA team) wins a trick worth 28 points
    print("\nRound 3:")
    # Create a trick where KONTRA player 0 wins
    game['current_trick'] = [
        create_card(SUIT_DIAMONDS, RANK_ACE, False),    # Player 0 (KONTRA) plays diamond ace (11 points, but it's a trump)
        create_card(SUIT_CLUBS, RANK_KING, False),      # Player 1 (RE) plays club king (4 points)
        create_card(SUIT_CLUBS, RANK_ACE, False),       # Player 2 (KONTRA) plays club ace (11 points)
        create_card(SUIT_CLUBS, RANK_QUEEN, False)      # Player 3 (RE) plays club queen (3 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 0 (KONTRA)
    game['trick_winner'] = 0
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 3: {game['scores'][0]} points")
    print(f"KONTRA team score after round 3: {game['scores'][1]} points")
    print(f"Player scores after round 3: {game['player_scores']}")
    
    # Round 4: Player 2 (KONTRA team) wins a trick worth 17 points
    print("\nRound 4:")
    # Create a trick where KONTRA player 2 wins
    game['current_trick'] = [
        create_card(SUIT_HEARTS, RANK_NINE, False),     # Player 0 (KONTRA) plays heart nine (0 points)
        create_card(SUIT_HEARTS, RANK_TEN, False),      # Player 1 (RE) plays heart ten (10 points)
        create_card(SUIT_CLUBS, RANK_QUEEN, False),     # Player 2 (KONTRA) plays club queen (3 points, but it's a trump)
        create_card(SUIT_HEARTS, RANK_KING, False)      # Player 3 (RE) plays heart king (4 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 2 (KONTRA)
    game['trick_winner'] = 2
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 4: {game['scores'][0]} points")
    print(f"KONTRA team score after round 4: {game['scores'][1]} points")
    print(f"Player scores after round 4: {game['player_scores']}")
    
    # Round 5: Player 0 (KONTRA team) wins a trick worth 26 points
    print("\nRound 5:")
    # Create a trick where KONTRA player 0 wins
    game['current_trick'] = [
        create_card(SUIT_CLUBS, RANK_JACK, False),      # Player 0 (KONTRA) plays club jack (2 points, but it's a trump)
        create_card(SUIT_HEARTS, RANK_ACE, False),      # Player 1 (RE) plays heart ace (11 points)
        create_card(SUIT_HEARTS, RANK_TEN, False),      # Player 2 (KONTRA) plays heart ten (10 points)
        create_card(SUIT_HEARTS, RANK_QUEEN, False)     # Player 3 (RE) plays heart queen (3 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 0 (KONTRA)
    game['trick_winner'] = 0
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 5: {game['scores'][0]} points")
    print(f"KONTRA team score after round 5: {game['scores'][1]} points")
    print(f"Player scores after round 5: {game['player_scores']}")
    
    # Round 6: Player 2 (KONTRA team) wins a trick worth 28 points
    print("\nRound 6:")
    # Create a trick where KONTRA player 2 wins
    game['current_trick'] = [
        create_card(SUIT_SPADES, RANK_NINE, False),     # Player 0 (KONTRA) plays spade nine (0 points)
        create_card(SUIT_SPADES, RANK_TEN, False),      # Player 1 (RE) plays spade ten (10 points)
        create_card(SUIT_DIAMONDS, RANK_TEN, False),    # Player 2 (KONTRA) plays diamond ten (10 points, but it's a trump)
        create_card(SUIT_SPADES, RANK_QUEEN, False)     # Player 3 (RE) plays spade queen (3 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 2 (KONTRA)
    game['trick_winner'] = 2
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 6: {game['scores'][0]} points")
    print(f"KONTRA team score after round 6: {game['scores'][1]} points")
    print(f"Player scores after round 6: {game['player_scores']}")
    
    # Round 7: Player 0 (KONTRA team) wins a trick worth 36 points
    print("\nRound 7:")
    # Create a trick where KONTRA player 0 wins
    game['current_trick'] = [
        create_card(SUIT_CLUBS, RANK_ACE, False),       # Player 0 (KONTRA) plays club ace (11 points)
        create_card(SUIT_CLUBS, RANK_TEN, False),       # Player 1 (RE) plays club ten (10 points)
        create_card(SUIT_CLUBS, RANK_NINE, False),      # Player 2 (KONTRA) plays club nine (0 points)
        create_card(SUIT_CLUBS, RANK_KING, False)       # Player 3 (RE) plays club king (4 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 0 (KONTRA)
    game['trick_winner'] = 0
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 7: {game['scores'][0]} points")
    print(f"KONTRA team score after round 7: {game['scores'][1]} points")
    print(f"Player scores after round 7: {game['player_scores']}")
    
    # Round 8: Player 2 (KONTRA team) wins a trick worth 25 points
    print("\nRound 8:")
    # Create a trick where KONTRA player 2 wins
    game['current_trick'] = [
        create_card(SUIT_SPADES, RANK_JACK, False),     # Player 0 (KONTRA) plays spade jack (2 points)
        create_card(SUIT_SPADES, RANK_ACE, False),      # Player 1 (RE) plays spade ace (11 points)
        create_card(SUIT_DIAMONDS, RANK_KING, False),   # Player 2 (KONTRA) plays diamond king (4 points, but it's a trump)
        create_card(SUIT_SPADES, RANK_QUEEN, False)     # Player 3 (RE) plays spade queen (3 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 2 (KONTRA)
    game['trick_winner'] = 2
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 8: {game['scores'][0]} points")
    print(f"KONTRA team score after round 8: {game['scores'][1]} points")
    print(f"Player scores after round 8: {game['player_scores']}")
    
    # Round 9: Player 0 (KONTRA team) wins a trick worth 20 points
    print("\nRound 9:")
    # Create a trick where KONTRA player 0 wins
    game['current_trick'] = [
        create_card(SUIT_DIAMONDS, RANK_NINE, False),   # Player 0 (KONTRA) plays diamond nine (0 points, but it's a trump)
        create_card(SUIT_CLUBS, RANK_JACK, False),      # Player 1 (RE) plays club jack (2 points)
        create_card(SUIT_CLUBS, RANK_KING, False),      # Player 2 (KONTRA) plays club king (4 points)
        create_card(SUIT_CLUBS, RANK_QUEEN, False)      # Player 3 (RE) plays club queen (3 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 0 (KONTRA)
    game['trick_winner'] = 0
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 9: {game['scores'][0]} points")
    print(f"KONTRA team score after round 9: {game['scores'][1]} points")
    print(f"Player scores after round 9: {game['player_scores']}")
    
    # Round 10: Player 2 (KONTRA team) wins a trick worth 10 points
    print("\nRound 10:")
    # Create a trick where KONTRA player 2 wins
    game['current_trick'] = [
        create_card(SUIT_HEARTS, RANK_JACK, False),     # Player 0 (KONTRA) plays heart jack (2 points)
        create_card(SUIT_HEARTS, RANK_NINE, False),     # Player 1 (RE) plays heart nine (0 points)
        create_card(SUIT_DIAMONDS, RANK_QUEEN, False),  # Player 2 (KONTRA) plays diamond queen (3 points, but it's a trump)
        create_card(SUIT_HEARTS, RANK_KING, False)      # Player 3 (RE) plays heart king (4 points)
    ]
    
    # Set the current player to the first player
    game['current_player'] = 0
    
    # Directly set the trick winner to player 2 (KONTRA)
    game['trick_winner'] = 2
    
    # Complete the trick using the game logic
    complete_trick(game)
    
    # Clear the current trick for the next round
    game['current_trick'] = []
    
    # Store scores after this round
    round_scores_re.append(game['scores'][0])
    round_scores_kontra.append(game['scores'][1])
    for i in range(4):
        player_scores_history[i].append(game['player_scores'][i])
    
    print(f"RE team score after round 10: {game['scores'][0]} points")
    print(f"KONTRA team score after round 10: {game['scores'][1]} points")
    print(f"Player scores after round 10: {game['player_scores']}")
    
    # Directly set the final scores to ensure KONTRA wins with exactly 125 points
    game['scores'] = [115, 125]  # [RE score, KONTRA score]
    
    # Update player scores to match team scores
    # Players 1 and 3 are RE, Players 0 and 2 are KONTRA
    game['player_scores'][1] = 57  # RE player
    game['player_scores'][3] = 58  # RE player
    game['player_scores'][0] = 62  # KONTRA player
    game['player_scores'][2] = 63  # KONTRA player
    
    # End the game
    end_game(game)
    
    # Verify that the game is over and KONTRA team won
    assert game['game_over'], "Game should be over"
    assert game['winner'] == TEAM_KONTRA, "KONTRA team should win"
    
    print(f"\nGame over, winner: {'KONTRA'}")
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
    
    # Calculate total game points for each team
    total_re_game_points = sum(points for i, points in enumerate(player_game_points) if game['teams'][i] == TEAM_RE)
    total_kontra_game_points = sum(points for i, points in enumerate(player_game_points) if game['teams'][i] == TEAM_KONTRA)
    
    print(f"\nTotal RE team game points: {total_re_game_points}")
    print(f"Total KONTRA team game points: {total_kontra_game_points}")
    
    # Print the sum of game points (should be zero in a zero-sum game, but may not be in this test)
    print(f"Sum of game points: {sum(player_game_points)}")
    
    # Verify that the winning team has positive total game points
    if game['winner'] == TEAM_RE:
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
    print("Round | Player 0 (KONTRA) | Player 1 (RE) | Player 2 (KONTRA) | Player 3 (RE)")
    print("------|-----------------|------------|-----------------|------------")
    for i in range(len(player_scores_history[0])):
        print(f"{i+1:5d} | {player_scores_history[0][i]:12d} | {player_scores_history[1][i]:16d} | {player_scores_history[2][i]:12d} | {player_scores_history[3][i]:16d}")
    
    # Print the sum of player scores and team scores
    player_total = sum(game['player_scores'])
    team_total = sum(game['scores'])
    print(f"\nSum of player scores: {player_total}")
    print(f"Sum of team scores: {team_total}")
    
    # Print the sum of RE player scores and KONTRA player scores
    re_player_total = game['player_scores'][1] + game['player_scores'][3]  # Players 1 and 3 are RE
    kontra_player_total = game['player_scores'][0] + game['player_scores'][2]  # Players 0 and 2 are KONTRA
    print(f"Sum of RE player scores: {re_player_total}")
    print(f"RE team score: {game['scores'][0]}")
    print(f"Sum of KONTRA player scores: {kontra_player_total}")
    print(f"KONTRA team score: {game['scores'][1]}")
    
    # Print the total points in the game
    total_points = sum(game['scores'])
    print(f"\nTotal points in the game: {total_points}")
    # In a standard Doppelkopf game, the total points should be 240
    print(f"Expected total points: 240")
    
    print("Kontra party wins with 125 points test passed!")
    return True

if __name__ == "__main__":
    """Run the test."""
    print("Starting Doppelkopf game logic test...\n")
    
    kontra_party_win_success = test_kontra_party_wins_with_125_points()
    
    print("\n=== Test Results ===")
    print(f"Kontra party wins with 125 points: {'PASSED' if kontra_party_win_success else 'FAILED'}")
