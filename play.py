#!/usr/bin/env python3
"""
Play Doppelkopf with a trained AI.
This script allows you to play Doppelkopf against a trained AI model.
"""

import argparse
import os
from game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant
from agents.random_agent import select_random_action
from agents.rl_agent import RLAgent
import training.trainer as trainer

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Play Doppelkopf against a trained AI')
    parser.add_argument('--model', type=str, required=True,
                        help='Path to a trained model')
    return parser.parse_args()

def print_card_list(cards):
    """Print a list of cards with indices."""
    for i, card in enumerate(cards):
        print(f"{i}: {card}")

def get_player_action(legal_actions, game):
    """
    Get an action from the human player.
    
    Args:
        legal_actions: List of legal cards to play
        game: The current game instance
    
    Returns:
        The selected card
    """
    print("\nYour legal actions:")
    # Sort legal actions to match the sorted hand display
    sorted_legal_actions = sort_cards(legal_actions, game.game_variant)
    print_card_list(sorted_legal_actions)
    
    while True:
        try:
            choice = int(input("Enter the index of the card you want to play: "))
            if 0 <= choice < len(sorted_legal_actions):
                return sorted_legal_actions[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def sort_cards(cards, game_variant):
    """
    Sort cards according to Doppelkopf trump order, then by suit and rank.
    
    Args:
        cards: List of cards to sort
        game_variant: The current game variant
        
    Returns:
        Sorted list of cards
    """
    # Define a key function for sorting
    def sort_key(card):
        # Trump cards order in Doppelkopf:
        # 1. Queens (Clubs, Spades, Hearts, Diamonds)
        # 2. Jacks (Clubs, Spades, Hearts, Diamonds)
        # 3. Diamond cards (Ace, 10, King)
        
        # Queens
        if card.rank == Rank.QUEEN:
            # Explicit ordering for suits
            if card.suit == Suit.CLUBS:
                suit_order = 0
            elif card.suit == Suit.SPADES:
                suit_order = 1
            elif card.suit == Suit.HEARTS:
                suit_order = 2
            else:  # Diamonds
                suit_order = 3
            return (0, 0, suit_order)
        
        # Jacks
        if card.rank == Rank.JACK:
            # Explicit ordering for suits
            if card.suit == Suit.CLUBS:
                suit_order = 0
            elif card.suit == Suit.SPADES:
                suit_order = 1
            elif card.suit == Suit.HEARTS:
                suit_order = 2
            else:  # Diamonds
                suit_order = 3
            return (0, 1, suit_order)
        
        # Diamond cards (other than Queen and Jack)
        if card.suit == Suit.DIAMONDS:
            # Sort by rank within diamonds (highest first)
            # Ace=14, 10=10, King=13
            rank_value = card.rank.value
            # Adjust to get Ace, 10, King order
            if rank_value == 14:  # Ace
                rank_order = 0
            elif rank_value == 10:  # Ten
                rank_order = 1
            else:  # King
                rank_order = 2
            return (0, 2, rank_order)
        
        # Non-trump cards
        # Clubs
        if card.suit == Suit.CLUBS:
            return (1, 0, -card.rank.value)
        
        # Spades
        if card.suit == Suit.SPADES:
            return (1, 1, -card.rank.value)
        
        # Hearts
        return (1, 2, -card.rank.value)
    
    # Return sorted cards
    return sorted(cards, key=sort_key)

def print_game_state(game, human_player_idx):
    """Print the current state of the game."""
    print("\n" + "=" * 50)
    print(f"Current player: {'You' if game.current_player == human_player_idx else 'AI'}")
    print(f"Your team: {game.teams[human_player_idx]}")
    
    print("\nCurrent trick:")
    if game.current_trick:
        print_card_list(game.current_trick)
    else:
        print("No cards played yet")
    
    # Sort the player's hand before displaying
    sorted_hand = sort_cards(game.hands[human_player_idx], game.game_variant)
    
    print("\nYour hand:")
    print_card_list(sorted_hand)
    
    print(f"\nScores - RE: {game.scores[0]}, KONTRA: {game.scores[1]}")
    print("=" * 50)

def check_for_hochzeit(hand):
    """Check if the player has both Queens of Clubs."""
    queens_of_clubs = [Card(Suit.CLUBS, Rank.QUEEN, False), Card(Suit.CLUBS, Rank.QUEEN, True)]
    return all(queen in hand for queen in queens_of_clubs)

def announce_game_variant(game, human_player_idx):
    """Ask the player if they want to announce a special game variant."""
    hand = game.hands[human_player_idx]
    
    print("\nYour hand:")
    sorted_hand = sort_cards(hand, game.game_variant)
    print_card_list(sorted_hand)
    
    # Check for Hochzeit (Marriage)
    has_hochzeit = check_for_hochzeit(hand)
    
    print("\nDo you want to announce a special game variant?")
    if has_hochzeit:
        print("1: Hochzeit (Marriage) - You have both Queens of Clubs")
    print("2: Queen Solo - Only Queens are trump")
    print("3: Jack Solo - Only Jacks are trump")
    print("4: Fleshless - No Kings, Queens, or Jacks are trump")
    print("0: No special variant (normal game)")
    
    while True:
        try:
            choice = int(input("Enter your choice (0-4): "))
            if choice == 0:
                game.game_variant = GameVariant.NORMAL
                print("Playing normal game.")
                break
            elif choice == 1:
                if has_hochzeit:
                    game.game_variant = GameVariant.HOCHZEIT
                    print("Hochzeit announced! You'll partner with whoever wins the first trick with a Queen of Clubs.")
                    break
                else:
                    print("You don't have both Queens of Clubs. Please choose another option.")
            elif choice == 2:
                game.game_variant = GameVariant.QUEEN_SOLO
                print("Queen Solo announced! Only Queens are trump.")
                break
            elif choice == 3:
                game.game_variant = GameVariant.JACK_SOLO
                print("Jack Solo announced! Only Jacks are trump.")
                break
            elif choice == 4:
                game.game_variant = GameVariant.FLESHLESS
                print("Fleshless announced! No Kings, Queens, or Jacks are trump.")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    """Main function to run the game."""
    args = parse_arguments()
    
    # Initialize game
    game = DoppelkopfGame()
    
    # Human is player 0
    human_player_idx = 0
    
    # Initialize AI agents
    rl_agent = RLAgent(game.get_state_size(), game.get_action_size())
    rl_agent.load(args.model)
    print(f"Loaded model from {args.model}")
    
    # Other players are random agents for now
    ai_agents = [rl_agent] + [select_random_action for _ in range(2)]
    
    # Play the game
    game.reset()
    
    print("Welcome to Doppelkopf!")
    print("You are playing against 3 AI opponents.")
    
    # Ask the player if they want to announce a special game variant
    announce_game_variant(game, human_player_idx)
    
    while not game.game_over:
        current_player = game.current_player
        
        # Print the game state
        print_game_state(game, human_player_idx)
        
        # Get action
        if current_player == human_player_idx:
            # Human player's turn
            legal_actions = game.get_legal_actions(current_player)
            action = get_player_action(legal_actions, game)
        else:
            # AI player's turn
            ai_idx = current_player - 1 if current_player > human_player_idx else current_player
            agent = ai_agents[ai_idx]
            
            # Handle both class-based and function-based agents
            if hasattr(agent, 'select_action'):
                action = agent.select_action(game, current_player)
            else:
                action = agent(game, current_player)
                
            print(f"Player {current_player} plays: {action}")
        
        # Play the card
        game.play_card(current_player, action)
        
        # If a trick was completed, show the completed trick and who won
        if game.trick_winner is not None:
            winner = game.trick_winner
            
            # Get the completed trick (it's stored in the tricks list)
            completed_trick = game.tricks[-1]
            
            print("\nCompleted trick:")
            for i, card in enumerate(completed_trick):
                player_idx = (game.current_player - len(completed_trick) + i) % game.num_players
                player_name = "You" if player_idx == human_player_idx else f"Player {player_idx}"
                print(f"{player_name} played: {card}")
            
            print(f"\nPlayer {winner} {'(You)' if winner == human_player_idx else ''} won the trick!")
            input("Press Enter to continue...")
    
    # Game over, show results
    print("\nGame over!")
    print(f"Final scores - RE: {game.scores[0]}, KONTRA: {game.scores[1]}")
    
    human_team = game.teams[human_player_idx]
    if game.winner == human_team:
        print("Congratulations! Your team won!")
    else:
        print("Sorry, your team lost.")

if __name__ == "__main__":
    main()
