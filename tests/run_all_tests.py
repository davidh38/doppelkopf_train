#!/usr/bin/env python3
"""
Main test runner for the Doppelkopf game.
This script runs all the tests in the tests folder.
"""

import unittest
import sys
import os
import argparse

# Add the parent directory to the path so that the tests can import modules from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the test modules for the legacy function-based tests
from tests.test_game_logic import test_team_reveal, test_score_calculation, test_re_party_wins_with_125_points
from tests.test_kontra_wins import test_kontra_party_wins_with_125_points
from tests.test_jack_solo_re_win import test_jack_solo_re_win
from tests.test_re_team_wins import test_re_party_wins_with_125_points as test_re_team_wins
from tests.test_card_giver_turn import test_player_turn_after_card_dealing

# Import unittest-based test modules
from tests.test_play_with_trained_model import TestPlayWithTrainedModel

def run_legacy_tests():
    """Run the legacy function-based tests."""
    print("Starting legacy Doppelkopf game logic tests...\n")
    
    # Run the tests
    team_reveal_success = test_team_reveal()
    score_calculation_success = test_score_calculation()
    re_party_win_success = test_re_party_wins_with_125_points()
    kontra_party_win_success = test_kontra_party_wins_with_125_points()
    jack_solo_re_win_success = test_jack_solo_re_win()
    re_team_win_success = test_re_team_wins()
    card_giver_turn_success = test_player_turn_after_card_dealing()
    
    # Print the results
    print("\n=== Legacy Test Results ===")
    print(f"Team reveal logic: {'PASSED' if team_reveal_success else 'FAILED'}")
    print(f"Score calculation logic: {'PASSED' if score_calculation_success else 'FAILED'}")
    print(f"Re party wins with 125 points: {'PASSED' if re_party_win_success else 'FAILED'}")
    print(f"Kontra party wins with 125 points: {'PASSED' if kontra_party_win_success else 'FAILED'}")
    print(f"Jack Solo with RE announcement and win: {'PASSED' if jack_solo_re_win_success else 'FAILED'}")
    print(f"RE team wins test: {'PASSED' if re_team_win_success else 'FAILED'}")
    print(f"Card giver turn test: {'PASSED' if card_giver_turn_success else 'FAILED'}")
    # Overall result
    all_passed = (team_reveal_success and score_calculation_success and 
                 re_party_win_success and kontra_party_win_success and 
                 jack_solo_re_win_success and re_team_win_success and
                 card_giver_turn_success)
    print(f"All legacy tests: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

def run_unittest_tests():
    """Run the unittest-based tests."""
    print("\nStarting unittest-based tests...\n")
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add the test cases
    suite.addTest(loader.loadTestsFromTestCase(TestPlayWithTrainedModel))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Check if all tests passed
    all_passed = result.wasSuccessful()
    print(f"\nAll unittest tests: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

def run_all_tests(skip_model_tests=False):
    """Run all the tests."""
    print("Starting Doppelkopf game logic tests...\n")
    
    # Run the legacy tests
    legacy_success = run_legacy_tests()
    
    # Run the unittest tests if not skipped
    if skip_model_tests:
        print("\nSkipping model-based tests as requested.")
        unittest_success = True
    else:
        unittest_success = run_unittest_tests()
    
    # Overall result
    all_passed = legacy_success and unittest_success
    print(f"\n=== Overall Test Results ===")
    print(f"All tests: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    """Run the tests."""
    parser = argparse.ArgumentParser(description='Run Doppelkopf game tests')
    parser.add_argument('--skip-model-tests', action='store_true',
                        help='Skip tests that require trained models')
    args = parser.parse_args()
    
    success = run_all_tests(skip_model_tests=args.skip_model_tests)
    sys.exit(0 if success else 1)  # Exit with 0 if all tests passed, 1 otherwise
