"""
Trainer for Doppelkopf AI.
This module handles the training process for the RL agent.
It supports training for card playing, making Re/Contra announcements, and selecting game variants.
"""

import os
import time
import numpy as np
from typing import List, Dict, Any, Tuple
import utils.logger as logger

def train(game, rl_agent, opponents, num_episodes: int, eval_interval: int, save_interval: int, model_dir: str):
    """
    Train the RL agent.
    
    Args:
        game: The game instance
        rl_agent: The RL agent to train
        opponents: List of opponent agents
        num_episodes: Number of episodes to train for
        eval_interval: Evaluate the agent every N episodes
        save_interval: Save the agent every N episodes
        model_dir: Directory to save models
    """
    # Ensure we have the right number of opponents
    assert len(opponents) == game.num_players - 1, \
        f"Expected {game.num_players - 1} opponents, got {len(opponents)}"
    
    logger.info(f"Starting training for {num_episodes} episodes")
    
    # Training statistics
    episode_rewards = []
    episode_wins = []
    
    for episode in range(1, num_episodes + 1):
        # Reset the game
        game.reset()
        
        # Play one episode
        episode_reward, episode_win = play_episode(game, rl_agent, opponents)
        
        # Record statistics
        episode_rewards.append(episode_reward)
        episode_wins.append(episode_win)
        
        # Log progress
        if episode % 100 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            win_rate = np.mean(episode_wins[-100:])
            logger.info(f"Episode {episode}/{num_episodes} - "
                            f"Avg Reward: {avg_reward:.2f}, "
                            f"Win Rate: {win_rate:.2f}")
        
        # Evaluate the agent
        if episode % eval_interval == 0:
            evaluate(game, rl_agent, opponents, 10)
        
        # Save the model
        if episode % save_interval == 0:
            model_path = os.path.join(model_dir, f"model_episode_{episode}.pt")
            rl_agent.save(model_path)
            logger.info(f"Saved model to {model_path}")

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
    
    # Reward for winning a trick (only applies to card actions)
    if action_type == 'card' and game.trick_winner == player_idx:
        # Get the points in the trick
        trick_points = sum(card.get_value() for card in game.tricks[-1])
        reward += trick_points / 10  # Scale down the points
    
    # Reward for making announcements
    if action_type == 'announce':
        # Small immediate reward for making an announcement
        reward += 1.0
        
        # Additional reward based on the player's team
        player_team = game.teams[player_idx]
        if (announcement == 're' and player_team.name == 'RE') or \
           (announcement == 'contra' and player_team.name == 'KONTRA'):
            # Correct team announcement
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
            # Count relevant cards in hand
            count = 0
            for card in game.hands[player_idx]:
                if (announcement == 'queen_solo' and card.rank.name == 'QUEEN') or \
                   (announcement == 'jack_solo' and card.rank.name == 'JACK'):
                    count += 1
            
            # Reward based on count (more queens/jacks = better for solo)
            if count >= 4:  # Having at least 4 queens/jacks is good for solo
                reward += count / 2.0
    
    return reward

