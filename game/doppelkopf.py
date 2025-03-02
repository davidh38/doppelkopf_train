"""
Doppelkopf game implementation.
This module contains the rules and mechanics of the Doppelkopf card game.
"""

import random
import numpy as np
from enum import Enum, auto
from typing import List, Tuple, Dict, Optional, Set

class Suit(Enum):
    """Card suits in Doppelkopf."""
    CLUBS = auto()
    SPADES = auto()
    HEARTS = auto()
    DIAMONDS = auto()
    
    def __str__(self):
        return self.name.capitalize()

class Rank(Enum):
    """Card ranks in Doppelkopf."""
    NINE = 9
    JACK = 11
    QUEEN = 12
    KING = 13
    TEN = 10
    ACE = 14
    
    def __str__(self):
        return self.name.capitalize()

class Card:
    """A playing card in Doppelkopf."""
    
    def __init__(self, suit: Suit, rank: Rank, is_second: bool = False):
        """
        Initialize a card.
        
        Args:
            suit: The suit of the card
            rank: The rank of the card
            is_second: Whether this is the second copy of the card (Doppelkopf has two of each card)
        """
        self.suit = suit
        self.rank = rank
        self.is_second = is_second
        
    def __str__(self):
        # Emoji mappings for suits
        suit_emojis = {
            Suit.HEARTS: "♥️",
            Suit.DIAMONDS: "♦️",
            Suit.CLUBS: "♣️",
            Suit.SPADES: "♠️"
        }
        
        # Emoji mappings for ranks
        rank_emojis = {
            Rank.ACE: "🅰️",
            Rank.KING: "👑",
            Rank.QUEEN: "👸",
            Rank.JACK: "🤴",
            Rank.TEN: "🔟",
            Rank.NINE: "9️⃣"
        }
        
        # Get the emoji representations
        suit_emoji = suit_emojis[self.suit]
        rank_emoji = rank_emojis[self.rank]
        
        # Create a compact emoji representation
        emoji_repr = f"{rank_emoji}{suit_emoji}"
        
        # Return both the emoji and the text representation
        return f"{emoji_repr} {self.rank} of {self.suit}" + (" (2)" if self.is_second else "")
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return (self.suit == other.suit and 
                self.rank == other.rank and 
                self.is_second == other.is_second)
    
    def __hash__(self):
        return hash((self.suit, self.rank, self.is_second))
    
    def is_trump(self, game_variant: 'GameVariant') -> bool:
        """Check if this card is a trump card in the given game variant."""
        # In normal game and hochzeit (marriage)
        if game_variant == GameVariant.NORMAL or game_variant == GameVariant.HOCHZEIT:
            # Queens and Jacks are always trump
            if self.rank == Rank.QUEEN or self.rank == Rank.JACK:
                return True
            
            # Diamonds are trump
            if self.suit == Suit.DIAMONDS:
                return True
                
            # Ten of Hearts is also trump
            if self.rank == Rank.TEN and self.suit == Suit.HEARTS:
                return True
        
        # In Queen solo, only Queens are trump
        elif game_variant == GameVariant.QUEEN_SOLO:
            return self.rank == Rank.QUEEN
        
        # In Jack solo, only Jacks are trump
        elif game_variant == GameVariant.JACK_SOLO:
            return self.rank == Rank.JACK
            
        # In Fleshless, no Kings, Queens, or Jacks are trump
        elif game_variant == GameVariant.FLESHLESS:
            # Only Diamonds and Ten of Hearts are trump
            if self.suit == Suit.DIAMONDS:
                return True
                
            if self.rank == Rank.TEN and self.suit == Suit.HEARTS:
                return True
                
            # Kings, Queens, and Jacks are not trump
            if self.rank == Rank.KING or self.rank == Rank.QUEEN or self.rank == Rank.JACK:
                return False
                
            return False
            
        return False
    
    def get_value(self) -> int:
        """Get the point value of this card."""
        if self.rank == Rank.ACE:
            return 11
        elif self.rank == Rank.TEN:
            return 10
        elif self.rank == Rank.KING:
            return 4
        elif self.rank == Rank.QUEEN:
            return 3
        elif self.rank == Rank.JACK:
            return 2
        else:  # NINE
            return 0
    
    def get_order_value(self, game_variant: 'GameVariant') -> int:
        """
        Get the order value of this card for comparison.
        Higher value means stronger card.
        """
        if not self.is_trump(game_variant):
            # Non-trump cards
            return self.rank.value
        
        # Trump cards have a special order
        if self.rank == Rank.TEN and self.suit == Suit.HEARTS:
            # Ten of Hearts is the highest trump
            base = 120
        elif self.rank == Rank.QUEEN:
            base = 100
        elif self.rank == Rank.JACK:
            base = 80
        else:  # Diamond cards in normal game
            base = 60
            
        # Add suit value for ordering within same rank
        suit_value = 4 - self.suit.value  # Clubs highest, Diamonds lowest
        
        return base + suit_value

