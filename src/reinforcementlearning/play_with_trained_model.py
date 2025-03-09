#!/usr/bin/env python3
"""
Play Doppelkopf with a trained AI model.
This script plays a game of Doppelkopf with a trained AI model against random agents.
"""

import os
import sys
import time

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent
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
    # Check if the model file exists
    model_path = "models/final_model.pt"
    if not os.path.exists(model_path):
        print(f"Model file {model_path} not found. Please train a model first.")
        return
    
    # Initialize game
    game = DoppelkopfGame()
    
    # Reset the game
    game.reset()
    
    # RL agent is always player 0
    rl_player_idx = 0
    
    # Initialize RL agent
    rl_agent = RLAgent(
        state_size=game.get_state_size(),
        action_size=game.get_action_size()
    )
    
    # Load the trained model
    rl_agent.load(model_path)
    print(f"Loaded model from {model_path}")
    
    # Set epsilon to a small value for evaluation
    rl_agent.epsilon = 0.05
    
    # Set the game variant to normal for all players
    for player_idx in range(game.num_players):
        game.set_variant('normal', player_idx)
    
    print("Starting a game of Doppelkopf with the trained AI...")
    
    # Play until the game is over
    while not game.game_over:
        # Print the game state
        print_game_state(game)
        
        # Get the current player
        current_player = game.current_player
        
        # Get action
        if current_player == rl_player_idx:
            # RL agent's turn
            action_result = rl_agent.select_action(game, current_player)
            
            # If no action was selected or the action is not valid
            if not action_result or not isinstance(action_result, tuple) or len(action_result) != 2:
                # Select a random legal action
                legal_actions = game.get_legal_actions(current_player)
                if legal_actions:
                    action = legal_actions[0]  # Just take the first legal action
                    action_type = 'card'
                else:
                    # No legal actions, this shouldn't happen
                    print(f"No legal actions for player {current_player}!")
                    break
            else:
                action_type, action = action_result
            
            if action_type == 'card':
                print(f"RL Agent plays: {print_card(action)}")
                
                # Play the card
                game.play_card(current_player, action)
        else:
            # Opponent's turn
            action = select_random_action(game, current_player)
            
            if action is None:
                # If the action is invalid, select a random legal action
                legal_actions = game.get_legal_actions(current_player)
                if legal_actions:
                    action = legal_actions[0]  # Just take the first legal action
                else:
                    # No legal actions, this shouldn't happen
                    print(f"No legal actions for player {current_player}!")
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
                player_name = "RL Agent" if player_idx == rl_player_idx else f"Player {player_idx}"
                print(f"{player_name} played: {print_card(card)}")
            
            winner_name = "RL Agent" if winner == rl_player_idx else f"Player {winner}"
            print(f"\n{winner_name} won the trick!")
            
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
        player_name = "RL Agent" if i == rl_player_idx else f"Player {i}"
        print(f"{player_name} was on team {team}")
    
    # Check if the RL agent's team won
    rl_team = game.teams[rl_player_idx]
    if rl_team == winning_team:
        print("\nThe RL Agent's team won!")
    else:
        print("\nThe RL Agent's team lost.")

if __name__ == "__main__":
    main()
