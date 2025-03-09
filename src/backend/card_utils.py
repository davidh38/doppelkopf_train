#!/usr/bin/env python3
"""
Utility functions for card operations in the Doppelkopf game.
"""

def cards_equal(card1, card2):
    """
    Compare two cards for equality.
    
    Args:
        card1: First card to compare
        card2: Second card to compare
        
    Returns:
        bool: True if the cards are equal, False otherwise
    """
    return (card1['suit'] == card2['suit'] and 
            card1['rank'] == card2['rank'] and 
            card1['is_second'] == card2['is_second'])
