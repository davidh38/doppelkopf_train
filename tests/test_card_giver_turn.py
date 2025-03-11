#!/usr/bin/env python3
"""
Test script to verify the player turn after card dealing in the Doppelkopf game.
"""

import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.game.doppelkopf import (
    create_game_state, set_variant, TEAM_RE, TEAM_KONTRA
)

def test_player_turn_after_card_dealing():
    """Test to verify which player's turn it is after the card giver deals the cards."""
    print("\n=== Testing Player Turn After Card Dealing ===")
    
    # Create a new game with a controlled setup
    game = create_game_state()
    
    # Set the card giver to player 0 (representing the user)
    game['card_giver'] = 0
    
    print(f"Card giver: Player {game['card_giver']}")
    print(f"Current player before variant selection: Player {game['current_player']}")
    
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
    
    # Print the teams
    print("Teams:")
    for i, team in enumerate(game['teams']):
        print(f"Player {i}: {'RE' if team == TEAM_RE else 'KONTRA'}")
    
    # After variant selection, the current player should be the player next to the card giver
    expected_current_player = (game['card_giver'] + 1) % game['num_players']
    print(f"Expected current player after variant selection: Player {expected_current_player}")
    print(f"Actual current player after variant selection: Player {game['current_player']}")
    
    assert game['current_player'] == expected_current_player, f"Current player should be {expected_current_player}, but is {game['current_player']}"
    
    print("Player turn after card dealing test passed!")
    return True

if __name__ == "__main__":
    """Run the test."""
    print("Starting Doppelkopf game logic test...\n")
    
    player_turn_success = test_player_turn_after_card_dealing()
    
    print("\n=== Test Results ===")
    print(f"Player turn after card dealing: {'PASSED' if player_turn_success else 'FAILED'}")
