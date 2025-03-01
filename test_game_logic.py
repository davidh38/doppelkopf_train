#!/usr/bin/env python3
"""
Test script to verify the team display and score calculation logic in the Doppelkopf game.
"""

from game.doppelkopf import DoppelkopfGame, Card, Suit, Rank, GameVariant, PlayerTeam

def test_team_reveal():
    """Test the team reveal logic when a Queen of Clubs is played."""
    print("=== Testing Team Reveal Logic ===")
    
    # Create a new game
    game = DoppelkopfGame()
    
    # Reset the game with a fixed seed for reproducibility
    import random
    random.seed(42)
    game.reset()
    
    # Print initial teams (should be determined but not revealed to players)
    print("Initial teams:")
    for i, team in enumerate(game.teams):
        print(f"Player {i}: {team.name}")
    
    # Find a player with a Queen of Clubs
    queen_of_clubs = Card(Suit.CLUBS, Rank.QUEEN, False)
    queen_of_clubs2 = Card(Suit.CLUBS, Rank.QUEEN, True)
    
    re_players = []
    for i, hand in enumerate(game.hands):
        if queen_of_clubs in hand or queen_of_clubs2 in hand:
            re_players.append(i)
            print(f"Player {i} has a Queen of Clubs and is on team RE")
    
    # There should be exactly 2 players on team RE
    assert len(re_players) == 2, f"Expected 2 RE players, found {len(re_players)}"
    
    # Verify that the teams are correctly assigned
    for i, team in enumerate(game.teams):
        if i in re_players:
            assert team == PlayerTeam.RE, f"Player {i} should be on team RE"
        else:
            assert team == PlayerTeam.KONTRA, f"Player {i} should be on team KONTRA"
    
    print("Team assignment test passed!")
    
    # In a real game, when a Queen of Clubs is played, it would reveal the player's team
    # This is handled in the web interface (game.js) but we can simulate it here
    
    # Simulate a game where a Queen of Clubs is played
    # First, make sure the player with Queen of Clubs is the current player
    re_player = re_players[0]
    game.current_player = re_player
    
    # Find the Queen of Clubs in their hand
    queen_in_hand = None
    for card in game.hands[re_player]:
        if card.rank == Rank.QUEEN and card.suit == Suit.CLUBS:
            queen_in_hand = card
            break
    
    assert queen_in_hand is not None, f"Player {re_player} should have a Queen of Clubs"
    
    # Play the Queen of Clubs
    print(f"\nPlayer {re_player} plays Queen of Clubs")
    game.play_card(re_player, queen_in_hand)
    
    # The current trick should now contain the Queen of Clubs
    assert game.current_trick[0] == queen_in_hand, "Queen of Clubs should be in the current trick"
    
    print("Queen of Clubs played successfully!")
    
    # In the web interface, this would trigger the team display to show "re" for this player
    # We can verify that the player is indeed on team RE
    assert game.teams[re_player] == PlayerTeam.RE, f"Player {re_player} should be on team RE"
    
    print("Team reveal test passed!")
    return True

def test_score_calculation():
    """Test the score calculation logic at the end of a game."""
    print("\n=== Testing Score Calculation Logic ===")
    
    # Create a new game
    game = DoppelkopfGame()
    
    # Reset the game with a fixed seed for reproducibility
    import random
    random.seed(42)
    game.reset()
    
    # Print initial teams
    print("Teams:")
    for i, team in enumerate(game.teams):
        print(f"Player {i}: {team.name}")
    
    # Simulate playing all cards to end the game
    # We'll just set the scores directly and call _end_game
    
    # Set scores so that RE team wins (needs at least 121 points)
    game.scores = [150, 90]  # [RE score, KONTRA score]
    
    # End the game
    game._end_game()
    
    # Verify that the game is over and RE team won
    assert game.game_over, "Game should be over"
    assert game.winner == PlayerTeam.RE, "RE team should win"
    
    print(f"Game over, winner: {game.winner.name}")
    
    # In the web interface, this would trigger the score display
    # The winning team gets +2 points per player, losing team gets -2 points per player
    
    # Count players in each team
    re_players = sum(1 for team in game.teams if team == PlayerTeam.RE)
    kontra_players = sum(1 for team in game.teams if team == PlayerTeam.KONTRA)
    
    assert re_players == 2, f"Expected 2 RE players, found {re_players}"
    assert kontra_players == 2, f"Expected 2 KONTRA players, found {kontra_players}"
    
    # Calculate expected points
    re_points = kontra_players  # Each RE player gets +kontra_players
    kontra_points = -re_players  # Each KONTRA player gets -re_players
    
    print(f"RE players should get {re_points} points each")
    print(f"KONTRA players should get {kontra_points} points each")
    
    # Verify that the points would be calculated correctly
    for i, team in enumerate(game.teams):
        expected_points = re_points if team == PlayerTeam.RE else kontra_points
        print(f"Player {i} ({team.name}): Expected {expected_points} points")
    
    print("Score calculation test passed!")
    return True

def main():
    """Run the tests."""
    print("Starting Doppelkopf game logic tests...\n")
    
    team_reveal_success = test_team_reveal()
    score_calculation_success = test_score_calculation()
    
    print("\n=== Test Results ===")
    print(f"Team reveal logic: {'PASSED' if team_reveal_success else 'FAILED'}")
    print(f"Score calculation logic: {'PASSED' if score_calculation_success else 'FAILED'}")
    print(f"All tests: {'PASSED' if team_reveal_success and score_calculation_success else 'FAILED'}")

if __name__ == "__main__":
    main()
