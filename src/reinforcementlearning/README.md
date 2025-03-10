# Doppelkopf Reinforcement Learning

This directory contains the reinforcement learning implementation for training AI agents to play Doppelkopf.

## Training an Agent

The training script focuses on maximizing both winning and score difference. This approach encourages the agent to play strategically to win games while also maximizing points.

To train an agent, run:

```bash
# From the project root directory
python src/reinforcementlearning/train.py
```

### Training Parameters

You can customize the training with various parameters:

```bash
python src/reinforcementlearning/train.py \
  --episodes 10 \
  --model-dir models/training \
  --verbose \
  --learning-rate 0.001 \
  --gamma 0.99 \
  --epsilon-start 1.0 \
  --epsilon-end 0.05 \
  --epsilon-decay 0.9995
```

### Training Approach

The training approach includes:

1. **Balanced Reward Function**: The agent receives rewards for winning tricks, making appropriate announcements, and maximizing score difference.
2. **Trick Rewards**: Rewards for capturing high-value cards (10s, Queens, Kings, Aces).
3. **End-Game Reward**: The final reward is based on both the score difference and whether the agent's team won.
4. **Variant Selection**: The agent learns to select appropriate game variants based on its hand.

## Quick Training

For quick testing, you can train for just 1 episode:

```bash
# From the project root directory
python src/reinforcementlearning/train_1_episode.py
```

## Using a Trained Model

To use a trained model in the game:

1. The model file is automatically saved to `models/final_model.pt` after training
2. Start the game with the default model:

```bash
python src/backend/app.py
```

Or specify a different model:

```bash
python src/backend/app.py --model models/my_custom_model.pt
```

## Playing with a Trained Model

You can play against the trained model by running:

```bash
python src/reinforcementlearning/play.py
```

This will load the default model from `models/final_model.pt` and let you play against it.
