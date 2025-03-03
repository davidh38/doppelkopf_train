# Doppelkopf Reinforcement Learning

This directory contains the reinforcement learning implementation for training AI agents to play Doppelkopf.

## Training a Score-Optimized Agent

The new score-optimized training focuses on maximizing the score difference rather than just winning. This approach encourages the agent to play more aggressively to maximize points.

To train a score-optimized agent, run:

```bash
# From the project root directory
python src/reinforcementlearning/train_score_optimizer.py
```

### Training Parameters

You can customize the training with various parameters:

```bash
python src/reinforcementlearning/train_score_optimizer.py \
  --episodes 20000 \
  --eval-interval 1000 \
  --save-interval 1000 \
  --model-dir models/score_optimizer \
  --learning-rate 0.0005 \
  --gamma 0.99 \
  --epsilon-start 1.0 \
  --epsilon-end 0.05 \
  --epsilon-decay 0.9995
```

### Key Differences from Standard Training

The score-optimized training differs from the standard training in several ways:

1. **Reward Function**: The agent receives rewards based on the score difference throughout the game, not just at the end.
2. **Trick Rewards**: Higher rewards for capturing high-value cards (10s, Queens, Kings, Aces).
3. **End-Game Reward**: The final reward is primarily based on the score difference, with a smaller bonus for winning.

## Standard Training

To run the standard training (focused on winning rather than score maximization):

```bash
# From the project root directory
python src/reinforcementlearning/main.py
```

## Using a Trained Model

To use a trained model in the game:

1. Make sure the model file is in the `models/` directory
2. Start the game with the model:

```bash
python src/backend/app.py --model models/score_optimizer/final_score_optimizer_model.pt
```

## Comparing Models

You can compare the performance of different models by running them against each other or against random agents.
