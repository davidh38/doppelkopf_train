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
    return parser.parse_args()

# Get command line arguments
args = parse_arguments()
MODEL_PATH = args.model

# Configure Flask paths
TEMPLATE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates'))
STATIC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/static'))
