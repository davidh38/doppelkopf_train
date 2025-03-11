"""
Doppelkopf game implementation.
This module contains the rules and mechanics of the Doppelkopf card game.
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Any

# Constants for suits
SUIT_CLUBS = 1
SUIT_SPADES = 2
SUIT_HEARTS = 3
SUIT_DIAMONDS = 4

# Constants for ranks
RANK_NINE = 9
RANK_JACK = 11
RANK_QUEEN = 12
RANK_KING = 13
RANK_TEN = 10
RANK_ACE = 14

# Constants for game variants
VARIANT_NORMAL = 1
VARIANT_HOCHZEIT = 2
VARIANT_QUEEN_SOLO = 3
VARIANT_JACK_SOLO = 4
VARIANT_FLESHLESS = 5
VARIANT_KING_SOLO = 6

# Constants for player teams
TEAM_RE = 1
TEAM_KONTRA = 2
TEAM_UNKNOWN = 3

# Mapping dictionaries for display purposes
SUIT_NAMES = {
    SUIT_CLUBS: "CLUBS",
    SUIT_SPADES: "SPADES",
    SUIT_HEARTS: "HEARTS",
    SUIT_DIAMONDS: "DIAMONDS"
}

RANK_NAMES = {
    RANK_NINE: "NINE",
    RANK_JACK: "JACK",
    RANK_QUEEN: "QUEEN",
    RANK_KING: "KING",
    RANK_TEN: "TEN",
    RANK_ACE: "ACE"
}

VARIANT_NAMES = {
    VARIANT_NORMAL: "NORMAL",
    VARIANT_HOCHZEIT: "HOCHZEIT",
    VARIANT_QUEEN_SOLO: "QUEEN_SOLO",
    VARIANT_JACK_SOLO: "JACK_SOLO",
    VARIANT_FLESHLESS: "FLESHLESS",
    VARIANT_KING_SOLO: "KING_SOLO"
}

TEAM_NAMES = {
    TEAM_RE: "RE",
    TEAM_KONTRA: "KONTRA",
    TEAM_UNKNOWN: "UNKNOWN"
}

# Emoji mappings for suits
SUIT_EMOJIS = {
    SUIT_HEARTS: "♥️",
    SUIT_DIAMONDS: "♦️",
    SUIT_CLUBS: "♣️",
    SUIT_SPADES: "♠️"
}

# Emoji mappings for ranks
RANK_EMOJIS = {
    RANK_ACE: "🅰️",
    RANK_KING: "👑",
    RANK_QUEEN: "👸",
    RANK_JACK: "🤴",
    RANK_TEN: "🔟",
    RANK_NINE: "9️⃣"
}

def create_card(suit: int, rank: int, is_second: bool = False) -> Dict:
    """
    Create a card dictionary.
    
    Args:
        suit: The suit of the card
        rank: The rank of the card
        is_second: Whether this is the second copy of the card
        
    Returns:
        A dictionary representing the card
    """
    return {
        'suit': suit,
        'rank': rank,
        'is_second': is_second
    }

def card_to_string(card: Dict) -> str:
    """
    Convert a card to a string representation.
    
    Args:
        card: The card dictionary
        
    Returns:
        A string representation of the card
    """
    suit_emoji = SUIT_EMOJIS[card['suit']]
    rank_emoji = RANK_EMOJIS[card['rank']]
    
    # Create a compact emoji representation
    emoji_repr = f"{rank_emoji}{suit_emoji}"
    
    # Return both the emoji and the text representation
    return f"{emoji_repr} {RANK_NAMES[card['rank']]} of {SUIT_NAMES[card['suit']]}" + (" (2)" if card['is_second'] else "")

def cards_equal(card1: Dict, card2: Dict) -> bool:
    """
    Check if two cards are equal.
    
    Args:
        card1: The first card
        card2: The second card
        
    Returns:
        True if the cards are equal, False otherwise
    """
    return (card1['suit'] == card2['suit'] and 
            card1['rank'] == card2['rank'] and 
            card1['is_second'] == card2['is_second'])

def card_hash(card: Dict) -> int:
    """
    Get a hash value for a card.
    
    Args:
        card: The card dictionary
        
    Returns:
        A hash value for the card
    """
    return hash((card['suit'], card['rank'], card['is_second']))

def is_trump(card: Dict, game_variant: int) -> bool:
    """
    Check if a card is a trump card in the given game variant.
    
    Args:
        card: The card dictionary
        game_variant: The game variant
        
    Returns:
        True if the card is a trump, False otherwise
    """
    # In normal game and hochzeit (marriage)
    if game_variant == VARIANT_NORMAL or game_variant == VARIANT_HOCHZEIT:
        # Queens and Jacks are always trump
        if card['rank'] == RANK_QUEEN or card['rank'] == RANK_JACK:
            return True
        
        # Diamonds are trump
        if card['suit'] == SUIT_DIAMONDS:
            return True
            
        # Ten of Hearts is also trump
        if card['rank'] == RANK_TEN and card['suit'] == SUIT_HEARTS:
            return True
    
    # In Queen solo, only Queens are trump
    elif game_variant == VARIANT_QUEEN_SOLO:
        return card['rank'] == RANK_QUEEN
    
    # In Jack solo, only Jacks are trump
    elif game_variant == VARIANT_JACK_SOLO:
        return card['rank'] == RANK_JACK
        
    # In King solo, only Kings are trump
    elif game_variant == VARIANT_KING_SOLO:
        return card['rank'] == RANK_KING
        
    # In Fleshless, no Kings, Queens, or Jacks are trump
    elif game_variant == VARIANT_FLESHLESS:
        # Only Diamonds and Ten of Hearts are trump
        if card['suit'] == SUIT_DIAMONDS:
            return True
            
        if card['rank'] == RANK_TEN and card['suit'] == SUIT_HEARTS:
            return True
            
        # Kings, Queens, and Jacks are not trump
        if card['rank'] == RANK_KING or card['rank'] == RANK_QUEEN or card['rank'] == RANK_JACK:
            return False
            
        return False
        
    return False

def get_card_value(card: Dict) -> int:
    """
    Get the point value of a card.
    
    Args:
        card: The card dictionary
        
    Returns:
        The point value of the card
    """
    if card['rank'] == RANK_ACE:
        return 11
    elif card['rank'] == RANK_TEN:
        return 10
    elif card['rank'] == RANK_KING:
        return 4
    elif card['rank'] == RANK_QUEEN:
        return 3
    elif card['rank'] == RANK_JACK:
        return 2
    else:  # NINE
        return 0

def get_card_order_value(card: Dict, game_variant: int) -> int:
    """
    Get the order value of a card for comparison.
    Higher value means stronger card.
    
    Args:
        card: The card dictionary
        game_variant: The game variant
        
    Returns:
        The order value of the card
    """
    if not is_trump(card, game_variant):
        # Non-trump cards
        return card['rank']
    
    # Trump cards have a special order
    if card['rank'] == RANK_TEN and card['suit'] == SUIT_HEARTS:
        # Ten of Hearts is the highest trump
        base = 120
    elif card['rank'] == RANK_QUEEN:
        base = 100
    elif card['rank'] == RANK_JACK:
        base = 80
    else:  # Diamond cards in normal game
        base = 60
        
    # Add suit value for ordering within same rank
    suit_value = 4 - card['suit']  # Clubs highest, Diamonds lowest
    
    return base + suit_value

def create_game_state() -> Dict:
    """
    Create a new game state.
    
    Returns:
        A dictionary representing the game state
    """
    state = {
        'num_players': 4,
        'deck': [],
        'hands': [[] for _ in range(4)],
        'tricks': [],
        'current_trick': [],
        'current_player': 0,  # This will be overridden in game_management.py
        'game_variant': VARIANT_NORMAL,
        'scores': [0, 0],  # [RE score, KONTRA score]
        'player_scores': [0, 0, 0, 0],  # Individual player scores
        'teams': [TEAM_UNKNOWN] * 4,
        'trick_winner': None,
        'game_over': False,
        'players_with_hochzeit': set(),  # Cache for players who have hochzeit
        'card_giver': 0,  # Player who is the card giver (will be set in game_management.py)
        
        # Variant selection phase
        'variant_selection_phase': True,
        'player_variant_choices': [None] * 4,  # Track each player's variant choice
        'variant_priority': {
            'fleshless': 1,   # Highest priority
            'king_solo': 2,
            'queen_solo': 3,
            'jack_solo': 4,   # This is the trump solo
            'hochzeit': 5,
            'normal': 6,      # Lowest priority
        },
        
        # Announcement tracking
        're_announced': False,
        'contra_announced': False,
        'can_announce': True  # Can announce until the fifth card is played
    }
    
    # Create a deck of cards (2 copies of each card)
    for suit in [SUIT_CLUBS, SUIT_SPADES, SUIT_HEARTS, SUIT_DIAMONDS]:
        for rank in [RANK_NINE, RANK_JACK, RANK_QUEEN, RANK_KING, RANK_TEN, RANK_ACE]:
            # Skip Nine cards
            if rank != RANK_NINE:
                state['deck'].append(create_card(suit, rank, False))
                state['deck'].append(create_card(suit, rank, True))
    
    # Deal cards
    deal_cards(state)
    
    # Determine teams based on Queens of Clubs
    determine_teams(state)
    
    # Cache hochzeit status for each player
    cache_hochzeit_status(state)
    
    return state

def deal_cards(state: Dict) -> None:
    """
    Deal cards to players.
    
    Args:
        state: The game state
    """
    random.shuffle(state['deck'])
    cards_per_player = len(state['deck']) // state['num_players']
    
    for i in range(state['num_players']):
        state['hands'][i] = state['deck'][i * cards_per_player:(i + 1) * cards_per_player]

def determine_teams(state: Dict) -> None:
    """
    Determine which players are on which team based on Queens of Clubs.
    
    Args:
        state: The game state
    """
    queens_of_clubs = [
        create_card(SUIT_CLUBS, RANK_QUEEN, False), 
        create_card(SUIT_CLUBS, RANK_QUEEN, True)
    ]
    
    for i, hand in enumerate(state['hands']):
        if any(cards_equal(card, queen) for card in hand for queen in queens_of_clubs):
            state['teams'][i] = TEAM_RE
        else:
            state['teams'][i] = TEAM_KONTRA

def cache_hochzeit_status(state: Dict) -> None:
    """
    Cache which players have hochzeit (both Queens of Clubs).
    
    Args:
        state: The game state
    """
    queens_of_clubs = [
        create_card(SUIT_CLUBS, RANK_QUEEN, False), 
        create_card(SUIT_CLUBS, RANK_QUEEN, True)
    ]
    state['players_with_hochzeit'].clear()
    
    for player_idx in range(state['num_players']):
        if all(any(cards_equal(card, queen) for card in state['hands'][player_idx]) for queen in queens_of_clubs):
            state['players_with_hochzeit'].add(player_idx)

def has_hochzeit(state: Dict, player_idx: int) -> bool:
    """
    Check if the player has both Queens of Clubs (Hochzeit/Marriage).
    
    Args:
        state: The game state
        player_idx: Index of the player
        
    Returns:
        True if the player has both Queens of Clubs, False otherwise
    """
    return player_idx in state['players_with_hochzeit']

def get_legal_actions(state: Dict, player_idx: int) -> List[Dict]:
    """
    Get the legal actions (cards that can be played) for the given player.
    
    Args:
        state: The game state
        player_idx: Index of the player
        
    Returns:
        List of legal cards to play
    """
    # Cannot play cards during variant selection phase
    if state['variant_selection_phase']:
        return []
        
    if player_idx != state['current_player'] or state['game_over']:
        return []
    
    hand = state['hands'][player_idx]
    
    # If this is the first card in the trick, any card can be played
    if not state['current_trick']:
        return hand.copy()
    
    # Otherwise, must follow suit if possible
    lead_card = state['current_trick'][0]
    lead_suit = lead_card['suit']
    
    # Check if the lead card is trump
    lead_is_trump = is_trump(lead_card, state['game_variant'])
    
    # Find cards of the same type (trump or same suit)
    matching_cards = []
    for card in hand:
        card_is_trump = is_trump(card, state['game_variant'])
        
        if lead_is_trump and card_is_trump:
            matching_cards.append(card)
        elif not lead_is_trump and not card_is_trump and card['suit'] == lead_suit:
            matching_cards.append(card)
    
    # If player has matching cards, they must play one
    if matching_cards:
        return matching_cards
    
    # Otherwise, any card can be played
    return hand.copy()

def play_card(state: Dict, player_idx: int, card: Dict) -> bool:
    """
    Play a card for the given player.
    
    Args:
        state: The game state
        player_idx: Index of the player
        card: The card to play
        
    Returns:
        True if the move was legal and executed, False otherwise
    """
    # Cannot play cards during variant selection phase
    if state['variant_selection_phase']:
        return False
        
    if player_idx != state['current_player'] or state['game_over']:
        return False
    
    legal_actions = get_legal_actions(state, player_idx)
    if not any(cards_equal(card, legal_card) for legal_card in legal_actions):
        return False
    
    # Remove the card from the player's hand
    state['hands'][player_idx] = [c for c in state['hands'][player_idx] if not cards_equal(c, card)]
    
    # If the card is a Queen of Clubs, update hochzeit cache
    if card['suit'] == SUIT_CLUBS and card['rank'] == RANK_QUEEN and player_idx in state['players_with_hochzeit']:
        # Player no longer has both Queens of Clubs
        state['players_with_hochzeit'].discard(player_idx)
    
    # Add the card to the current trick
    state['current_trick'].append(card)
    
    # Move to the next player
    state['current_player'] = (state['current_player'] + 1) % state['num_players']
    
    # If the trick is complete, determine the winner
    if len(state['current_trick']) == state['num_players']:
        complete_trick(state)
    
    # Check if the game is over
    if all(len(hand) == 0 for hand in state['hands']):
        end_game(state)
    
    # Update announcement eligibility
    # Can announce until the fifth card is played
    cards_played = len(state['current_trick'])
    for trick in state['tricks']:
        cards_played += len(trick)
    state['can_announce'] = cards_played < 5
    
    return True

def announce(state: Dict, player_idx: int, announcement: str) -> bool:
    """
    Make an announcement (Re, Contra, or Hochzeit).
    
    Args:
        state: The game state
        player_idx: Index of the player
        announcement: The announcement to make ('re', 'contra', or 'hochzeit')
        
    Returns:
        True if the announcement was legal and executed, False otherwise
    """
    # Cannot announce during variant selection phase
    if state['variant_selection_phase']:
        return False
        
    # Cannot announce if not allowed
    if not state['can_announce']:
        return False
    
    # Handle hochzeit announcement
    if announcement == 'hochzeit':
        # Check if the player has both Queens of Clubs
        if has_hochzeit(state, player_idx):
            # Set the game variant to Hochzeit
            state['game_variant'] = VARIANT_HOCHZEIT
            return True
        return False
    
    # Check if the player is in the appropriate team for the announcement
    player_team = state['teams'][player_idx]
    
    if announcement == 're' and player_team != TEAM_RE:
        return False
    elif announcement == 'contra' and player_team != TEAM_KONTRA:
        return False
    
    # Check if the announcement has already been made
    if announcement == 're' and state['re_announced']:
        return False
    elif announcement == 'contra' and state['contra_announced']:
        return False
    
    # Make the announcement
    if announcement == 're':
        state['re_announced'] = True
    else:  # 'contra'
        state['contra_announced'] = True
    
    return True

def set_variant(state: Dict, variant: str, player_idx: int = None) -> bool:
    """
    Set the game variant for a player.
    
    Args:
        state: The game state
        variant: The variant to set ('normal', 'hochzeit', 'queen_solo', 'jack_solo', 'fleshless')
        player_idx: Index of the player making the choice (if None, uses current_player)
        
    Returns:
        True if the variant was set, False otherwise
    """
    # Can only set variant during variant selection phase
    if not state['variant_selection_phase']:
        return False
    
    # Use current player if player_idx is not provided
    if player_idx is None:
        player_idx = state['current_player']
        
    # Validate the variant
    valid_variant = False
    variant_enum = None
    
    if variant == 'normal':
        valid_variant = True
        variant_enum = VARIANT_NORMAL
        variant_key = 'normal'
    elif variant == 'hochzeit':
        valid_variant = True
        variant_enum = VARIANT_HOCHZEIT
        variant_key = 'hochzeit'
    elif variant == 'queen_solo':
        valid_variant = True
        variant_enum = VARIANT_QUEEN_SOLO
        variant_key = 'queen_solo'
    elif variant == 'jack_solo':
        valid_variant = True
        variant_enum = VARIANT_JACK_SOLO
        variant_key = 'jack_solo'
    elif variant == 'fleshless':
        valid_variant = True
        variant_enum = VARIANT_FLESHLESS
        variant_key = 'fleshless'
    elif variant == 'king_solo':
        valid_variant = True
        variant_enum = VARIANT_KING_SOLO
        variant_key = 'king_solo'
    elif variant == 'trump_solo':  # This is not implemented yet, but included for priority
        valid_variant = True
        variant_enum = VARIANT_NORMAL  # Fallback to normal for now
        variant_key = 'trump_solo'
        
    if not valid_variant:
        return False
        
    # Record the player's choice
    state['player_variant_choices'][player_idx] = variant_key
    
    # Move to the next player
    state['current_player'] = (state['current_player'] + 1) % state['num_players']
    
    # Check if all players have made a choice
    if all(choice is not None for choice in state['player_variant_choices']):
        # Determine the final game variant based on choices
        determine_final_variant(state)
        
        # End variant selection phase
        state['variant_selection_phase'] = False
        
        # Reset the current player to be the player next to the card giver
        # This ensures the correct player starts the first trick
        state['current_player'] = (state['card_giver'] + 1) % state['num_players']
        
    return True

def determine_final_variant(state: Dict) -> None:
    """
    Determine the final game variant based on player choices.
    
    Args:
        state: The game state
    """
    # Count the occurrences of each variant
    variant_counts = {}
    for choice in state['player_variant_choices']:
        if choice in variant_counts:
            variant_counts[choice] += 1
        else:
            variant_counts[choice] = 1
    
    # Track which player chose each variant
    state['variant_choosers'] = {}
    for player_idx, choice in enumerate(state['player_variant_choices']):
        if choice not in state['variant_choosers']:
            state['variant_choosers'][choice] = []
        state['variant_choosers'][choice].append(player_idx)
            
    # If everyone chose normal, play normal
    if len(variant_counts) == 1 and 'normal' in variant_counts:
        state['game_variant'] = VARIANT_NORMAL
        # Use standard team determination for normal games
        reassign_teams(state)
        return
        
    # If only one player chose a non-normal variant, play that variant
    non_normal_variants = [v for v in state['player_variant_choices'] if v != 'normal' and v != 'hochzeit']
    if len(set(non_normal_variants)) == 1 and len(non_normal_variants) == 1:
        variant = non_normal_variants[0]
        if variant == 'queen_solo':
            state['game_variant'] = VARIANT_QUEEN_SOLO
        elif variant == 'jack_solo':
            state['game_variant'] = VARIANT_JACK_SOLO
        elif variant == 'king_solo':
            state['game_variant'] = VARIANT_KING_SOLO
        elif variant == 'fleshless':
            state['game_variant'] = VARIANT_FLESHLESS
        elif variant == 'trump_solo':
            state['game_variant'] = VARIANT_NORMAL  # Fallback to normal for now
        
        # Reassign teams based on the solo variant
        reassign_teams(state)
        return
        
    # If multiple players chose different non-normal variants, use priority
    if len(set(non_normal_variants)) > 1:
        # Find the variant with the highest priority (lowest priority number)
        highest_priority_variant = None
        highest_priority = float('inf')
        
        for variant in set(non_normal_variants):
            priority = state['variant_priority'].get(variant, float('inf'))
            if priority < highest_priority:
                highest_priority = priority
                highest_priority_variant = variant
                
        if highest_priority_variant == 'queen_solo':
            state['game_variant'] = VARIANT_QUEEN_SOLO
        elif highest_priority_variant == 'jack_solo':
            state['game_variant'] = VARIANT_JACK_SOLO
        elif highest_priority_variant == 'king_solo':
            state['game_variant'] = VARIANT_KING_SOLO
        elif highest_priority_variant == 'fleshless':
            state['game_variant'] = VARIANT_FLESHLESS
        elif highest_priority_variant == 'trump_solo':
            state['game_variant'] = VARIANT_NORMAL  # Fallback to normal for now
        
        # Reassign teams based on the solo variant
        reassign_teams(state)
        return
    
    # Check for hochzeit variant
    if 'hochzeit' in variant_counts:
        state['game_variant'] = VARIANT_HOCHZEIT
        # Initialize hochzeit-specific state
        state['hochzeit_active'] = True
        state['hochzeit_non_trump_trick_played'] = False
        state['hochzeit_partner'] = None
        
        # Reassign teams based on hochzeit variant
        reassign_teams(state)
        return
        
    # Default to normal game
    state['game_variant'] = VARIANT_NORMAL
    # Use standard team determination for normal games
    reassign_teams(state)

def reassign_teams(state: Dict) -> None:
    """
    Reassign teams based on the game variant.
    
    Args:
        state: The game state
    """
    # For solo variants, the player who chose the solo variant is on team RE, all others on team KONTRA
    if state['game_variant'] in [VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_KING_SOLO, VARIANT_FLESHLESS]:
        # Find the player who chose the solo variant
        solo_player = None
        solo_variants = ['queen_solo', 'jack_solo', 'king_solo', 'fleshless']
        
        for variant in solo_variants:
            if variant in state['variant_choosers'] and state['variant_choosers'][variant]:
                solo_player = state['variant_choosers'][variant][0]  # Take the first player who chose this variant
                break
        
        if solo_player is not None:
            # Assign the solo player to team RE, all others to team KONTRA
            for i in range(state['num_players']):
                if i == solo_player:
                    state['teams'][i] = TEAM_RE
                else:
                    state['teams'][i] = TEAM_KONTRA
        else:
            # Fallback to standard team determination if no solo player found
            determine_teams(state)
    
    # For hochzeit variant, the player who chose hochzeit is on team RE
    # The partner will be determined when a non-trump trick is won
    elif state['game_variant'] == VARIANT_HOCHZEIT:
        # Find the player(s) who chose hochzeit
        if 'hochzeit' in state['variant_choosers'] and state['variant_choosers']['hochzeit']:
            hochzeit_player = state['variant_choosers']['hochzeit'][0]  # Take the first player who chose hochzeit
            
            # Initially assign the hochzeit player to team RE, all others to team KONTRA
            for i in range(state['num_players']):
                if i == hochzeit_player:
                    state['teams'][i] = TEAM_RE
                else:
                    state['teams'][i] = TEAM_KONTRA
        else:
            # Fallback to standard team determination if no hochzeit player found
            determine_teams(state)
    
    # For normal games, use the standard team determination based on Queens of Clubs
    else:
        determine_teams(state)

def complete_trick(state: Dict) -> None:
    """
    Complete the current trick and determine the winner.
    
    Args:
        state: The game state
    """
    # Determine the winner of the trick
    lead_card = state['current_trick'][0]
    lead_is_trump = is_trump(lead_card, state['game_variant'])
    
    # Find the highest card of the same type
    highest_card_idx = 0
    highest_card_value = get_card_order_value(lead_card, state['game_variant'])
    
    for i in range(1, len(state['current_trick'])):
        card = state['current_trick'][i]
        card_is_trump = is_trump(card, state['game_variant'])
        
        # Trump beats non-trump
        if card_is_trump and not lead_is_trump:
            highest_card_idx = i
            highest_card_value = get_card_order_value(card, state['game_variant'])
            lead_is_trump = True
        # Compare cards of the same type
        elif card_is_trump == lead_is_trump:
            if card_is_trump or card['suit'] == lead_card['suit']:
                card_value = get_card_order_value(card, state['game_variant'])
                if card_value > highest_card_value:
                    highest_card_idx = i
                    highest_card_value = card_value
    
    # The winner is the player who played the highest card
    trick_winner = (state['current_player'] - (state['num_players'] - highest_card_idx)) % state['num_players']
    state['trick_winner'] = trick_winner
    
    # Handle hochzeit partner determination
    if state['game_variant'] == VARIANT_HOCHZEIT and state.get('hochzeit_active', False):
        # Check if this is a non-trump trick (no trump cards played)
        is_non_trump_trick = True
        for card in state['current_trick']:
            if is_trump(card, state['game_variant']):
                is_non_trump_trick = False
                break
        
        # If this is a non-trump trick and the winner is not already on team RE
        if is_non_trump_trick and state['teams'][trick_winner] != TEAM_RE:
            # This player becomes the hochzeit partner
            state['teams'][trick_winner] = TEAM_RE
            state['hochzeit_partner'] = trick_winner
            state['hochzeit_non_trump_trick_played'] = True
            state['hochzeit_active'] = False  # Hochzeit is resolved
    
    # Add the trick to the list of completed tricks
    state['tricks'].append(state['current_trick'].copy())
    
    # Calculate points for the trick
    trick_points = sum(get_card_value(card) for card in state['current_trick'])
    
    # Check for Diamond Ace capture in normal or hochzeit game
    diamond_ace_bonus = 0
    diamond_aces_captured = []
    
    if (state['game_variant'] == VARIANT_NORMAL or state['game_variant'] == VARIANT_HOCHZEIT):
        # Check if there are Diamond Aces in the trick
        for i, card in enumerate(state['current_trick']):
            if card['suit'] == SUIT_DIAMONDS and card['rank'] == RANK_ACE:
                # Calculate which player played this card
                card_player = (state['current_player'] - (state['num_players'] - i)) % state['num_players']
                # Check if the card player's team is different from the trick winner's team
                if state['teams'][card_player] != state['teams'][state['trick_winner']]:
                    # Award a bonus point for capturing opponent's Diamond Ace
                    diamond_ace_bonus += 1
                    # Store information about this Diamond Ace capture
                    diamond_aces_captured.append({
                        'winner': state['trick_winner'],
                        'winner_team': TEAM_NAMES[state['teams'][state['trick_winner']]],
                        'loser': card_player,
                        'loser_team': TEAM_NAMES[state['teams'][card_player]],
                        'is_second': card['is_second'],  # Track which copy of the Diamond Ace
                        'type': 'diamond_ace'
                    })
    
    # Check for 40+ point trick
    forty_plus_bonus = 0
    if trick_points >= 40:
        # Award a bonus point for a 40+ point trick
        forty_plus_bonus = 1
        # Store information about the 40+ point trick
        if 'special_tricks' not in state:
            state['special_tricks'] = []
        
        state['special_tricks'].append({
            'winner': state['trick_winner'],
            'winner_team': TEAM_NAMES[state['teams'][state['trick_winner']]],
            'points': trick_points,
            'type': 'forty_plus'
        })
    
    # Store information about Diamond Ace captures if any occurred
    if diamond_aces_captured:
        state['diamond_ace_captured'] = diamond_aces_captured
        
    # Store information about the 40+ point trick if it occurred
    if forty_plus_bonus > 0:
        # If we already have diamond_ace_captured, add the 40+ trick to it
        if 'diamond_ace_captured' in state:
            # Add a special entry for the 40+ trick
            state['diamond_ace_captured'].append({
                'winner': state['trick_winner'],
                'winner_team': TEAM_NAMES[state['teams'][state['trick_winner']]],
                'points': trick_points,
                'type': 'forty_plus'
            })
        else:
            # Create a new list with just the 40+ trick
            state['diamond_ace_captured'] = [{
                'winner': state['trick_winner'],
                'winner_team': TEAM_NAMES[state['teams'][state['trick_winner']]],
                'points': trick_points,
                'type': 'forty_plus'
            }]
    
    # Add points to the winner's team
    winner_team = state['teams'][state['trick_winner']]
    if winner_team == TEAM_RE:
        state['scores'][0] += trick_points
        # Add bonus points for Diamond Ace capture
        if diamond_ace_bonus > 0:
            state['scores'][0] += diamond_ace_bonus
            # Subtract from the other team
            state['scores'][1] -= diamond_ace_bonus
        # Add bonus point for 40+ point trick (zero-sum)
        if forty_plus_bonus > 0:
            state['scores'][0] += forty_plus_bonus
            # Subtract from the other team to keep total at 240
            state['scores'][1] -= forty_plus_bonus
    else:
        state['scores'][1] += trick_points
        # Add bonus points for Diamond Ace capture
        if diamond_ace_bonus > 0:
            state['scores'][1] += diamond_ace_bonus
            # Subtract from the other team
            state['scores'][0] -= diamond_ace_bonus
        # Add bonus point for 40+ point trick (zero-sum)
        if forty_plus_bonus > 0:
            state['scores'][1] += forty_plus_bonus
            # Subtract from the other team to keep total at 240
            state['scores'][0] -= forty_plus_bonus
        
    # Add points to the individual player's score
    state['player_scores'][state['trick_winner']] += trick_points
    
    # Add bonus points for Diamond Ace capture to all players on the winner's team
    if diamond_ace_bonus > 0:
        winner_team = state['teams'][state['trick_winner']]
        for i, team in enumerate(state['teams']):
            if team == winner_team:
                state['player_scores'][i] += diamond_ace_bonus
        
    # Add bonus point for 40+ point trick to all players on the winner's team
    if forty_plus_bonus > 0:
        winner_team = state['teams'][state['trick_winner']]
        for i, team in enumerate(state['teams']):
            if team == winner_team:
                state['player_scores'][i] += forty_plus_bonus
    
    # Store the last trick points for display
    state['last_trick_points'] = trick_points
    # Store the Diamond Ace bonus for display
    state['last_trick_diamond_ace_bonus'] = diamond_ace_bonus
    
    # The current_player will be updated to the trick winner when the trick is cleared
    # This is handled by the server after a delay to show the completed trick

def end_game(state: Dict) -> None:
    """
    End the game and calculate final scores.
    
    Args:
        state: The game state
    """
    state['game_over'] = True
    
    # Determine the winner based on scores
    re_score = state['scores'][0]
    kontra_score = state['scores'][1]
    
    # In normal game, RE team needs 121 points to win
    if re_score >= 121:
        state['winner'] = TEAM_RE
    else:
        state['winner'] = TEAM_KONTRA
    
    # Initialize player_game_points if it doesn't exist
    state['player_game_points'] = [0, 0, 0, 0]
    
    # Determine the winning and losing teams
    winning_team = state['winner']
    losing_team = TEAM_KONTRA if winning_team == TEAM_RE else TEAM_RE
    
    # Handle special variants
    if state['game_variant'] in [VARIANT_QUEEN_SOLO, VARIANT_JACK_SOLO, VARIANT_KING_SOLO, VARIANT_FLESHLESS]:
        # Find the player who chose the solo variant
        solo_player = None
        for i, choice in enumerate(state['player_variant_choices']):
            if choice in ['queen_solo', 'jack_solo', 'king_solo', 'fleshless']:
                solo_player = i
                break
        
        if solo_player is not None:
            # The solo player is always on the RE team
            if state['winner'] == TEAM_RE:
                # Solo player wins
                state['solo_winner'] = True
                
                # Calculate points for solo win
                # Base points: 3 (one for each opponent)
                base_points = 3
                
                # Double points if RE was announced
                if state.get('re_announced', False):
                    base_points *= 2
                
                # Award points to solo player
                state['player_game_points'][solo_player] = base_points
                
                # Each opponent gets negative points
                opponent_points = -base_points / 3  # Divide by number of opponents
                for i in range(len(state['teams'])):
                    if i != solo_player:
                        state['player_game_points'][i] = opponent_points
            else:
                # Solo player loses
                state['solo_winner'] = False
                
                # Calculate points for solo loss
                # Base points: 3 (one for each opponent)
                base_points = 3
                
                # Double points if RE was announced
                if state.get('re_announced', False):
                    base_points *= 2
                
                # Solo player gets negative points
                state['player_game_points'][solo_player] = -base_points
                
                # Each opponent gets positive points
                opponent_points = base_points / 3  # Divide by number of opponents
                for i in range(len(state['teams'])):
                    if i != solo_player:
                        state['player_game_points'][i] = opponent_points
    else:
        # Normal game - award positive points to winning team and negative points to losing team
        # This implements a zero-sum approach for game points
        for i, team in enumerate(state['teams']):
            if team == winning_team:
                state['player_game_points'][i] = 1  # Positive points for winners
            elif team == losing_team:
                state['player_game_points'][i] = -1  # Negative points for losers

def get_state_for_player(state: Dict, player_idx: int) -> List[float]:
    """
    Get a state representation for a specific player.
    
    Args:
        state: The game state
        player_idx: Index of the player
        
    Returns:
        A list of floats representing the state
    """
    # Initialize state representation
    state_repr = []
    
    # Add player's hand
    hand = state['hands'][player_idx]
    # One-hot encoding for each possible card (24 cards * 2 copies = 48 cards)
    hand_repr = [0] * 48
    for card in hand:
        card_idx = card_to_idx(card)
        hand_repr[card_idx] = 1
    state_repr.extend(hand_repr)
    
    # Add current trick
    trick = state['current_trick']
    # One-hot encoding for each card in the trick
    trick_repr = [0] * 48
    for card in trick:
        card_idx = card_to_idx(card)
        trick_repr[card_idx] = 1
    state_repr.extend(trick_repr)
    
    # Add played cards
    played_cards = []
    for past_trick in state['tricks']:
        played_cards.extend(past_trick)
    # One-hot encoding for each played card
    played_repr = [0] * 48
    for card in played_cards:
        card_idx = card_to_idx(card)
        played_repr[card_idx] = 1
    state_repr.extend(played_repr)
    
    # Add game variant
    variant_repr = [0] * 6  # 6 possible variants
    variant_repr[state['game_variant'] - 1] = 1  # -1 because variants start at 1
    state_repr.extend(variant_repr)
    
    # Add player's team
    team_repr = [0] * 3  # 3 possible teams
    team_repr[state['teams'][player_idx] - 1] = 1  # -1 because teams start at 1
    state_repr.extend(team_repr)
    
    # Add current player
    current_player_repr = [0] * 4  # 4 players
    current_player_repr[state['current_player']] = 1
    state_repr.extend(current_player_repr)
    
    # Add scores
    state_repr.append(state['scores'][0] / 240.0)  # Normalize RE score
    state_repr.append(state['scores'][1] / 240.0)  # Normalize KONTRA score
    
    # Add announcements
    state_repr.append(1.0 if state.get('re_announced', False) else 0.0)
    state_repr.append(1.0 if state.get('contra_announced', False) else 0.0)
    
    return state_repr

def card_to_idx(card: Dict) -> int:
    """
    Convert a card to an index.
    
    Args:
        card: The card dictionary
        
    Returns:
        An index representing the card
    """
    # Calculate base index based on suit and rank
    # Each suit has 6 ranks (9, J, Q, K, 10, A), and each rank has 2 copies
    suit_offset = (card['suit'] - 1) * 12  # 12 cards per suit (6 ranks * 2 copies)
    rank_offset = 0
    
    # Map rank to offset
    if card['rank'] == RANK_NINE:
        rank_offset = 0
    elif card['rank'] == RANK_JACK:
        rank_offset = 2
    elif card['rank'] == RANK_QUEEN:
        rank_offset = 4
    elif card['rank'] == RANK_KING:
        rank_offset = 6
    elif card['rank'] == RANK_TEN:
        rank_offset = 8
    elif card['rank'] == RANK_ACE:
        rank_offset = 10
    
    # Add 1 if it's the second copy
    copy_offset = 1 if card['is_second'] else 0
    
    return suit_offset + rank_offset + copy_offset

def get_state_size() -> int:
    """
    Get the size of the state representation.
    
    Returns:
        The size of the state representation
    """
    # Hand representation: 48 cards (one-hot encoding)
    hand_size = 48
    
    # Current trick representation: 48 cards (one-hot encoding)
    trick_size = 48
    
    # Played cards representation: 48 cards (one-hot encoding)
    played_size = 48
    
    # Game variant representation: 6 variants (one-hot encoding)
    variant_size = 6
    
    # Team representation: 3 teams (one-hot encoding)
    team_size = 3
    
    # Current player representation: 4 players (one-hot encoding)
    current_player_size = 4
    
    # Scores representation: 2 scores (normalized)
    scores_size = 2
    
    # Announcements representation: 2 announcements (re, contra)
    announcements_size = 2
    
    # Total state size
    return hand_size + trick_size + played_size + variant_size + team_size + current_player_size + scores_size + announcements_size

def get_action_size() -> int:
    """
    Get the size of the action space.
    
    Returns:
        The size of the action space
    """
    # Card actions: 48 cards (4 suits * 6 ranks * 2 copies)
    return 48

def idx_to_card(idx: int) -> Dict:
    """
    Convert an index to a card.
    
    Args:
        idx: The index to convert
        
    Returns:
        The corresponding card
    """
    # Each suit has 12 cards (6 ranks * 2 copies)
    suit_idx = idx // 12 + 1  # +1 because suits start at 1
    
    # Calculate the rank and copy within the suit
    rank_copy_idx = idx % 12
    
    # Determine the rank
    rank = 0
    if rank_copy_idx < 2:
        rank = RANK_NINE
    elif rank_copy_idx < 4:
        rank = RANK_JACK
    elif rank_copy_idx < 6:
        rank = RANK_QUEEN
    elif rank_copy_idx < 8:
        rank = RANK_KING
    elif rank_copy_idx < 10:
        rank = RANK_TEN
    else:
        rank = RANK_ACE
    
    # Determine if it's the second copy
    is_second = rank_copy_idx % 2 == 1
    
    return create_card(suit_idx, rank, is_second)

def action_to_card(state: Dict, action: int, player_idx: int) -> Optional[Dict]:
    """
    Convert an action index to a card for the given player.
    
    Args:
        state: The game state
        action: The action index
        player_idx: Index of the player
        
    Returns:
        The corresponding card, or None if the action is invalid
    """
    # Convert the action index to a card
    card = idx_to_card(action)
    
    # Check if the card is in the player's hand
    hand = state['hands'][player_idx]
    for hand_card in hand:
        if cards_equal(card, hand_card):
            return hand_card
    
    # Card not in hand
    return None
