# Doppelkopf Final Card Scenario

This script creates a Doppelkopf game with only one card left to play for each player. It allows you to experience the excitement of playing the final card that determines the outcome of the game.

## Prerequisites

- Python 3.6 or higher
- Flask
- Flask-SocketIO
- A web browser

## How to Run

1. Make sure you have all the required dependencies installed:
   ```
   pip install flask flask-socketio
   ```

2. Run the script with one of the available scenarios:
   ```
   python final_card_game.py --scenario re_wins
   ```
   or
   ```
   python final_card_game.py --scenario kontra_wins
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5008
   ```

## Available Scenarios

### Re Wins Scenario (`--scenario re_wins`)

In this scenario:
- You are on the Re team
- The scores are tied at 115-115
- You have the Ace of Diamonds (a trump card)
- When you play your card, your team will win with exactly 125 points

### Kontra Wins Scenario (`--scenario kontra_wins`)

In this scenario:
- You are on the Re team
- The scores are tied at 115-115
- You have the Nine of Hearts (a non-trump card)
- When you play your card, the Kontra team will win with exactly 125 points

## How to Play

1. Wait for the AI players to play their cards (Player 3 starts)
2. When it's your turn, click on your card to play it
3. Watch as the final trick is completed and the winner is determined
4. The game will display the final scores and the winner

## Game Rules

- The Re team consists of players with Queens of Clubs
- The Kontra team consists of players without Queens of Clubs
- Trump cards are:
  - All Queens
  - All Jacks
  - All Diamonds
  - Ten of Hearts
- The team that reaches at least 121 points wins
- In these scenarios, the winning team will have exactly 125 points

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed
2. Check that port 5008 is available on your system
3. If the web interface doesn't load, try refreshing the page
4. If the game doesn't start, check the console output for errors

## Customizing the Game

You can modify the `setup_re_wins_scenario` and `setup_kontra_wins_scenario` functions in the script to create your own scenarios with different cards and scores.
