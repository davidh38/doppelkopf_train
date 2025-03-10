#!/usr/bin/env python3
"""
Doppelkopf AI Training Program
This program implements a reinforcement learning approach to train an AI to play Doppelkopf.
"""

import os
import sys
import time
import numpy as np
import argparse
import random
from typing import List, Dict, Any, Tuple

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import src.backend.utils.logger as logger
from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.rl_agent import RLAgent
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.backend.game.doppelkopf import TEAM_RE, TEAM_KONTRA

def print_card(card):
    """Print a card in a readable format."""
    return f"{card['rank']} of {card['suit']}"

def print_game_state(game, episode_num, trick_num):
    """Print the current state of the game."""
    print(f"\n{'='*20} Episode {episode_num} - Trick {trick_num} {'='*20}")
    print(f"Current player: {game.current_player}")
    
    print("\nCurrent trick:")
    if game.current_trick:
        for i, card in enumerate(game.current_trick):
            print(f"{i}: {print_card(card)}")
    else:
        print("No cards played yet")
    
    print(f"\nScores - RE: {game.scores[0]}, KONTRA: {game.scores[1]}")
    print(f"Teams - {[game.teams[i] for i in range(game.num_players)]}")

def train(model_dir: str, episodes: int = 10, verbose: bool = False, 
          learning_rate: float = 0.001, gamma: float = 0.99,
          epsilon_start: float = 1.0, epsilon_end: float = 0.05, epsilon_decay: float = 0.9995):
    """
    Train the RL agent for the specified number of episodes.
    
    Args:
        model_dir: Directory to save models
        episodes: Number of episodes to train for
        verbose: Whether to print detailed game information
        learning_rate: Learning rate for the optimizer
        gamma: Discount factor for future rewards
        epsilon_start: Starting value of epsilon for epsilon-greedy policy
        epsilon_end: Minimum value of epsilon
        epsilon_decay: Decay rate of epsilon
    """
    # Create model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Initialize game
    game = DoppelkopfGame()
    
    # Initialize RL agent with custom parameters
    state_size = game.get_state_size()
    action_size = game.get_action_size()
    rl_agent = RLAgent(
        state_size=state_size,
        action_size=action_size,
        learning_rate=learning_rate,
        gamma=gamma,
        epsilon_start=epsilon_start,
        epsilon_end=epsilon_end,
        epsilon_decay=epsilon_decay
    )
    
    # Initialize opponents (random agents)
    opponents = [select_random_action] * (game.num_players - 1)
    
    logger.info(f"Starting training for {episodes} episodes")
    logger.info(f"Training parameters: LR={learning_rate}, Gamma={gamma}, "
                f"Epsilon: {epsilon_start}->{epsilon_end} (decay={epsilon_decay})")
    
    # Training statistics
    episode_rewards = []
    episode_wins = []
    episode_details = []
    
    for episode in range(1, episodes + 1):
        # Reset the game
        game.reset()
        
        # Play one episode
        episode_reward, episode_win, details = play_episode(game, rl_agent, opponents, episode, verbose)
        
        # Record statistics
        episode_rewards.append(episode_reward)
        episode_wins.append(episode_win)
        episode_details.append(details)
        
        # Log progress
        avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) > 100 else np.mean(episode_rewards)
        win_rate = np.mean(episode_wins[-100:]) if len(episode_wins) > 100 else np.mean(episode_wins)
        logger.info(f"Episode {episode}/{episodes} - "
                    f"Reward: {episode_reward:.2f}, "
                    f"Win: {episode_win}, "
                    f"Avg Reward: {avg_reward:.2f}, "
                    f"Win Rate: {win_rate:.2f}")
        
        # Save the model at regular intervals
        save_interval = max(1, episodes // 10)  # Save at least 10 checkpoints
        if episode % save_interval == 0 or episode == episodes:
            model_path = os.path.join(model_dir, f"model_episode_{episode}.pt")
            rl_agent.save(model_path)
            logger.info(f"Saved model to {model_path}")
    
    # Save the final model
    final_model_path = os.path.join(model_dir, "final_model.pt")
    rl_agent.save(final_model_path)
    logger.info(f"Saved final model to {final_model_path}")
    
    # Also save to the default location for the app
    default_model_path = os.path.join("models", "final_model.pt")
    rl_agent.save(default_model_path)
    logger.info(f"Saved final model to default location: {default_model_path}")
    
    # Print summary of all episodes
    print("\n" + "="*50)
    print("Training Summary")
    print("="*50)
    print(f"Episodes: {episodes}")
    print(f"Average Reward: {np.mean(episode_rewards):.2f}")
    print(f"Win Rate: {np.mean(episode_wins):.2f}")
    
    # Print details for the last few episodes
    num_details = min(10, len(episode_details))
    for i in range(len(episode_details) - num_details, len(episode_details)):
        print(f"\nEpisode {i+1}:")
        print(f"  Variant: {episode_details[i]['variant']}")
        print(f"  Winner: {episode_details[i]['winner']}")
        print(f"  Score - RE: {episode_details[i]['re_score']}, KONTRA: {episode_details[i]['kontra_score']}")
        print(f"  RL Agent Team: {episode_details[i]['rl_team']}")
        print(f"  Reward: {episode_rewards[i]:.2f}")
    
    return episode_rewards, episode_wins, episode_details

def calculate_reward(game, player_idx: int, action_type: str = 'card', announcement: str = None) -> float:
    """
    Calculate the reward for the given player.
    
    Args:
        game: The game instance
        player_idx: Index of the player
        action_type: Type of action ('card', 'announce', or 'variant')
        announcement: The announcement made ('re' or 'contra')
        
    Returns:
        The reward value
    """
    # Basic reward structure
    reward = 0
    
    # Get the player's team
    player_team = game.teams[player_idx]
    team_idx = 0 if player_team == TEAM_RE else 1
    
    # Reward for winning a trick (only applies to card actions)
    if action_type == 'card' and game.trick_winner == player_idx:
        # Simple reward for winning a trick
        reward += 1.0
    
    # Reward for making announcements
    if action_type == 'announce':
        # Small immediate reward for making an announcement
        reward += 1.0
        
        # Additional reward based on the player's team
        if (announcement == 're' and player_team == TEAM_RE) or \
           (announcement == 'contra' and player_team == TEAM_KONTRA):
            # Correct team announcement
            reward += 1.0
            
        # Reward based on current score advantage
        if game.scores[team_idx] > game.scores[1 - team_idx]:
            # If player's team is ahead, announcing is good
            reward += 1.0
    
    # Reward for selecting game variants
    if action_type == 'variant':
        # Small immediate reward for selecting a variant
        reward += 0.5
        
        # We could add more sophisticated rewards based on the hand and variant
        # For example, reward for selecting hochzeit when having both Queens of Clubs
        if announcement == 'hochzeit' and hasattr(game, 'has_hochzeit') and game.has_hochzeit(player_idx):
            reward += 2.0
        
        # Reward for selecting solo variants when appropriate
        if announcement in ['queen_solo', 'jack_solo'] and player_idx == 0:
            # Simple reward for selecting a solo variant
            reward += 1.0
    
    # Continuous reward based on score difference
    if hasattr(game, 'scores') and len(game.scores) == 2:
        # Get the score difference between the player's team and the opponent team
        score_diff = game.scores[team_idx] - game.scores[1 - team_idx]
        
        # Give a small continuous reward based on the score difference
        # This encourages the agent to maximize the score difference throughout the game
        reward += score_diff / 50.0  # Scale down to avoid overshadowing other rewards
    
    return reward

def play_episode(game, rl_agent, opponents, episode_num, verbose=False) -> Tuple[float, bool, Dict]:
    """
    Play one episode of the game.
    
    Args:
        game: The game instance
        rl_agent: The RL agent
        opponents: List of opponent agents
        episode_num: Current episode number
        verbose: Whether to print detailed game information
        
    Returns:
        Tuple of (total reward for the RL agent, whether the RL agent's team won, episode details)
    """
    # RL agent is always player 0
    rl_player_idx = 0
    
    # Track the total reward for the RL agent
    total_reward = 0
    
    # Add variant selection phase flag to the game
    game.variant_selection_phase = True
    
    if verbose:
        logger.info(f"Episode {episode_num} - Starting variant selection phase")
    
    # Handle variant selection phase for all players
    selected_variant = 'normal'  # Default
    
    # First, let the RL agent (player 0) select a variant
    if rl_player_idx == 0:
        # Get the current state
        state = game.get_state_for_player(rl_player_idx)
        
        # Select a variant action
        action_result = rl_agent.select_action(game, rl_player_idx)
        
        if action_result and action_result[0] == 'variant':
            action_type, variant = action_result
            selected_variant = variant
            
            # Use the set_variant method to properly update the game state
            game.set_variant(variant, rl_player_idx)
            
            # Get the next state
            next_state = game.get_state_for_player(rl_player_idx)
            
            # Calculate reward for variant selection
            reward = calculate_reward(game, rl_player_idx, 'variant', variant)
            
            # Observe the action and train
            rl_agent.observe_action(state, variant, next_state, reward, 'variant')
            rl_agent.train()
            total_reward += reward
            
            if verbose:
                logger.info(f"Episode {episode_num} - Player {rl_player_idx} (RL agent) selected variant: {variant}")
    
    # Then, let all other players select a variant (they'll choose 'normal')
    for i in range(1, game.num_players):
        if verbose:
            logger.info(f"Episode {episode_num} - Player {i} (AI opponent) selecting variant")
        
        # AI opponents always choose 'normal'
        game.set_variant('normal', i)
    
    # The variant selection phase should now be automatically ended by the game
    if verbose:
        logger.info(f"Episode {episode_num} - Variant selection phase ended. Game variant: {game.game_variant}")
    
    # Track announcements to avoid duplicates
    re_announced = False
    contra_announced = False
    
    if verbose:
        logger.info(f"Episode {episode_num} - Starting card play phase")
    
    # Play until the game is over
    trick_count = 0
    card_count = 0
    max_tricks = 100  # Safety limit to prevent infinite loops
    
    while not game.game_over and trick_count < max_tricks:
        current_player = game.current_player
        
        # Get the current state
        state = game.get_state_for_player(current_player)
        
        # Log current game state
        if len(game.current_trick) == 0:
            trick_count += 1
            if verbose:
                print_game_state(game, episode_num, trick_count)
        
        # Select an action
        if current_player == rl_player_idx:
            action_result = rl_agent.select_action(game, current_player)
            
            # Handle different action types
            if action_result and isinstance(action_result, tuple) and len(action_result) == 2:
                action_type, action = action_result
                
                if action_type == 'card':
                    # Log card play
                    card_count += 1
                    if verbose:
                        logger.info(f"Episode {episode_num} - Player {current_player} (RL agent) plays: {print_card(action)}")
                    
                    # Play the card
                    game.play_card(current_player, action)
                    
                    # Convert the card to an action index for the RL agent
                    action_idx = game.card_to_idx(action)
                    
                    # Get the next state
                    next_state = game.get_state_for_player(current_player)
                    
                    # Calculate reward for playing a card
                    reward = calculate_reward(game, current_player, 'card')
                    
                    # Observe the action and train
                    rl_agent.observe_action(state, action_idx, next_state, reward, 'card')
                    rl_agent.train()
                    total_reward += reward
                
                elif action_type == 'announce':
                    # Make the announcement
                    if action == 're' and not re_announced:
                        re_announced = True
                        # In a real game, this would trigger the re announcement
                        # For training, we just track it
                        
                        if verbose:
                            logger.info(f"Episode {episode_num} - Player {current_player} (RL agent) announces: RE")
                        
                        # Get the next state (same as current since announcement doesn't change game state)
                        next_state = state
                        
                        # Calculate reward for making an announcement
                        reward = calculate_reward(game, current_player, 'announce', 're')
                        
                        # Observe the action and train
                        rl_agent.observe_action(state, 're', next_state, reward, 'announce')
                        rl_agent.train()
                        total_reward += reward
                    
                    elif action == 'contra' and not contra_announced:
                        contra_announced = True
                        # In a real game, this would trigger the contra announcement
                        # For training, we just track it
                        
                        if verbose:
                            logger.info(f"Episode {episode_num} - Player {current_player} (RL agent) announces: CONTRA")
                        
                        # Get the next state (same as current since announcement doesn't change game state)
                        next_state = state
                        
                        # Calculate reward for making an announcement
                        reward = calculate_reward(game, current_player, 'announce', 'contra')
                        
                        # Observe the action and train
                        rl_agent.observe_action(state, 'contra', next_state, reward, 'announce')
                        rl_agent.train()
                        total_reward += reward
            else:
                # RL agent couldn't select a valid action
                if verbose:
                    logger.warning(f"Episode {episode_num} - Player {current_player} (RL agent) couldn't select a valid action")
                
                # Get legal actions for debugging
                legal_actions = game.get_legal_actions(current_player)
                if verbose:
                    logger.warning(f"Legal actions: {len(legal_actions)}")
                
                # Force a random action if there are legal actions available
                if legal_actions:
                    action = random.choice(legal_actions)
                    if verbose:
                        logger.info(f"Episode {episode_num} - Forcing random action for Player {current_player}: {print_card(action)}")
                    
                    # Play the card
                    game.play_card(current_player, action)
                    
                    # Convert the card to an action index for the RL agent
                    action_idx = game.card_to_idx(action)
                    
                    # Get the next state
                    next_state = game.get_state_for_player(current_player)
                    
                    # Calculate reward for playing a card (with penalty for random action)
                    reward = calculate_reward(game, current_player, 'card') - 1.0  # Penalty for random action
                    
                    # Observe the action and train
                    rl_agent.observe_action(state, action_idx, next_state, reward, 'card')
                    rl_agent.train()
                    total_reward += reward
                    card_count += 1
                else:
                    # No legal actions available, this should not happen
                    # End the game to avoid infinite loop
                    logger.error(f"Episode {episode_num} - No legal actions available for Player {current_player}. Ending game.")
                    game.game_over = True
                    break
        else:
            # Opponent's turn - they only play cards, no announcements
            opponent_idx = current_player - 1  # Adjust for the RL agent
            action = opponents[opponent_idx](game, current_player)
            
            # Check if the opponent could select a valid action
            if action is None:
                # Opponent couldn't select a valid action
                if verbose:
                    logger.warning(f"Episode {episode_num} - Player {current_player} (AI opponent) couldn't select a valid action")
                
                # Get legal actions for debugging
                legal_actions = game.get_legal_actions(current_player)
                if verbose:
                    logger.warning(f"Legal actions: {len(legal_actions)}")
                
                # Force a random action if there are legal actions available
                if legal_actions:
                    action = random.choice(legal_actions)
                    if verbose:
                        logger.info(f"Episode {episode_num} - Forcing random action for Player {current_player}: {print_card(action)}")
                else:
                    # No legal actions available, this should not happen
                    # End the game to avoid infinite loop
                    logger.error(f"Episode {episode_num} - No legal actions available for Player {current_player}. Ending game.")
                    game.game_over = True
                    break
            
            # Log card play
            card_count += 1
            if verbose:
                logger.info(f"Episode {episode_num} - Player {current_player} (AI opponent) plays: {print_card(action)}")
            
            # Play the card
            game.play_card(current_player, action)
    
    # Check if we hit the max tricks limit
    if trick_count >= max_tricks:
        logger.warning(f"Episode {episode_num} - Reached maximum number of tricks ({max_tricks}). Ending game.")
        game.game_over = True
    
    # Check if the RL agent's team won
    rl_team = game.teams[rl_player_idx]
    win = game.winner == rl_team
    
    # Get the player's team index
    team_idx = 0 if rl_team == TEAM_RE else 1
    
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
    winner_team = "RE" if game.winner == TEAM_RE else "KONTRA"
    if verbose:
        logger.info(f"Episode {episode_num} - Game over! {winner_team} team wins with score {score_diff}. RL agent reward: {total_reward:.2f}")
    
    # Collect episode details
    episode_details = {
        'variant': selected_variant,
        'winner': winner_team,
        're_score': game.scores[0],
        'kontra_score': game.scores[1],
        'rl_team': 'RE' if rl_team == TEAM_RE else 'KONTRA',
        'tricks_played': trick_count,
        'cards_played': card_count,
        're_announced': re_announced,
        'contra_announced': contra_announced
    }
    
    return total_reward, win, episode_details

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train a Doppelkopf RL agent')
    parser.add_argument('--episodes', type=int, default=10,
                        help='Number of episodes to train for (default: 10)')
    parser.add_argument('--model-dir', type=str, default='models/training',
                        help='Directory to save models (default: models/training)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed game information')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                        help='Learning rate for the optimizer (default: 0.001)')
    parser.add_argument('--gamma', type=float, default=0.99,
                        help='Discount factor for future rewards (default: 0.99)')
    parser.add_argument('--epsilon-start', type=float, default=1.0,
                        help='Starting value of epsilon for epsilon-greedy policy (default: 1.0)')
    parser.add_argument('--epsilon-end', type=float, default=0.05,
                        help='Minimum value of epsilon (default: 0.05)')
    parser.add_argument('--epsilon-decay', type=float, default=0.9995,
                        help='Decay rate of epsilon (default: 0.9995)')
    return parser.parse_args()

def main():
    """Main function to run the training."""
    args = parse_arguments()
    
    # Initialize logger
    os.makedirs('logs', exist_ok=True)
    logger.setup_logger('logs')
    
    # Train for the specified number of episodes
    train(
        model_dir=args.model_dir,
        episodes=args.episodes,
        verbose=args.verbose,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        epsilon_start=args.epsilon_start,
        epsilon_end=args.epsilon_end,
        epsilon_decay=args.epsilon_decay
    )

if __name__ == "__main__":
    main()
