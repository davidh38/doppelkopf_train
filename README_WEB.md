# Web-based Doppelkopf Game

This is a web-based implementation of the Doppelkopf card game, allowing you to play against AI opponents through a browser interface.

## Features

- Play Doppelkopf against AI opponents
- Beautiful card interface using open source card images
- Support for different game variants:
  - Normal game
  - Hochzeit (Marriage)
  - Queen Solo
  - Jack Solo
- Real-time updates using WebSockets
- Responsive design that works on desktop and mobile

## Requirements

- Python 3.6+
- Flask
- Flask-SocketIO
- Other dependencies listed in requirements.txt

## Installation

1. Make sure you have Python installed on your system
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

1. Start the Flask server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

3. Click "New Game" to start a game
4. Select a game variant
5. Play cards by clicking on them when it's your turn

## Game Rules

### Basic Rules

Doppelkopf is a trick-taking card game for four players. The deck consists of 40 cards (no nines) with two copies of each card. Players are divided into two teams: Re and Kontra.

### Trump Cards

In the normal game:
- All Queens and Jacks are trump cards
- All Diamond cards are trump cards

In special variants:
- Queen Solo: Only Queens are trump
- Jack Solo: Only Jacks are trump

### Scoring

The game is played until all cards are played. The team with more points wins. A total of 240 points are available in the game, so a team needs at least 121 points to win.

### Card Values

- Ace: 11 points
- Ten: 10 points
- King: 4 points
- Queen: 3 points
- Jack: 2 points

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, images)
- `game/`: Game logic implementation
- `agents/`: AI agent implementations

## Credits

- Card images: [cardsJS](https://github.com/richardschneider/cardsJS)
- Game logic based on the Doppelkopf implementation in this repository
