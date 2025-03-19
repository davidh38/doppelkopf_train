#!/usr/bin/env python3
"""
Configuration for the Doppelkopf web application.
"""

import os
import argparse
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Global game state (in a real application, you'd use a database or session management)
games = {}

# Global scoreboard to track wins and player scores
scoreboard = {
    'player_wins': 0,
    'ai_wins': 0,
    'player_scores': [0, 0, 0, 0],  # Individual scores for all 4 players
    'last_starting_player': 0  # Track the last player who started a game
}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Doppelkopf web app with a trained model')
    parser.add_argument('--model', type=str, default='models/final_model.pt',
                        help='Path to a trained model')
    parser.add_argument('--port', type=int, default=5007,
                        help='Port to run the server on')
    parser.add_argument('--human', type=int, default=1,
                        help='Number of human players (1-4)')
    parser.add_argument('--human-settings', type=str, default='first',
                        help='Where to place human player(s): "first" or "random" (default: first)')
    args = parser.parse_args()
    
    # Validate human players argument
    if not 1 <= args.human <= 4:
        parser.error('Number of human players must be between 1 and 4')
    
    # Validate human-settings argument
    if args.human_settings not in ['first', 'random']:
        parser.error('Human-settings must be either "first" or "random"')
        
    return args

# Parse and validate command line arguments
args = parse_arguments()
MODEL_PATH = args.model

# Configure Flask paths
TEMPLATE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates'))
STATIC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/static'))
