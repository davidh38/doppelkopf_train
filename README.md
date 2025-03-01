# Doppelkopf AI Training Program

This project implements a reinforcement learning approach to train an AI to play Doppelkopf, a traditional German card game.

## Overview

Doppelkopf is a trick-taking card game for four players, played with a double deck of 48 cards (two copies of each card from 9 to Ace in four suits). Players are divided into two teams, typically determined by who holds the Queens of Clubs. The goal is to score more points than the opposing team by winning tricks containing valuable cards.

This project uses Deep Q-Learning to train an AI agent to play Doppelkopf effectively. The agent learns by playing against random agents and gradually improves its strategy through experience.

## Project Structure

- `main.py`: Entry point for training the AI
- `play.py`: Script to play Doppelkopf against a trained AI
- `game/`: Implementation of the Doppelkopf game rules and mechanics
- `agents/`: Implementation of different agents (RL agent and random agent)
- `training/`: Training process for the RL agent
- `utils/`: Utility functions and classes

## Requirements

- Python 3.7+
- PyTorch
- NumPy

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/doppelkopf-ai.git
cd doppelkopf-ai
```

2. Install the required packages:
```
pip install torch numpy
```

## Usage

### Training the AI

To train the AI, run:

```
python main.py --episodes 10000 --eval-interval 1000 --save-interval 1000
```

Options:
- `--episodes`: Number of episodes to train for (default: 10000)
- `--eval-interval`: Evaluate the agent every N episodes (default: 1000)
- `--save-interval`: Save the agent every N episodes (default: 1000)
- `--load-model`: Path to a saved model to load (optional)
- `--log-dir`: Directory to save logs (default: 'logs')
- `--model-dir`: Directory to save models (default: 'models')

### Playing Against the AI

To play against a trained AI, run:

```
python play.py --model models/final_model.pt
```

Options:
- `--model`: Path to a trained model (required)

## How the AI Works

The AI uses Deep Q-Learning, a reinforcement learning technique that combines Q-learning with deep neural networks. The key components are:

1. **State Representation**: The game state is represented as a vector that includes:
   - The player's hand (which cards they have)
   - The current trick (which cards have been played)
   - The current player

2. **Action Selection**: The AI selects actions using an epsilon-greedy policy:
   - With probability epsilon, it selects a random legal action
   - With probability 1-epsilon, it selects the action with the highest Q-value

3. **Reward Structure**: The AI receives rewards for:
   - Winning tricks (proportional to the points in the trick)
   - Winning the game (large positive reward)
   - Losing the game (large negative reward)

4. **Neural Network**: A deep neural network is used to approximate the Q-function:
   - Input: The state representation
   - Output: Q-values for each possible action

5. **Experience Replay**: The AI stores experiences in a replay buffer and learns from random batches to break correlations between consecutive samples.

## Future Improvements

- Implement more sophisticated agents (e.g., rule-based agents)
- Add support for different Doppelkopf variants (e.g., solo games)
- Improve the state representation to include more information
- Experiment with different neural network architectures
- Add a graphical user interface for playing against the AI

## License

This project is licensed under the MIT License - see the LICENSE file for details.
