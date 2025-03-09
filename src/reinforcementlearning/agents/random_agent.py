"""
Random agent for Doppelkopf.
This module provides functions for a random agent that selects random legal actions.
"""

import random
from typing import Any, Dict

def select_random_action(game, player_idx: int) -> Any:
    """
    Select a random legal action.
    
    Args:
        game: The game instance or state dictionary
        player_idx: Index of the player
        
    Returns:
        A randomly selected legal action
    """
    # Check if game is a DoppelkopfGame instance or a dictionary
    if hasattr(game, 'get_legal_actions'):
        # It's a DoppelkopfGame instance
        legal_actions = game.get_legal_actions(player_idx)
    else:
        # It's a dictionary state
        from src.backend.game.doppelkopf import get_legal_actions
        legal_actions = get_legal_actions(game, player_idx)
    if not legal_actions:
        return None
    return random.choice(legal_actions)

# No need for observe_action function as random agent doesn't learn