class GameVariant(Enum):
    """Different variants of Doppelkopf game."""
    NORMAL = auto()  # Normal game with diamonds as trump
    HOCHZEIT = auto()  # Marriage - player with both Queens of Clubs announces partnership
    QUEEN_SOLO = auto()  # Solo game where only Queens are trump
    JACK_SOLO = auto()  # Solo game where only Jacks are trump
    FLESHLESS = auto()  # Fleshless - no Kings, Queens, or Jacks are trump

class PlayerTeam(Enum):
    """Teams in Doppelkopf."""
    RE = auto()  # Players with Queens of Clubs
    KONTRA = auto()  # Players without Queens of Clubs
    UNKNOWN = auto()  # Team not yet revealed

class DoppelkopfGame:
    """Implementation of the Doppelkopf card game."""
    
    def __init__(self):
        """Initialize a new Doppelkopf game."""
        self.num_players = 4
        self.reset()
    
    def reset(self):
        """Reset the game to its initial state."""
        # Create a deck of cards (2 copies of each card)
        self.deck = []
        for suit in Suit:
            for rank in Rank:
                # Skip Nine cards
                if rank != Rank.NINE:
                    self.deck.append(Card(suit, rank, False))
                    self.deck.append(Card(suit, rank, True))
        
        # Game state
        self.hands = [[] for _ in range(self.num_players)]
        self.tricks = []
        self.current_trick = []
        self.current_player = 0
        self.game_variant = GameVariant.NORMAL
        self.scores = [0, 0]  # [RE score, KONTRA score]
        self.player_scores = [0, 0, 0, 0]  # Individual player scores
        self.teams = [PlayerTeam.UNKNOWN] * self.num_players
        self.trick_winner = None
        self.game_over = False
        
        # Variant selection phase
        self.variant_selection_phase = True
        self.player_variant_choices = [None] * self.num_players  # Track each player's variant choice
        self.variant_priority = {
            'trump_solo': 1,  # Highest priority
            'queen_solo': 2,
            'jack_solo': 3,
            'fleshless': 4,
            'normal': 5,      # Lowest priority
            'hochzeit': 5     # Same priority as normal
        }
        
        # Announcement tracking
        self.re_announced = False
        self.contra_announced = False
        self.can_announce = True  # Can announce until the fifth card is played
        
        # Deal cards
        self._deal_cards()
        
        # Determine teams based on Queens of Clubs
        self._determine_teams()
    
    def _deal_cards(self):
        """Deal cards to players."""
        random.shuffle(self.deck)
        cards_per_player = len(self.deck) // self.num_players
        
        for i in range(self.num_players):
            self.hands[i] = self.deck[i * cards_per_player:(i + 1) * cards_per_player]
    
    def _determine_teams(self):
        """Determine which players are on which team based on Queens of Clubs."""
        queens_of_clubs = [Card(Suit.CLUBS, Rank.QUEEN, False), Card(Suit.CLUBS, Rank.QUEEN, True)]
        
        for i, hand in enumerate(self.hands):
            if any(card in queens_of_clubs for card in hand):
                self.teams[i] = PlayerTeam.RE
            else:
                self.teams[i] = PlayerTeam.KONTRA
    
    def has_hochzeit(self, player_idx: int) -> bool:
        """
        Check if the player has both Queens of Clubs (Hochzeit/Marriage).
        
        Args:
            player_idx: Index of the player
            
        Returns:
            True if the player has both Queens of Clubs, False otherwise
        """
        queens_of_clubs = [Card(Suit.CLUBS, Rank.QUEEN, False), Card(Suit.CLUBS, Rank.QUEEN, True)]
        return all(queen in self.hands[player_idx] for queen in queens_of_clubs)
    
    def get_legal_actions(self, player_idx: int) -> List[Card]:
        """
        Get the legal actions (cards that can be played) for the given player.
        
        Args:
            player_idx: Index of the player
            
        Returns:
            List of legal cards to play
        """
        # Cannot play cards during variant selection phase
        if self.variant_selection_phase:
            return []
            
        if player_idx != self.current_player or self.game_over:
            return []
        
        hand = self.hands[player_idx]
        
        # If this is the first card in the trick, any card can be played
        if not self.current_trick:
            return hand.copy()
        
        # Otherwise, must follow suit if possible
        lead_card = self.current_trick[0]
        lead_suit = lead_card.suit
        
        # Check if the lead card is trump
        lead_is_trump = lead_card.is_trump(self.game_variant)
        
        # Find cards of the same type (trump or same suit)
        matching_cards = []
        for card in hand:
            card_is_trump = card.is_trump(self.game_variant)
            
            if lead_is_trump and card_is_trump:
                matching_cards.append(card)
            elif not lead_is_trump and not card_is_trump and card.suit == lead_suit:
                matching_cards.append(card)
        
        # If player has matching cards, they must play one
        if matching_cards:
            return matching_cards
        
        # Otherwise, any card can be played
        return hand.copy()
    
    def play_card(self, player_idx: int, card: Card) -> bool:
        """
        Play a card for the given player.
        
        Args:
            player_idx: Index of the player
            card: The card to play
            
        Returns:
            True if the move was legal and executed, False otherwise
        """
        # Cannot play cards during variant selection phase
        if self.variant_selection_phase:
            return False
            
        if player_idx != self.current_player or self.game_over:
            return False
        
        legal_actions = self.get_legal_actions(player_idx)
        if card not in legal_actions:
            return False
        
        # Remove the card from the player's hand
        self.hands[player_idx].remove(card)
        
        # Add the card to the current trick
        self.current_trick.append(card)
        
        # Move to the next player
        self.current_player = (self.current_player + 1) % self.num_players
        
        # If the trick is complete, determine the winner
        if len(self.current_trick) == self.num_players:
            self._complete_trick()
        
        # Check if the game is over
        if all(len(hand) == 0 for hand in self.hands):
            self._end_game()
        
        # Update announcement eligibility
        # Can announce until the fifth card is played
        cards_played = len(self.current_trick)
        for trick in self.tricks:
            cards_played += len(trick)
        self.can_announce = cards_played < 5
        
        return True
    
    def announce(self, player_idx: int, announcement: str) -> bool:
        """
        Make an announcement (Re or Contra).
        
        Args:
            player_idx: Index of the player
            announcement: The announcement to make ('re' or 'contra')
            
        Returns:
            True if the announcement was legal and executed, False otherwise
        """
        # Cannot announce during variant selection phase
        if self.variant_selection_phase:
            return False
            
        # Cannot announce if not allowed
        if not self.can_announce:
            return False
        
        # Check if the player is in the appropriate team for the announcement
        player_team = self.teams[player_idx]
        
        if announcement == 're' and player_team != PlayerTeam.RE:
            return False
        elif announcement == 'contra' and player_team != PlayerTeam.KONTRA:
            return False
        
        # Check if the announcement has already been made
        if announcement == 're' and self.re_announced:
            return False
        elif announcement == 'contra' and self.contra_announced:
            return False
        
        # Make the announcement
        if announcement == 're':
            self.re_announced = True
        else:  # 'contra'
            self.contra_announced = True
        
        return True
    
    def set_variant(self, variant: str, player_idx: int = None) -> bool:
        """
        Set the game variant for a player.
        
        Args:
            variant: The variant to set ('normal', 'hochzeit', 'queen_solo', 'jack_solo', 'fleshless')
            player_idx: Index of the player making the choice (if None, uses current_player)
            
        Returns:
            True if the variant was set, False otherwise
        """
        # Can only set variant during variant selection phase
        if not self.variant_selection_phase:
            return False
        
        # Use current player if player_idx is not provided
        if player_idx is None:
            player_idx = self.current_player
            
        # Validate the variant
        valid_variant = False
        variant_enum = None
        
        if variant == 'normal':
            valid_variant = True
            variant_enum = GameVariant.NORMAL
            variant_key = 'normal'
        elif variant == 'hochzeit':
            valid_variant = True
            variant_enum = GameVariant.HOCHZEIT
            variant_key = 'hochzeit'
        elif variant == 'queen_solo':
            valid_variant = True
            variant_enum = GameVariant.QUEEN_SOLO
            variant_key = 'queen_solo'
        elif variant == 'jack_solo':
            valid_variant = True
            variant_enum = GameVariant.JACK_SOLO
            variant_key = 'jack_solo'
        elif variant == 'fleshless':
            valid_variant = True
            variant_enum = GameVariant.FLESHLESS
            variant_key = 'fleshless'
        elif variant == 'trump_solo':  # This is not implemented yet, but included for priority
            valid_variant = True
            variant_enum = GameVariant.NORMAL  # Fallback to normal for now
            variant_key = 'trump_solo'
            
        if not valid_variant:
            return False
            
        # Record the player's choice
        self.player_variant_choices[player_idx] = variant_key
        
        # Move to the next player
        self.current_player = (self.current_player + 1) % self.num_players
        
        # Check if all players have made a choice
        if all(choice is not None for choice in self.player_variant_choices):
            # Determine the final game variant based on choices
            self._determine_final_variant()
            
            # End variant selection phase
            self.variant_selection_phase = False
            
        return True
        
    def _determine_final_variant(self):
        """Determine the final game variant based on player choices."""
        # Count the occurrences of each variant
        variant_counts = {}
        for choice in self.player_variant_choices:
            if choice in variant_counts:
                variant_counts[choice] += 1
            else:
                variant_counts[choice] = 1
                
        # If everyone chose normal, play normal
        if len(variant_counts) == 1 and 'normal' in variant_counts:
            self.game_variant = GameVariant.NORMAL
            return
            
        # If only one player chose a non-normal variant, play that variant
        non_normal_variants = [v for v in self.player_variant_choices if v != 'normal' and v != 'hochzeit']
        if len(set(non_normal_variants)) == 1 and len(non_normal_variants) == 1:
            variant = non_normal_variants[0]
            if variant == 'queen_solo':
                self.game_variant = GameVariant.QUEEN_SOLO
            elif variant == 'jack_solo':
                self.game_variant = GameVariant.JACK_SOLO
            elif variant == 'fleshless':
                self.game_variant = GameVariant.FLESHLESS
            elif variant == 'trump_solo':
                self.game_variant = GameVariant.NORMAL  # Fallback to normal for now
            return
            
        # If multiple players chose different non-normal variants, use priority
        if len(set(non_normal_variants)) > 1:
            # Find the variant with the highest priority (lowest priority number)
            highest_priority_variant = None
            highest_priority = float('inf')
            
            for variant in set(non_normal_variants):
                priority = self.variant_priority.get(variant, float('inf'))
                if priority < highest_priority:
                    highest_priority = priority
                    highest_priority_variant = variant
                    
            if highest_priority_variant == 'queen_solo':
                self.game_variant = GameVariant.QUEEN_SOLO
            elif highest_priority_variant == 'jack_solo':
                self.game_variant = GameVariant.JACK_SOLO
            elif highest_priority_variant == 'fleshless':
                self.game_variant = GameVariant.FLESHLESS
            elif highest_priority_variant == 'trump_solo':
                self.game_variant = GameVariant.NORMAL  # Fallback to normal for now
            return
            
        # Default to normal game
        self.game_variant = GameVariant.NORMAL
    
    def _complete_trick(self):
        """Complete the current trick and determine the winner."""
        # Determine the winner of the trick
        lead_card = self.current_trick[0]
        lead_is_trump = lead_card.is_trump(self.game_variant)
        
        # Find the highest card of the same type
        highest_card_idx = 0
        highest_card_value = lead_card.get_order_value(self.game_variant)
        
        for i in range(1, len(self.current_trick)):
            card = self.current_trick[i]
            card_is_trump = card.is_trump(self.game_variant)
            
            # Trump beats non-trump
            if card_is_trump and not lead_is_trump:
                highest_card_idx = i
                highest_card_value = card.get_order_value(self.game_variant)
                lead_is_trump = True
            # Compare cards of the same type
            elif card_is_trump == lead_is_trump:
                if card_is_trump or card.suit == lead_card.suit:
                    card_value = card.get_order_value(self.game_variant)
                    if card_value > highest_card_value:
                        highest_card_idx = i
                        highest_card_value = card_value
        
        # The winner is the player who played the highest card
        self.trick_winner = (self.current_player - (self.num_players - highest_card_idx)) % self.num_players
        
        # Add the trick to the list of completed tricks
        self.tricks.append(self.current_trick)
        
        # Calculate points for the trick
        trick_points = sum(card.get_value() for card in self.current_trick)
        
        # Add points to the winner's team
        winner_team = self.teams[self.trick_winner]
        if winner_team == PlayerTeam.RE:
            self.scores[0] += trick_points
        else:
            self.scores[1] += trick_points
            
        # Add points to the individual player's score
        self.player_scores[self.trick_winner] += trick_points
        
        # Store the last trick points for display
        self.last_trick_points = trick_points
        
        # Store the trick winner and set them as the next player to play
        # When a player wins a trick, it is their turn to play next
        
        # The current_player will be updated to the trick winner when the trick is cleared
        # This is handled by the server after a delay to show the completed trick
        
        # IMPORTANT: Do not clear the current trick here
        # The current trick will be cleared by the server after a delay
        # self.current_trick = []
    
    def _end_game(self):
        """End the game and calculate final scores."""
        self.game_over = True
        
        # The team with more points wins
        total_points = sum(self.scores)
        re_points = self.scores[0]
        kontra_points = self.scores[1]
        
        # In Doppelkopf, winning team needs at least 121 points
        # (total points is 240, so other team would have at most 119)
        if re_points >= 121:
            self.winner = PlayerTeam.RE
        else:
            self.winner = PlayerTeam.KONTRA
    
    def get_state(self) -> Dict:
        """
        Get the current state of the game.
        
        Returns:
            A dictionary representing the current game state
        """
        return {
            'hands': self.hands.copy(),
            'current_trick': self.current_trick.copy(),
            'tricks': [trick.copy() for trick in self.tricks],
            'current_player': self.current_player,
            'game_variant': self.game_variant,
            'scores': self.scores.copy(),
            'player_scores': self.player_scores.copy(),
            'teams': self.teams.copy(),
            'trick_winner': self.trick_winner,
            'game_over': self.game_over,
            'last_trick_points': getattr(self, 'last_trick_points', 0),
            'variant_selection_phase': self.variant_selection_phase,
            're_announced': self.re_announced,
            'contra_announced': self.contra_announced,
            'can_announce': self.can_announce
        }
    
    def get_state_size(self) -> int:
        """
        Get the size of the state representation for the RL agent.
        
        Returns:
            The size of the state vector
        """
        # This is a simplified representation for the RL agent
        # 48 cards (one-hot encoded) + 4 players (one-hot encoded) + current trick (48 cards)
        # + variant_selection_phase (1) + re_announced (1) + contra_announced (1) + can_announce (1) + player_team (1)
        return 48 + 4 + 48 + 5
    
    def get_action_size(self) -> int:
        """
        Get the size of the action space for the RL agent.
        
        Returns:
            The size of the action space
        """
        # There are 48 possible cards to play
        return 48
    
    def get_state_for_player(self, player_idx: int) -> np.ndarray:
        """
        Get the state representation for the given player.
        
        Args:
            player_idx: Index of the player
            
        Returns:
            A numpy array representing the state from the player's perspective
        """
        # Create a state vector
        # Extended state size to include:
        # - variant_selection_phase (1 element)
        # - re_announced (1 element)
        # - contra_announced (1 element)
        # - can_announce (1 element)
        # - player's team (1 element)
        state = np.zeros(self.get_state_size())
        
        # Encode the player's hand (first 48 elements)
        for card in self.hands[player_idx]:
            card_idx = self._card_to_idx(card)
            state[card_idx] = 1
        
        # Encode the current player (next 4 elements)
        state[48 + self.current_player] = 1
        
        # Encode the current trick (next 48 elements)
        for card in self.current_trick:
            card_idx = self._card_to_idx(card)
            state[52 + card_idx] = 1
        
        # Encode additional state information
        state[100] = 1 if self.variant_selection_phase else 0
        state[101] = 1 if self.re_announced else 0
        state[102] = 1 if self.contra_announced else 0
        state[103] = 1 if self.can_announce else 0
        state[104] = 1 if self.teams[player_idx] == PlayerTeam.RE else 0
        
        return state
    
    def _card_to_idx(self, card: Card) -> int:
        """
        Convert a card to an index in the state representation.
        
        Args:
            card: The card to convert
            
        Returns:
            The index of the card
        """
        suit_idx = card.suit.value - 1
        rank_idx = card.rank.value - 9  # 9 is the lowest rank
        is_second_idx = 1 if card.is_second else 0
        
        # 6 ranks, 4 suits, 2 copies
        return suit_idx * 12 + rank_idx * 2 + is_second_idx
    
    def _idx_to_card(self, idx: int) -> Card:
        """
        Convert an index to a card.
        
        Args:
            idx: The index to convert
            
        Returns:
            The corresponding card
        """
        is_second = idx % 2 == 1
        rank_idx = (idx // 2) % 6
        suit_idx = idx // 12
        
        suit = Suit(suit_idx + 1)
        rank = Rank(rank_idx + 9)  # 9 is the lowest rank
        
        return Card(suit, rank, is_second)
    
    def action_to_card(self, action: int, player_idx: int) -> Optional[Card]:
        """
        Convert an action index to a card for the given player.
        
        Args:
            action: The action index
            player_idx: Index of the player
            
        Returns:
            The corresponding card, or None if the action is invalid
        """
        if action < 0 or action >= self.get_action_size():
            return None
        
        card = self._idx_to_card(action)
        
        # Check if the card is in the player's hand and is a legal move
        legal_actions = self.get_legal_actions(player_idx)
        for legal_card in legal_actions:
            if (legal_card.suit == card.suit and 
                legal_card.rank == card.rank and 
                legal_card.is_second == card.is_second):
                return legal_card
        
        return None
