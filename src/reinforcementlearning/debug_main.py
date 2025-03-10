#!/usr/bin/env python3
"""
Debug version of the Doppelkopf AI Training Program
This program implements a reinforcement learning approach to train an AI to play Doppelkopf
with additional debugging information.
"""

import argparse
import os
import sys
import time
import traceback

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent
import src.reinforcementlearning.training.trainer as trainer
import src.backend.utils.logger as logger

def debug_train(game, rl_agent, opponents, num_episodes=1):
    """
    Debug version of the training function.
    
    Args:
        game: The game instance
        rl_agent: The RL agent to train
        opponents: List of opponent agents
        num_episodes: Number of episodes to train for
    """
    print("Starting debug training...")
    
    try:
        # Ensure we have the right number of opponents
        assert len(opponents) == game.num_players - 1, \
            f"Expected {game.num_players - 1} opponents, got {len(opponents)}"
        
        print(f"Training for {num_episodes} episodes")
        
        # Training statistics
        episode_rewards = []
        episode_wins = []
        
        for episode in range(1, num_episodes + 1):
            print(f"Episode {episode}/{num_episodes}")
            
            # Reset the game
            print("Resetting game...")
            game.reset()
            
            # Play one episode
            print("Playing episode...")
            episode_reward, episode_win = debug_play_episode(game, rl_agent, opponents)
            
            # Record statistics
            episode_rewards.append(episode_reward)
            episode_wins.append(episode_win)
            
            # Log progress
            avg_reward = sum(episode_rewards) / len(episode_rewards)
            win_rate = sum(episode_wins) / len(episode_wins)
            print(f"Episode {episode}/{num_episodes} - "
                      f"Reward: {episode_reward:.2f}, "
                      f"Win: {episode_win}, "
                      f"Avg Reward: {avg_reward:.2f}, "
                      f"Win Rate: {win_rate:.2f}")
        
        print("Training completed!")
        
    except Exception as e:
        print(f"ERROR: Exception occurred during training: {e}")
        print(traceback.format_exc())

