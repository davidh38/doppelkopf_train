#!/usr/bin/env python3
"""
Doppelkopf game class for reinforcement learning.
This module provides a class-based interface to the Doppelkopf game logic.
"""

import os
import sys
import numpy as np
from typing import List, Dict, Tuple, Optional, Any

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.backend.game.doppelkopf import (
    create_game_state, get_legal_actions, play_card, announce, set_variant,
    get_state_size as get_doppelkopf_state_size,
    get_action_size as get_doppelkopf_action_size,
    get_state_for_player, action_to_card, card_to_idx, idx_to_card,
    TEAM_RE, TEAM_KONTRA, TEAM_UNKNOWN,
    VARIANT_NORMAL, VARIANT_HOCHZEIT, VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_FLESHLESS
)

class DoppelkopfGame:
    """
    A class-based interface to the Doppelkopf game logic.
    This class wraps the functions from src.backend.game.doppelkopf into a class
    for easier use with reinforcement learning algorithms.
    """
    
    def __init__(self):
        """Initialize a new Doppelkopf game."""
        self.reset()
    
    def reset(self):
        """Reset the game to its initial state."""
        self.state = create_game_state()
        self.num_players = self.state['num_players']
        self.hands = self.state['hands']
        self.tricks = self.state['tricks']
        self.current_trick = self.state['current_trick']
        self.current_player = self.state['current_player']
        self.game_variant = self.state['game_variant']
        self.scores = self.state['scores']
        self.player_scores = self.state['player_scores']
        self.teams = self.state['teams']
        self.trick_winner = self.state['trick_winner']
        self.game_over = self.state['game_over']
        self.variant_selection_phase = self.state['variant_selection_phase']
        self.re_announced = self.state['re_announced']
        self.contra_announced = self.state['contra_announced']
        self.can_announce = self.state['can_announce']
        self.winner = None
        
        # Return the state for chaining
        return self.state
    
    def get_legal_actions(self, player_idx: int) -> List[Dict]:
        """
        Get the legal actions (cards that can be played) for the given player.
        
        Args:
            player_idx: Index of the player
            
        Returns:
            List of legal cards to play
        """
        return get_legal_actions(self.state, player_idx)
    
    def play_card(self, player_idx: int, card: Dict) -> bool:
        """
        Play a card for the given player.
        
        Args:
            player_idx: Index of the player
            card: The card to play
            
        Returns:
            True if the move was legal and executed, False otherwise
        """
        result = play_card(self.state, player_idx, card)
        
        # Update instance variables
        self.hands = self.state['hands']
        self.tricks = self.state['tricks']
        self.current_trick = self.state['current_trick']
        self.current_player = self.state['current_player']
        self.scores = self.state['scores']
        self.player_scores = self.state['player_scores']
        self.trick_winner = self.state['trick_winner']
        self.game_over = self.state['game_over']
        self.can_announce = self.state['can_announce']
        
        if self.game_over and 'winner' in self.state:
            self.winner = self.state['winner']
        
        return result
    
    def announce(self, player_idx: int, announcement: str) -> bool:
        """
        Make an announcement (Re, Contra, or Hochzeit).
        
        Args:
            player_idx: Index of the player
            announcement: The announcement to make ('re', 'contra', or 'hochzeit')
            
        Returns:
            True if the announcement was legal and executed, False otherwise
        """
        result = announce(self.state, player_idx, announcement)
        
        # Update instance variables
        if announcement == 'hochzeit':
            self.game_variant = self.state['game_variant']
        elif announcement == 're':
            self.re_announced = True
        elif announcement == 'contra':
            self.contra_announced = True
        
        return result
    
    def set_variant(self, variant: str, player_idx: int = None) -> bool:
        """
        Set the game variant for a player.
        
        Args:
            variant: The variant to set ('normal', 'hochzeit', 'queen_solo', 'jack_solo', 'fleshless')
            player_idx: Index of the player making the choice (if None, uses current_player)
            
        Returns:
            True if the variant was set, False otherwise
        """
        result = set_variant(self.state, variant, player_idx)
        
        # Update instance variables
        self.current_player = self.state['current_player']
        self.game_variant = self.state['game_variant']
        self.variant_selection_phase = self.state['variant_selection_phase']
        
        return result
    
    def has_hochzeit(self, player_idx: int) -> bool:
        """
        Check if the player has both Queens of Clubs (Hochzeit/Marriage).
        
        Args:
            player_idx: Index of the player
            
        Returns:
            True if the player has both Queens of Clubs, False otherwise
        """
        return player_idx in self.state['players_with_hochzeit']
    
    def get_state_for_player(self, player_idx: int) -> np.ndarray:
        """
        Get the state representation for the given player.
        
        Args:
            player_idx: Index of the player
            
        Returns:
            A numpy array representing the state from the player's perspective
        """
        return get_state_for_player(self.state, player_idx)
    
    def action_to_card(self, action: int, player_idx: int) -> Optional[Dict]:
        """
        Convert an action index to a card for the given player.
        
        Args:
            action: The action index
            player_idx: Index of the player
            
        Returns:
            The corresponding card, or None if the action is invalid
        """
        return action_to_card(self.state, action, player_idx)
    
    def card_to_idx(self, card: Dict) -> int:
        """
        Convert a card to an index in the state representation.
        
        Args:
            card: The card dictionary
            
        Returns:
            The index of the card
        """
        return card_to_idx(card)
    
    def idx_to_card(self, idx: int) -> Dict:
        """
        Convert an index to a card.
        
        Args:
            idx: The index to convert
            
        Returns:
            The corresponding card
        """
        return idx_to_card(idx)
    
    def get_state_size(self) -> int:
        """
        Get the size of the state representation for the RL agent.
        
        Returns:
            The size of the state vector
        """
        return get_doppelkopf_state_size()
    
    def get_action_size(self) -> int:
        """
        Get the size of the action space for the RL agent.
        
        Returns:
            The size of the action space
        """
        return get_doppelkopf_action_size()
