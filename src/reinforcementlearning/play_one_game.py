#!/usr/bin/env python3
"""
Play a single game of Doppelkopf with random agents.
This script plays a single game of Doppelkopf with random agents and prints the results.
"""

import os
import sys
import time

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.backend.game.doppelkopf import VARIANT_NORMAL, TEAM_RE, TEAM_KONTRA

def print_card(card):
    """Print a card in a readable format."""
    return f"{card['rank']} of {card['suit']}"

def print_game_state(game):
    """Print the current state of the game."""
    print("\n" + "=" * 50)
    print(f"Current player: {game.current_player}")
    
    print("\nCurrent trick:")
    if game.current_trick:
        for i, card in enumerate(game.current_trick):
            print(f"{i}: {print_card(card)}")
    else:
        print("No cards played yet")
    
    print("\nPlayer hands:")
    for i, hand in enumerate(game.hands):
        print(f"Player {i}: {len(hand)} cards")
        if i == 0:  # Show the first player's hand for debugging
            for j, card in enumerate(hand):
                print(f"  {j}: {print_card(card)}")
    
    print(f"\nScores - RE: {game.scores[0]}, KONTRA: {game.scores[1]}")
    print(f"Teams - {[game.teams[i] for i in range(game.num_players)]}")
    print("=" * 50)

def main():
    """Main function to run the game."""
    # Initialize game
    game = DoppelkopfGame()
    
    # Reset the game
    game.reset()
    
    # Set the game variant to normal for all players
    for player_idx in range(game.num_players):
        game.set_variant('normal', player_idx)
    
    print("Starting a game of Doppelkopf with random agents...")
    
    # Play until the game is over
    while not game.game_over:
        # Print the game state
        print_game_state(game)
        
        # Get the current player
        current_player = game.current_player
        
        # Get legal actions for the current player
        legal_actions = game.get_legal_actions(current_player)
        
        # Select a random action
        action = select_random_action(game, current_player)
        
        if action is None:
            print(f"Player {current_player} has no legal actions!")
            break
        
        print(f"Player {current_player} plays: {print_card(action)}")
        
        # Play the card
        game.play_card(current_player, action)
        
        # If a trick was completed, show the completed trick and who won
        if game.trick_winner is not None:
            winner = game.trick_winner
            
            # Get the completed trick (it's stored in the tricks list)
            completed_trick = game.tricks[-1]
            
            print("\nCompleted trick:")
            for i, card in enumerate(completed_trick):
                player_idx = (game.current_player - len(completed_trick) + i) % game.num_players
                print(f"Player {player_idx} played: {print_card(card)}")
            
            print(f"\nPlayer {winner} won the trick!")
            
            # Small delay to make it easier to follow
            time.sleep(1)
    
    # Game over, show results
    print("\nGame over!")
    print(f"Final scores - RE: {game.scores[0]}, KONTRA: {game.scores[1]}")
    
    # Determine the winning team
    if game.scores[0] > game.scores[1]:
        winning_team = TEAM_RE
    else:
        winning_team = TEAM_KONTRA
    
    print(f"Team {winning_team} wins!")
    
    # Show which players were on which team
    for i in range(game.num_players):
        team = "RE" if game.teams[i] == TEAM_RE else "KONTRA"
        print(f"Player {i} was on team {team}")

if __name__ == "__main__":
    main()