def debug_play_episode(game, rl_agent, opponents):
    """
    Debug version of play_episode.
    
    Args:
        game: The game instance
        rl_agent: The RL agent
        opponents: List of opponent agents
        
    Returns:
        Tuple of (total reward for the RL agent, whether the RL agent's team won)
    """
    # RL agent is always player 0
    rl_player_idx = 0
    
    # Track the total reward for the RL agent
    total_reward = 0
    
    # Add variant selection phase flag to the game
    game.variant_selection_phase = True
    
    print("Starting variant selection phase...")
    
    # First, select game variant (only for player 0)
    if rl_player_idx == 0:
        print("RL agent selecting variant...")
        
        # Get the current state
        state = game.get_state_for_player(rl_player_idx)
        print(f"State type: {type(state)}, State length: {len(state)}")
        
        # Select a variant action
        print("Selecting action...")
        action_result = rl_agent.select_action(game, rl_player_idx)
        
        if action_result and action_result[0] == 'variant':
            action_type, variant = action_result
            print(f"Selected variant: {variant}")
            
            # Set the game variant
            from src.backend.game.doppelkopf import VARIANT_NORMAL, VARIANT_HOCHZEIT, VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_FLESHLESS
            if variant == 'normal':
                game.game_variant = VARIANT_NORMAL
            elif variant == 'hochzeit':
                game.game_variant = VARIANT_HOCHZEIT
            elif variant == 'queen_solo':
                game.game_variant = VARIANT_QUEEN_SOLO
            elif variant == 'jack_solo':
                game.game_variant = VARIANT_JACK_SOLO
            elif variant == 'fleshless':
                game.game_variant = VARIANT_FLESHLESS
            
            # Get the next state
            next_state = game.get_state_for_player(rl_player_idx)
            
            # Calculate reward for variant selection
            reward = trainer.calculate_reward(game, rl_player_idx, 'variant', variant)
            print(f"Variant selection reward: {reward}")
            
            # Observe the action and train
            print("Observing action and training...")
            rl_agent.observe_action(state, variant, next_state, reward, 'variant')
            rl_agent.train()
            total_reward += reward
    
    # End variant selection phase
    game.variant_selection_phase = False
    
    # Track announcements to avoid duplicates
    re_announced = False
    contra_announced = False
    
    print("Starting card play phase...")
    
    # Play until the game is over
    trick_count = 0
    card_count = 0
    
    while not game.game_over:
        current_player = game.current_player
        
        # Get the current state
        state = game.get_state_for_player(current_player)
        
        # Log current game state
        if len(game.current_trick) == 0:
            trick_count += 1
            print(f"Starting trick #{trick_count}")
        
        # Select an action
        if current_player == rl_player_idx:
            print(f"RL agent (player {current_player}) selecting action...")
            action_result = rl_agent.select_action(game, current_player)
            
            # Handle different action types
            if action_result and isinstance(action_result, tuple) and len(action_result) == 2:
                action_type, action = action_result
                
                if action_type == 'card':
                    # Log card play
                    card_count += 1
                    print(f"RL agent plays card #{card_count}: {action}")
                    
                    # Play the card
                    result = game.play_card(current_player, action)
                    if not result:
                        print(f"ERROR: Failed to play card {action}!")
                        break
                    
                    # Convert the card to an action index for the RL agent
                    action_idx = game.card_to_idx(action)
                    
                    # Get the next state
                    next_state = game.get_state_for_player(current_player)
                    
                    # Calculate reward for playing a card
                    reward = trainer.calculate_reward(game, current_player, 'card')
                    print(f"Card play reward: {reward}")
                    
                    # Observe the action and train
                    print("Observing action and training...")
                    rl_agent.observe_action(state, action_idx, next_state, reward, 'card')
                    rl_agent.train()
                    total_reward += reward
                
                elif action_type == 'announce':
                    print(f"RL agent makes announcement: {action}")
                    
                    # Make the announcement
                    if action == 're' and not re_announced:
                        re_announced = True
                        # In a real game, this would trigger the re announcement
                        # For training, we just track it
                        
                        # Get the next state (same as current since announcement doesn't change game state)
                        next_state = state
                        
                        # Calculate reward for making an announcement
                        reward = trainer.calculate_reward(game, current_player, 'announce', 're')
                        print(f"Announcement reward: {reward}")
                        
                        # Observe the action and train
                        print("Observing action and training...")
                        rl_agent.observe_action(state, 're', next_state, reward, 'announce')
                        rl_agent.train()
                        total_reward += reward
                    
                    elif action == 'contra' and not contra_announced:
                        contra_announced = True
                        # In a real game, this would trigger the contra announcement
                        # For training, we just track it
                        
                        # Get the next state (same as current since announcement doesn't change game state)
                        next_state = state
                        
                        # Calculate reward for making an announcement
                        reward = trainer.calculate_reward(game, current_player, 'announce', 'contra')
                        print(f"Announcement reward: {reward}")
                        
                        # Observe the action and train
                        print("Observing action and training...")
                        rl_agent.observe_action(state, 'contra', next_state, reward, 'announce')
                        rl_agent.train()
                        total_reward += reward
            
        else:
            # Opponent's turn - they only play cards, no announcements
            opponent_idx = current_player - 1  # Adjust for the RL agent
            print(f"Opponent {opponent_idx} (player {current_player}) selecting action...")
            action = select_opponent_action(opponents[opponent_idx], game, current_player)
            
            # Log card play
            card_count += 1
            print(f"Opponent plays card #{card_count}: {action}")
            
            # Play the card
            result = game.play_card(current_player, action)
            if not result:
                print(f"ERROR: Failed to play card {action}!")
                break
    
    # Check if the RL agent's team won
    rl_team = game.teams[rl_player_idx]
    win = game.winner == rl_team
    
    # Get the player's team index
    team_idx = 0 if rl_team == trainer.TEAM_RE else 1
    
    # Calculate score difference
    score_diff = game.scores[team_idx] - game.scores[1 - team_idx]
    
    # Add a reward based on score difference
    # This encourages maximizing the score difference, not just winning
    score_reward = score_diff / 10.0  # Scale appropriately
    
    # Still give a bonus for winning, but make it smaller compared to score difference
    win_bonus = 5 if win else -5
    
    # Total end-game reward
    end_game_reward = score_reward + win_bonus
    total_reward += end_game_reward
    
    # Log game end
    winner_team = "RE" if game.winner == trainer.TEAM_RE else "KONTRA"
    print(f"Game over! {winner_team} team wins with score {score_diff}. RL agent reward: {total_reward:.2f}")
    
    return total_reward, win

def select_opponent_action(opponent, game, player_idx):
    """
    Select an action for an opponent.
    
    Args:
        opponent: The opponent agent
        game: The game instance
        player_idx: Index of the player
        
    Returns:
        The selected action
    """
    # Handle both class-based and function-based opponents
    if hasattr(opponent, 'select_action'):
        return opponent.select_action(game, player_idx)
    else:
        # Assume it's a function like select_random_action
        return opponent(game, player_idx)

def main():
    """Main function to run the debug training program."""
    parser = argparse.ArgumentParser(description='Debug training for Doppelkopf AI')
    parser.add_argument('--episodes', type=int, default=1,
                        help='Number of episodes to train for')
    args = parser.parse_args()
    
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
    
    # Train the agent
    debug_train(game, rl_agent, opponents, args.episodes)

if __name__ == "__main__":
    main()
