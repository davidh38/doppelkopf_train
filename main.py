#!/usr/bin/env python3
"""
Doppelkopf AI Training Program
This program implements a reinforcement learning approach to train an AI to play Doppelkopf.
"""

import argparse
import os
import time
from game.doppelkopf import DoppelkopfGame
from agents.random_agent import select_random_action
from agents.rl_agent import RLAgent
import training.trainer as trainer
import utils.logger as logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train an AI to play Doppelkopf')
    parser.add_argument('--episodes', type=int, default=10000,
                        help='Number of episodes to train for')
    parser.add_argument('--eval-interval', type=int, default=1000,
                        help='Evaluate the agent every N episodes')
    parser.add_argument('--save-interval', type=int, default=1000,
                        help='Save the agent every N episodes')
    parser.add_argument('--load-model', type=str, default=None,
                        help='Path to a saved model to load')
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Directory to save logs')
    parser.add_argument('--model-dir', type=str, default='models',
                        help='Directory to save models')
    return parser.parse_args()

def main():
    """Main function to run the training program."""
    args = parse_arguments()
    
    # Create directories if they don't exist
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)
    
    # Initialize logger
    logger.setup_logger(args.log_dir)
    logger.info("Starting Doppelkopf AI training program")
    
    # Initialize game
    game = DoppelkopfGame()
    
    # Initialize agents
    rl_agent = RLAgent(game.get_state_size(), game.get_action_size())
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
    final_model_path = os.path.join(args.model_dir, 'final_model.pt')
    rl_agent.save(final_model_path)
    logger.info(f"Saved final model to {final_model_path}")

if __name__ == "__main__":
    main()
