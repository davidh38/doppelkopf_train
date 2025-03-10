#!/usr/bin/env python3
"""
Main test runner for the Doppelkopf game.
This script runs all the tests in the tests folder.
"""

import unittest
import sys
import os

# Add the parent directory to the path so that the tests can import modules from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the test modules
from tests.test_game_logic import test_team_reveal, test_score_calculation, test_re_party_wins_with_125_points
from tests.test_kontra_wins import test_kontra_party_wins_with_125_points
from tests.test_jack_solo_re_win import test_jack_solo_re_win
from tests.test_re_team_wins import test_re_party_wins_with_125_points as test_re_team_wins

def run_all_tests():
    """Run all the tests."""
    print("Starting Doppelkopf game logic tests...\n")
    
    # Run the tests
    team_reveal_success = test_team_reveal()
    score_calculation_success = test_score_calculation()
    re_party_win_success = test_re_party_wins_with_125_points()
    kontra_party_win_success = test_kontra_party_wins_with_125_points()
    jack_solo_re_win_success = test_jack_solo_re_win()
    re_team_win_success = test_re_team_wins()
    
    
    # Print the results
    print("\n=== Test Results ===")
    print(f"Team reveal logic: {'PASSED' if team_reveal_success else 'FAILED'}")
    print(f"Score calculation logic: {'PASSED' if score_calculation_success else 'FAILED'}")
    print(f"Re party wins with 125 points: {'PASSED' if re_party_win_success else 'FAILED'}")
    print(f"Kontra party wins with 125 points: {'PASSED' if kontra_party_win_success else 'FAILED'}")
    print(f"Jack Solo with RE announcement and win: {'PASSED' if jack_solo_re_win_success else 'FAILED'}")
    print(f"RE team wins test: {'PASSED' if re_team_win_success else 'FAILED'}")
    # Overall result
    all_passed = (team_reveal_success and score_calculation_success and 
                 re_party_win_success and kontra_party_win_success and 
                 jack_solo_re_win_success and re_team_win_success)
    print(f"All tests: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    """Run the tests."""
    success = run_all_tests()
    sys.exit(0 if success else 1)  # Exit with 0 if all tests passed, 1 otherwise
