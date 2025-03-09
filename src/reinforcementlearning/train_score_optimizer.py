#!/usr/bin/env python3
"""
Doppelkopf AI Training Program - Score Optimizer
This program implements a reinforcement learning approach to train an AI to play Doppelkopf,
with a focus on maximizing scores rather than just winning.
"""

import argparse
import os
import sys
import time

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.reinforcementlearning.doppelkopf_game import DoppelkopfGame
from src.reinforcementlearning.agents.random_agent import select_random_action
from src.reinforcementlearning.agents.rl_agent import RLAgent
import src.reinforcementlearning.training.trainer as trainer
import src.backend.utils.logger as logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train an AI to play Doppelkopf with score optimization')
    parser.add_argument('--episodes', type=int, default=20000,
                        help='Number of episodes to train for')
    parser.add_argument('--eval-interval', type=int, default=1000,
                        help='Evaluate the agent every N episodes')
    parser.add_argument('--save-interval', type=int, default=1000,
                        help='Save the agent every N episodes')
    parser.add_argument('--load-model', type=str, default=None,
                        help='Path to a saved model to load')
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Directory to save logs')
    parser.add_argument('--model-dir', type=str, default='models/score_optimizer',
                        help='Directory to save models')
    parser.add_argument('--learning-rate', type=float, default=0.0005,
                        help='Learning rate for the optimizer')
    parser.add_argument('--gamma', type=float, default=0.99,
                        help='Discount factor for future rewards')
    parser.add_argument('--epsilon-start', type=float, default=1.0,
                        help='Starting value of epsilon for epsilon-greedy policy')
    parser.add_argument('--epsilon-end', type=float, default=0.05,
                        help='Minimum value of epsilon')
    parser.add_argument('--epsilon-decay', type=float, default=0.9995,
                        help='Decay rate of epsilon')
    return parser.parse_args()

def main():
    """Main function to run the training program."""
    args = parse_arguments()
    
    # Create directories if they don't exist
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)
    
    # Initialize logger
    logger.setup_logger(args.log_dir)
    logger.info("Starting Doppelkopf AI training program - Score Optimizer")
    logger.info(f"Training parameters: LR={args.learning_rate}, Gamma={args.gamma}, "
                f"Epsilon: {args.epsilon_start}->{args.epsilon_end} (decay={args.epsilon_decay})")
    
    # Initialize game
    game = DoppelkopfGame()
    
    # Initialize agents with custom parameters
    rl_agent = RLAgent(
        state_size=game.get_state_size(),
        action_size=game.get_action_size(),
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        epsilon_start=args.epsilon_start,
        epsilon_end=args.epsilon_end,
        epsilon_decay=args.epsilon_decay
    )
    
    if args.load_model:
        rl_agent.load(args.load_model)
        logger.info(f"Loaded model from {args.load_model}")
    
    # Other players are random agents for now
    opponents = [select_random_action for _ in range(3)]
    
    # Train the agent
    start_time = time.time()
    trainer.train(game, rl_agent, opponents, args.episodes, args.eval_interval, args.save_interval, args.model_dir)
    
    # Log training time
    training_time = time.time() - start_time
    logger.info(f"Training completed in {training_time:.2f} seconds")
    
    # Save the final model
    final_model_path = os.path.join(args.model_dir, 'final_score_optimizer_model.pt')
    rl_agent.save(final_model_path)
    logger.info(f"Saved final model to {final_model_path}")

if __name__ == "__main__":
    main()
