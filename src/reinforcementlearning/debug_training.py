#!/usr/bin/env python3
"""
Debug training for Doppelkopf AI.
This script runs a single episode of training with detailed logging to help identify issues.
"""

import os
import sys
import time
import traceback

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent
from src.reinforcementlearning.training.trainer import calculate_reward
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

def debug_train_episode(game, rl_agent, opponents):
    """
    Train for one episode with detailed debugging.
    
    Args:
        game: The game instance
        rl_agent: The RL agent to train
        opponents: List of opponent agents
        
    Returns:
        Tuple of (total reward for the RL agent, whether the RL agent's team won)
    """
    print("Starting debug training episode...")
    
    try:
        # Reset the game
        print("Resetting game...")
        game.reset()
        
        # RL agent is always player 0
        rl_player_idx = 0
        
        # Set the game variant to normal for all players
        print("Setting game variant to normal...")
        for player_idx in range(game.num_players):
            game.set_variant('normal', player_idx)
        
        # Track the total reward for the RL agent
        total_reward = 0
        
        # Print initial game state
        print("\nInitial game state:")
        print_game_state(game)
        
        # Play until the game is over
        trick_count = 0
        card_count = 0
        
        print("\nStarting game loop...")
        while not game.game_over:
            current_player = game.current_player
            print(f"\nCurrent player: {current_player}")
            
            # Get action
            if current_player == rl_player_idx:
                print("RL agent's turn...")
                
                # Get state before action
                state = game.get_state_for_player(current_player)
                print(f"State type: {type(state)}, State length: {len(state)}")
                
                # Select an action
                print("Selecting action...")
                action_result = rl_agent.select_action(game, current_player)
                
                # If no action was selected or the action is not valid
                if not action_result or not isinstance(action_result, tuple) or len(action_result) != 2:
                    print("No valid action selected, choosing first legal action...")
                    # Select a random legal action
                    legal_actions = game.get_legal_actions(current_player)
                    if legal_actions:
                        action = legal_actions[0]  # Just take the first legal action
                        action_type = 'card'
                    else:
                        # No legal actions, this shouldn't happen
                        print(f"ERROR: No legal actions for player {current_player}!")
                        break
                else:
                    action_type, action = action_result
                
                print(f"Selected action: {action_type}, {print_card(action) if action_type == 'card' else action}")
                
                if action_type == 'card':
                    # Play the card
                    print(f"Playing card: {print_card(action)}")
                    card_count += 1
                    
                    # Check if the action is legal
                    legal_actions = game.get_legal_actions(current_player)
                    legal_action_found = False
                    for legal_action in legal_actions:
                        if legal_action['suit'] == action['suit'] and legal_action['rank'] == action['rank']:
                            legal_action_found = True
                            break
                    
                    if not legal_action_found:
                        print(f"WARNING: Selected action {print_card(action)} is not in legal actions!")
                        print("Legal actions:")
                        for i, legal_action in enumerate(legal_actions):
                            print(f"  {i}: {print_card(legal_action)}")
                        
                        # Use a legal action instead
                        if legal_actions:
                            action = legal_actions[0]
                            print(f"Using legal action instead: {print_card(action)}")
                    
                    # Play the card
                    result = game.play_card(current_player, action)
                    if not result:
                        print(f"ERROR: Failed to play card {print_card(action)}!")
                        break
                    
                    # Get state after action
                    next_state = game.get_state_for_player(current_player)
                    
                    # Calculate reward
                    reward = calculate_reward(game, current_player, 'card')
                    print(f"Reward: {reward}")
                    
                    # Convert the card to an action index for the RL agent
                    action_idx = game.card_to_idx(action)
                    
                    # Observe the action and train
                    print("Observing action and training...")
                    rl_agent.observe_action(state, action_idx, next_state, reward, 'card')
                    rl_agent.train()
                    
                    total_reward += reward
            else:
                # Opponent's turn
                print(f"Opponent {current_player}'s turn...")
                opponent_idx = current_player - 1 if current_player > rl_player_idx else current_player
                
                # Get legal actions
                legal_actions = game.get_legal_actions(current_player)
                if not legal_actions:
                    print(f"ERROR: No legal actions for opponent {current_player}!")
                    break
                
                # Select a random action
                action = select_random_action(game, current_player)
                
                if action is None:
                    # If the action is invalid, select a random legal action
                    print("No valid action selected, choosing first legal action...")
                    if legal_actions:
                        action = legal_actions[0]  # Just take the first legal action
                    else:
                        # No legal actions, this shouldn't happen
                        print(f"ERROR: No legal actions for player {current_player}!")
                        break
                
                print(f"Opponent plays: {print_card(action)}")
                card_count += 1
                
                # Play the card
                result = game.play_card(current_player, action)
                if not result:
                    print(f"ERROR: Failed to play card {print_card(action)}!")
                    break
            
            # If a trick was completed, show the completed trick and who won
            if len(game.current_trick) == 0 and len(game.tricks) > trick_count:
                trick_count += 1
                winner = game.trick_winner
                
                # Get the completed trick (it's stored in the tricks list)
                completed_trick = game.tricks[-1]
                
                print("\nCompleted trick:")
                for i, card in enumerate(completed_trick):
                    print(f"  {i}: {print_card(card)}")
                
                print(f"Player {winner} won the trick!")
            
            # Print current game state
            print_game_state(game)
        
        # Game over, check if the RL agent's team won
        print("\nGame over!")
        rl_team = game.teams[rl_player_idx]
        win = game.winner == rl_team
        
        # Get the player's team index
        team_idx = 0 if rl_team == TEAM_RE else 1
        
        # Calculate score difference
        score_diff = game.scores[team_idx] - game.scores[1 - team_idx]
        
        # Add a reward based on score difference
        score_reward = score_diff / 10.0  # Scale appropriately
        
        # Add a bonus for winning
        win_bonus = 5 if win else -5
        
        # Total end-game reward
        end_game_reward = score_reward + win_bonus
        total_reward += end_game_reward
        
        print(f"Final scores - RE: {game.scores[0]}, KONTRA: {game.scores[1]}")
        print(f"RL Agent's Team: {'RE' if rl_team == TEAM_RE else 'KONTRA'}")
        print(f"Win: {win}, Total Reward: {total_reward:.2f}")
        
        return total_reward, win
    
    except Exception as e:
        print(f"ERROR: Exception occurred during training: {e}")
        print(traceback.format_exc())
        return 0, False

def main():
    """Main function to run the debug training."""
    # Initialize game
    game = DoppelkopfGame()
    
    # Initialize RL agent
    rl_agent = RLAgent(
        state_size=game.get_state_size(),
        action_size=game.get_action_size(),
        learning_rate=0.0005,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.05,
        epsilon_decay=0.9
    )
    
    # Other players are random agents
    opponents = [select_random_action for _ in range(3)]
    
    print("Starting debug training for 1 episode...")
    
    # Train for one episode
    episode_reward, episode_win = debug_train_episode(game, rl_agent, opponents)
    
    print("\nDebug training completed!")
    print(f"Episode Reward: {episode_reward:.2f}")
    print(f"Episode Win: {episode_win}")

if __name__ == "__main__":
    main()
