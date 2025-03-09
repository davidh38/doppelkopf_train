#!/usr/bin/env python3
"""
Train a Doppelkopf AI with progress reporting.
This script trains an AI to play Doppelkopf and reports progress after each episode.
"""

import os
import sys
import time

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent
from src.reinforcementlearning.training.trainer import calculate_reward
from src.backend.game.doppelkopf import VARIANT_NORMAL, TEAM_RE, TEAM_KONTRA

def train_episode(game, rl_agent, opponents, episode_num):
    """
    Train for one episode and report progress.
    
    Args:
        game: The game instance
        rl_agent: The RL agent to train
        opponents: List of opponent agents
        episode_num: The current episode number
        
    Returns:
        Tuple of (total reward for the RL agent, whether the RL agent's team won)
    """
    # Reset the game
    game.reset()
    
    # RL agent is always player 0
    rl_player_idx = 0
    
    # Set the game variant to normal for all players
    for player_idx in range(game.num_players):
        game.set_variant('normal', player_idx)
    
    # Track the total reward for the RL agent
    total_reward = 0
    
    # Play until the game is over
    while not game.game_over:
        current_player = game.current_player
        
        # Get action
        if current_player == rl_player_idx:
            # RL agent's turn
            # Select an action
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
            
            # Get state before action
            state = game.get_state_for_player(current_player)
            
            if action_type == 'card':
                # Play the card
                game.play_card(current_player, action)
                
                # Get state after action
                next_state = game.get_state_for_player(current_player)
                
                # Calculate reward
                reward = calculate_reward(game, current_player, 'card')
                
                # Convert the card to an action index for the RL agent
                action_idx = game.card_to_idx(action)
                
                # Observe the action and train
                rl_agent.observe_action(state, action_idx, next_state, reward, 'card')
                rl_agent.train()
                
                total_reward += reward
        else:
            # Opponent's turn
            opponent_idx = current_player - 1 if current_player > rl_player_idx else current_player
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
            
            # Play the card
            game.play_card(current_player, action)
    
    # Check if the RL agent's team won
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
    
    # Print progress
    print(f"Episode {episode_num} completed - Score: {game.scores[0]}-{game.scores[1]}, " +
          f"Winner: {'RE' if game.winner == TEAM_RE else 'KONTRA'}, " +
          f"RL Agent's Team: {'RE' if rl_team == TEAM_RE else 'KONTRA'}, " +
          f"Win: {win}, Reward: {total_reward:.2f}")
    
    return total_reward, win

def main():
    """Main function to run the training."""
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
    
    # Number of episodes to train
    num_episodes = 10
    
    print(f"Starting training for {num_episodes} episodes...")
    
    # Training statistics
    episode_rewards = []
    episode_wins = []
    
    # Train for the specified number of episodes
    for episode in range(1, num_episodes + 1):
        # Train for one episode
        episode_reward, episode_win = train_episode(game, rl_agent, opponents, episode)
        
        # Record statistics
        episode_rewards.append(episode_reward)
        episode_wins.append(episode_win)
    
    # Calculate and print final statistics
    avg_reward = sum(episode_rewards) / len(episode_rewards)
    win_rate = sum(episode_wins) / len(episode_wins)
    
    print("\nTraining completed!")
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Win Rate: {win_rate:.2f}")
    
    # Save the final model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    final_model_path = os.path.join(model_dir, "final_model.pt")
    rl_agent.save(final_model_path)
    print(f"Saved final model to {final_model_path}")

if __name__ == "__main__":
    main()
