"""
Reinforcement Learning agent for Doppelkopf.
This agent uses Deep Q-Learning to learn to play Doppelkopf.
It supports making Re/Contra announcements and selecting game variants.
"""

import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque, namedtuple
from typing import Any, List, Tuple

# Define a transition for the replay buffer
Transition = namedtuple('Transition', 
                        ('state', 'action', 'next_state', 'reward'))

class ReplayBuffer:
    """A replay buffer to store and sample transitions."""
    
    def __init__(self, capacity: int):
        """
        Initialize the replay buffer.
        
        Args:
            capacity: Maximum number of transitions to store
        """
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
    
    def push(self, *args):
        """Add a transition to the buffer."""
        self.buffer.append(Transition(*args))
    
    def sample(self, batch_size: int) -> List[Transition]:
        """
        Sample a batch of transitions.
        
        Args:
            batch_size: Number of transitions to sample
            
        Returns:
            A list of sampled transitions
        """
        return random.sample(self.buffer, batch_size)
    
    def __len__(self) -> int:
        """Get the current size of the buffer."""
        return len(self.buffer)

class DQN(nn.Module):
    """Deep Q-Network for Doppelkopf."""
    
    def __init__(self, input_size: int, output_size: int):
        """
        Initialize the DQN.
        
        Args:
            input_size: Size of the input state
            output_size: Size of the output action space
        """
        super(DQN, self).__init__()
        
        # Define the neural network architecture
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, output_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class RLAgent:
    """Reinforcement Learning agent using Deep Q-Learning."""
    
    def __init__(self, state_size: int, action_size: int, 
                 learning_rate: float = 0.001, 
                 gamma: float = 0.99, 
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.1,
                 epsilon_decay: float = 0.995,
                 buffer_size: int = 10000,
                 batch_size: int = 64,
                 target_update: int = 10):
        """
        Initialize the RL agent.
        
        Args:
            state_size: Size of the state space
            action_size: Size of the action space (cards only)
            learning_rate: Learning rate for the optimizer
            gamma: Discount factor for future rewards
            epsilon_start: Starting value of epsilon for epsilon-greedy policy
            epsilon_end: Minimum value of epsilon
            epsilon_decay: Decay rate of epsilon
            buffer_size: Size of the replay buffer
            batch_size: Batch size for training
            target_update: How often to update the target network
        """
        # Base state and action sizes for cards
        self.state_size = state_size
        self.action_size = action_size
        
        # Additional actions for announcements and game variants
        # 2 announcement actions (Re, Contra)
        # 5 game variant actions (Normal, Hochzeit, Queen Solo, Jack Solo, Fleshless)
        self.num_announcement_actions = 2
        self.num_variant_actions = 5
        
        # Total action size including cards, announcements, and variants
        self.total_action_size = action_size + self.num_announcement_actions + self.num_variant_actions
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update = target_update
        
        # Initialize device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize networks with expanded action space
        self.policy_net = DQN(state_size, self.total_action_size).to(self.device)
        self.target_net = DQN(state_size, self.total_action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Initialize optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        # Initialize replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
        
        # Initialize step counter
        self.steps_done = 0
    
    def select_action(self, game, player_idx: int) -> Any:
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            game: The game instance
            player_idx: Index of the player
            
        Returns:
            The selected action (card, announcement, or game variant)
        """
        # Check if we need to select a game variant (at the start of the game)
        if hasattr(game, 'variant_selection_phase') and game.variant_selection_phase:
            return self._select_variant_action(game, player_idx)
        
        # Check if we can make an announcement
        can_announce = False
        if hasattr(game, 'can_announce'):
            can_announce = game.can_announce
        else:
            # If not explicitly tracked, we can announce until the fifth card is played
            cards_played = len(game.current_trick)
            for trick in game.tricks:
                cards_played += len(trick)
            can_announce = cards_played < 5
        
        # Get legal card actions
        legal_card_actions = game.get_legal_actions(player_idx)
        if not legal_card_actions and not can_announce:
            return None
        
        # Get state representation
        state = game.get_state_for_player(player_idx)
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            # Random action selection
            
            # Determine all possible actions
            all_possible_actions = []
            
            # Add card actions
            for card in legal_card_actions:
                all_possible_actions.append(('card', card))
            
            # Add announcement actions if allowed
            if can_announce:
                player_team = game.teams[player_idx]
                if player_team.name == 'RE':
                    all_possible_actions.append(('announce', 're'))
                elif player_team.name == 'KONTRA':
                    all_possible_actions.append(('announce', 'contra'))
            
            # Randomly select one action
            if all_possible_actions:
                action_type, action = random.choice(all_possible_actions)
                return (action_type, action)
            return None
        else:
            # Greedy action selection
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)
                
                # Collect all possible actions with their Q-values
                action_q_values = []
                
                # Add card actions
                for card in legal_card_actions:
                    card_idx = game._card_to_idx(card)
                    action_q_values.append(('card', card, q_values[0][card_idx].item()))
                
                # Add announcement actions if allowed
                if can_announce:
                    player_team = game.teams[player_idx]
                    if player_team.name == 'RE':
                        re_idx = self.action_size  # First announcement action
                        action_q_values.append(('announce', 're', q_values[0][re_idx].item()))
                    elif player_team.name == 'KONTRA':
                        contra_idx = self.action_size + 1  # Second announcement action
                        action_q_values.append(('announce', 'contra', q_values[0][contra_idx].item()))
                
                # Select the action with the highest Q-value
                if action_q_values:
                    action_type, action, _ = max(action_q_values, key=lambda x: x[2])
                    return (action_type, action)
                return None
    
    def _select_variant_action(self, game, player_idx: int) -> Any:
        """
        Select a game variant action.
        
        Args:
            game: The game instance
            player_idx: Index of the player
            
        Returns:
            The selected game variant
        """
        # Get state representation
        state = game.get_state_for_player(player_idx)
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        # Epsilon-greedy variant selection
        if random.random() < self.epsilon:
            # Random variant
            variants = ['normal', 'hochzeit', 'queen_solo', 'jack_solo', 'fleshless']
            return ('variant', random.choice(variants))
        else:
            # Greedy variant selection
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)
                
                # Get Q-values for variant actions
                variant_start_idx = self.action_size + self.num_announcement_actions
                variant_q_values = q_values[0][variant_start_idx:variant_start_idx + self.num_variant_actions]
                
                # Map variant indices to names
                variants = ['normal', 'hochzeit', 'queen_solo', 'jack_solo', 'fleshless']
                
                # Select the variant with the highest Q-value
                variant_idx = variant_q_values.argmax().item()
                return ('variant', variants[variant_idx])
    
    def observe_action(self, state, action, next_state, reward, action_type='card'):
        """
        Observe an action and its result.
        
        Args:
            state: The state before the action
            action: The action that was taken (index)
            next_state: The state after the action
            reward: The reward received
            action_type: Type of action ('card', 'announce', or 'variant')
        """
        # Convert to tensors
        state_tensor = torch.FloatTensor(state).to(self.device)
        
        # Adjust action index based on action type
        if action_type == 'announce':
            if action == 're':
                action = self.action_size  # First announcement action
            else:  # 'contra'
                action = self.action_size + 1  # Second announcement action
        elif action_type == 'variant':
            variants = ['normal', 'hochzeit', 'queen_solo', 'jack_solo', 'fleshless']
            variant_idx = variants.index(action)
            action = self.action_size + self.num_announcement_actions + variant_idx
        
        action_tensor = torch.LongTensor([action]).to(self.device)
        
        if next_state is not None:
            next_state_tensor = torch.FloatTensor(next_state).to(self.device)
        else:
            next_state_tensor = None
            
        reward_tensor = torch.FloatTensor([reward]).to(self.device)
        
        # Store transition in replay buffer
        self.replay_buffer.push(state_tensor, action_tensor, next_state_tensor, reward_tensor)
        
        # Increment step counter
        self.steps_done += 1
        
        # Update target network if needed
        if self.steps_done % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
    
    def train(self):
        """Train the agent using a batch from the replay buffer."""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample a batch from the replay buffer
        transitions = self.replay_buffer.sample(self.batch_size)
        batch = Transition(*zip(*transitions))
        
        # Create batch tensors
        state_batch = torch.stack(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)
        
        # Create mask for non-terminal states
        non_final_mask = torch.tensor(
            tuple(map(lambda s: s is not None, batch.next_state)),
            device=self.device, dtype=torch.bool)
        
        non_final_next_states = torch.stack(
            [s for s in batch.next_state if s is not None])
        
        # Compute Q-values for the current states and actions
        state_action_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))
        
        # Compute V(s_{t+1}) for all next states
        next_state_values = torch.zeros(self.batch_size, device=self.device)
        next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()
        
        # Compute the expected Q-values
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch
        
        # Compute the loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
        
        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()
        
        return loss.item()
    
    def save(self, path: str):
        """
        Save the agent's policy network.
        
        Args:
            path: Path to save the model
        """
        torch.save(self.policy_net.state_dict(), path)
    
    def load(self, path: str):
        """
        Load the agent's policy network.
        
        Args:
            path: Path to load the model from
        """
        # Use map_location to ensure the model loads on the correct device
        self.policy_net.load_state_dict(torch.load(path, map_location=self.device))
        self.target_net.load_state_dict(self.policy_net.state_dict())
        print(f"Model loaded successfully to {self.device}")
