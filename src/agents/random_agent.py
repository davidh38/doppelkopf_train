"""
Random agent for Doppelkopf.
This module provides functions for a random agent that selects random legal actions.
"""

import random
from typing import Any, List

def select_random_action(game, player_idx: int) -> Any:
    """
    Select a random legal action.
    
    Args:
        game: The game instance
        player_idx: Index of the player
        
    Returns:
        A randomly selected legal action
    """
    legal_actions = game.get_legal_actions(player_idx)
    if not legal_actions:
        return None
    return random.choice(legal_actions)

# No need for observe_action function as random agent doesn't learn