def play_episode(game, rl_agent, opponents) -> Tuple[float, bool]:
    """
    Play one episode of the game.
    
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
    
    # First, select game variant (only for player 0)
    if rl_player_idx == 0:
        # Get the current state
        state = game.get_state_for_player(rl_player_idx)
        
        # Select a variant action
        action_result = rl_agent.select_action(game, rl_player_idx)
        
        if action_result and action_result[0] == 'variant':
            action_type, variant = action_result
            
            # Set the game variant
            from game.doppelkopf import GameVariant
            if variant == 'normal':
                game.game_variant = GameVariant.NORMAL
            elif variant == 'hochzeit':
                game.game_variant = GameVariant.HOCHZEIT
            elif variant == 'queen_solo':
                game.game_variant = GameVariant.QUEEN_SOLO
            elif variant == 'jack_solo':
                game.game_variant = GameVariant.JACK_SOLO
            elif variant == 'fleshless':
                game.game_variant = GameVariant.FLESHLESS
            
            # Get the next state
            next_state = game.get_state_for_player(rl_player_idx)
            
            # Calculate reward for variant selection
            reward = calculate_reward(game, rl_player_idx, 'variant', variant)
            
            # Observe the action and train
            rl_agent.observe_action(state, variant, next_state, reward, 'variant')
            rl_agent.train()
            total_reward += reward
    
    # End variant selection phase
    game.variant_selection_phase = False
    
    # Track announcements to avoid duplicates
    re_announced = False
    contra_announced = False
    
    # Play until the game is over
    while not game.game_over:
        current_player = game.current_player
        
        # Get the current state
        state = game.get_state_for_player(current_player)
        
        # Select an action
        if current_player == rl_player_idx:
            action_result = rl_agent.select_action(game, current_player)
            
            # Handle different action types
            if action_result and isinstance(action_result, tuple) and len(action_result) == 2:
                action_type, action = action_result
                
                if action_type == 'card':
                    # Play the card
                    game.play_card(current_player, action)
                    
                    # Convert the card to an action index for the RL agent
                    action_idx = game._card_to_idx(action)
                    
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
                        
                        # Get the next state (same as current since announcement doesn't change game state)
                        next_state = state
                        
                        # Calculate reward for making an announcement
                        reward = calculate_reward(game, current_player, 'announce', 'contra')
                        
                        # Observe the action and train
                        rl_agent.observe_action(state, 'contra', next_state, reward, 'announce')
                        rl_agent.train()
                        total_reward += reward
            
        else:
            # Opponent's turn - they only play cards, no announcements
            opponent_idx = current_player - 1  # Adjust for the RL agent
            action = select_opponent_action(opponents[opponent_idx], game, current_player)
            
            # Play the card
            game.play_card(current_player, action)
    
    # Check if the RL agent's team won
    rl_team = game.teams[rl_player_idx]
    win = game.winner == rl_team
    
    # Add a win/loss reward
    win_reward = 10 if win else -10
    total_reward += win_reward
    
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

def play_evaluation_episode(game, rl_agent, opponents) -> Tuple[float, bool]:
    """
    Play one episode for evaluation (no training).
    
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
    
    # First, select game variant (only for player 0)
    if rl_player_idx == 0:
        # Select a variant action
        action_result = rl_agent.select_action(game, rl_player_idx)
        
        if action_result and action_result[0] == 'variant':
            action_type, variant = action_result
            
            # Set the game variant
            from game.doppelkopf import GameVariant
            if variant == 'normal':
                game.game_variant = GameVariant.NORMAL
            elif variant == 'hochzeit':
                game.game_variant = GameVariant.HOCHZEIT
            elif variant == 'queen_solo':
                game.game_variant = GameVariant.QUEEN_SOLO
            elif variant == 'jack_solo':
                game.game_variant = GameVariant.JACK_SOLO
            elif variant == 'fleshless':
                game.game_variant = GameVariant.FLESHLESS
            
            # Calculate reward for variant selection
            reward = calculate_reward(game, rl_player_idx, 'variant', variant)
            total_reward += reward
    
    # End variant selection phase
    game.variant_selection_phase = False
    
    # Track announcements to avoid duplicates
    re_announced = False
    contra_announced = False
    
    # Play until the game is over
    while not game.game_over:
        current_player = game.current_player
        
        # Select an action
        if current_player == rl_player_idx:
            action_result = rl_agent.select_action(game, current_player)
            
            # Handle different action types
            if action_result and isinstance(action_result, tuple) and len(action_result) == 2:
                action_type, action = action_result
                
                if action_type == 'card':
                    # Play the card
                    game.play_card(current_player, action)
                    
                    # Calculate reward for playing a card
                    reward = calculate_reward(game, current_player, 'card')
                    total_reward += reward
                
                elif action_type == 'announce':
                    # Make the announcement
                    if action == 're' and not re_announced:
                        re_announced = True
                        # In a real game, this would trigger the re announcement
                        # For evaluation, we just track it
                        
                        # Calculate reward for making an announcement
                        reward = calculate_reward(game, current_player, 'announce', 're')
                        total_reward += reward
                    
                    elif action == 'contra' and not contra_announced:
                        contra_announced = True
                        # In a real game, this would trigger the contra announcement
                        # For evaluation, we just track it
                        
                        # Calculate reward for making an announcement
                        reward = calculate_reward(game, current_player, 'announce', 'contra')
                        total_reward += reward
            
        else:
            # Opponent's turn - they only play cards, no announcements
            opponent_idx = current_player - 1  # Adjust for the RL agent
            action = select_opponent_action(opponents[opponent_idx], game, current_player)
            
            # Play the card
            game.play_card(current_player, action)
    
    # Check if the RL agent's team won
    rl_team = game.teams[rl_player_idx]
    win = game.winner == rl_team
    
    # Add a win/loss reward
    win_reward = 10 if win else -10
    total_reward += win_reward
    
    return total_reward, win

def evaluate(game, rl_agent, opponents, num_episodes: int):
    """
    Evaluate the RL agent.
    
    Args:
        game: The game instance
        rl_agent: The RL agent
        opponents: List of opponent agents
        num_episodes: Number of episodes to evaluate for
    """
    logger.info(f"Evaluating agent for {num_episodes} episodes")
    
    # Save the current epsilon
    original_epsilon = rl_agent.epsilon
    
    # Set epsilon to a small value for evaluation
    rl_agent.epsilon = 0.05
    
    # Evaluation statistics
    eval_rewards = []
    eval_wins = []
    
    for _ in range(num_episodes):
        # Reset the game
        game.reset()
        
        # Play one episode without training
        episode_reward, episode_win = play_evaluation_episode(game, rl_agent, opponents)
        
        # Record statistics
        eval_rewards.append(episode_reward)
        eval_wins.append(episode_win)
    
    # Restore the original epsilon
    rl_agent.epsilon = original_epsilon
    
    # Log evaluation results
    avg_reward = np.mean(eval_rewards)
    win_rate = np.mean(eval_wins)
    logger.info(f"Evaluation - Avg Reward: {avg_reward:.2f}, Win Rate: {win_rate:.2f}")
