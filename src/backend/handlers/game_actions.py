#!/usr/bin/env python3
"""
Game action route handlers for the Doppelkopf web application.
These include setting variants, playing cards, and making announcements.
"""

from flask import jsonify

from src.backend.game.doppelkopf import (
    SUIT_NAMES, RANK_NAMES, TEAM_NAMES, VARIANT_NAMES,
    create_card, get_legal_actions, play_card, announce, set_variant, get_card_value
)
from src.backend.card_utils import cards_equal
from src.backend.config import games, scoreboard
from src.backend.game_state import (
    get_game_state, check_team_revelation, 
    generate_game_summary, update_scoreboard_for_game_over
)
from src.backend.ai_logic import ai_play_turn, handle_trick_completion

def set_variant_route(socketio, data):
    """Set the game variant."""
    game_id = data.get('game_id')
    variant = data.get('variant')
    player_idx = data.get('player_idx', 0)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Set the variant for the player
    result = set_variant(game, variant, player_idx)
    
    if not result:
        return jsonify({'error': 'Invalid variant or not in variant selection phase'}), 400
    
    # Store the player's variant selection
    if 'player_variants' not in games[game_id]:
        games[game_id]['player_variants'] = {}
    
    games[game_id]['player_variants'][player_idx] = variant
    
    # If the variant selection phase is over, have AI play if it's not the player's turn
    if not game['variant_selection_phase'] and game['current_player'] != 0:
        ai_play_turn(socketio, game_id)
    
    # If we're still in variant selection phase and it's an AI player's turn,
    # have all remaining AI players choose their variants in sequence
    elif game['variant_selection_phase'] and game['current_player'] != 0:
        # Have all remaining AI players choose their variants in sequence
        while game['variant_selection_phase'] and game['current_player'] != 0:
            current_player = game['current_player']
            
            # Emit an event to show the variant selection animation for this AI player
            socketio.emit('ai_selecting_variant', {
                'player': current_player,
                'variant': 'normal'
            })
            
            # Add a small delay to allow the animation to be visible
            import time
            time.sleep(0.5)
            
            # Set the variant for the AI player
            set_variant(game, 'normal', current_player)
            
            if 'player_variants' not in games[game_id]:
                games[game_id]['player_variants'] = {}
            games[game_id]['player_variants'][current_player] = 'normal'
            
            # Update the game state for the client
            socketio.emit('game_update', get_game_state(game_id), room=game_id)
        
        # If the variant selection phase is now over, have AI play if it's not the player's turn
        if not game['variant_selection_phase'] and game['current_player'] != 0:
            ai_play_turn(socketio, game_id)
    
    # Set legal actions for the player if it's their turn
    if not game['variant_selection_phase'] and game['current_player'] == 0:
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player: {game['legal_actions']}")
    
    return jsonify({
        'state': get_game_state(game_id),
        'variant_selection_phase': game['variant_selection_phase'],
        'current_player': game['current_player'],
        'game_variant': VARIANT_NAMES[game['game_variant']]
    })

def play_card_route(socketio, data):
    """Play a card."""
    game_id = data.get('game_id')
    card_id = data.get('card_id')
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]['game']
    
    # Check if it's the player's turn
    if game['current_player'] != 0:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Find the card in the player's hand
    card_parts = card_id.split('_')
    suit_name = card_parts[0]
    rank_name = card_parts[1]
    is_second = card_parts[2] == '1'
    
    # Convert suit and rank names to constants
    suit_map = {name: const for const, name in SUIT_NAMES.items()}
    rank_map = {name: const for const, name in RANK_NAMES.items()}
    
    suit = suit_map[suit_name]
    rank = rank_map[rank_name]
    
    # Create the card
    selected_card = create_card(suit, rank, is_second)
    
    # Find the card in the legal actions
    legal_actions = get_legal_actions(game, 0)
    if not any(cards_equal(selected_card, legal_card) for legal_card in legal_actions):
        return jsonify({'error': 'Invalid card or not a legal move'}), 400
    
    # Play the card
    play_card(game, 0, selected_card)
    
    # Check if the player revealed their team by playing a Queen of Clubs
    check_team_revelation(game, 0, selected_card, games[game_id])
    
    # Check if a trick was completed
    trick_completed = game.get('trick_winner') is not None
    trick_winner = game.get('trick_winner')
    trick_points = 0
    
    # If a trick was completed, handle it before AI plays
    if trick_completed:
        # Store the trick winner before handling the trick completion
        trick_winner = game['trick_winner']
        
        # Calculate points for the trick before handling the trick completion
        trick_points = sum(get_card_value(card) for card in game['current_trick'])
        
        # Handle trick completion
        handle_trick_completion(socketio, game_id, game)
    
    # Have AI players take their turns
    ai_play_turn(socketio, game_id)
    
    # Set legal actions for the player if it's their turn
    if game['current_player'] == 0:
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player after AI turns: {game['legal_actions']}")
    
    # Check if game is over and update scoreboard
    if game['game_over']:
        # Generate game summary
        summary_text = generate_game_summary(game_id)
        
        # Update scoreboard
        update_scoreboard_for_game_over(game_id)
    
    # Create a response object
    response_data = {
        'state': get_game_state(game_id),
        'trick_completed': trick_completed,
        'trick_winner': trick_winner,
        'is_player_winner': trick_winner == 0 if trick_winner is not None else False,
        'trick_points': trick_points if trick_completed else 0,
        'scoreboard': scoreboard
    }
    
    # If the game is over, include the player scores in the state and add a game summary
    if game['game_over']:
        # Make sure the player scores are included in the state
        response_data['state']['player_scores'] = scoreboard['player_scores']
        
        # Also include the scoreboard in the state for easy access
        response_data['state']['scoreboard'] = {
            'player_wins': scoreboard['player_wins'],
            'ai_wins': scoreboard['ai_wins'],
            'player_scores': scoreboard['player_scores']
        }
        
        # Add the game summary to the response
        response_data['game_summary'] = games[game_id]['game_summary']
    
    return jsonify(response_data)

def announce_route(socketio, data):
    """Announce Re, Contra, or additional announcements (No 90, No 60, No 30, Black)."""
    game_id = data.get('game_id')
    announcement = data.get('announcement')  # 're', 'contra', 'no90', 'no60', 'no30', 'black'
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Count cards played
    cards_played = len(game['current_trick'])
    for trick in game['tricks']:
        cards_played += len(trick)
    
    # Check if the player is in the appropriate team for the announcement
    player_team = game['teams'][0]  # Player is always index 0
    
    # Handle Re and Contra announcements
    if announcement in ['re', 'contra']:
        # Check if more than 5 cards have been played
        if cards_played >= 5:
            return jsonify({'error': 'Cannot announce Re or Contra after the fifth card has been played'}), 400
        
        # Check if the player is in the appropriate team
        if announcement == 're' and player_team != TEAM_RE:
            return jsonify({'error': 'Only RE team members can announce Re'}), 400
        elif announcement == 'contra' and player_team != TEAM_KONTRA:
            return jsonify({'error': 'Only KONTRA team members can announce Contra'}), 400
        
        # Update the game data based on the announcement
        if announcement == 're':
            game_data['re_announced'] = True
            game_data['re_announcement_card'] = cards_played  # Track when Re was announced
            game_data['multiplier'] = 2  # Set multiplier to 2 for Re
        elif announcement == 'contra':
            game_data['contra_announced'] = True
            game_data['contra_announcement_card'] = cards_played  # Track when Contra was announced
            game_data['multiplier'] = 2  # Set multiplier to 2 for Contra
    
    # Handle additional announcements (No 90, No 60, No 30, Black)
    elif announcement in ['no90', 'no60', 'no30', 'black']:
        # Check if the player has announced Re or Contra
        if player_team == TEAM_RE and not game_data.get('re_announced', False):
            return jsonify({'error': 'You must announce Re before making additional announcements'}), 400
        elif player_team == TEAM_KONTRA and not game_data.get('contra_announced', False):
            return jsonify({'error': 'You must announce Contra before making additional announcements'}), 400
        
        # Check if the announcement was made within 5 cards after Re or Contra
        re_announced_card = game_data.get('re_announcement_card', -1)
        contra_announced_card = game_data.get('contra_announcement_card', -1)
        
        if player_team == TEAM_RE and (re_announced_card < 0 or cards_played > re_announced_card + 5):
            return jsonify({'error': 'Additional announcements must be made within 5 cards after Re'}), 400
        elif player_team == TEAM_KONTRA and (contra_announced_card < 0 or cards_played > contra_announced_card + 5):
            return jsonify({'error': 'Additional announcements must be made within 5 cards after Contra'}), 400
        
        # Check if the announcements are made in the correct order
        if announcement == 'no90' and not game_data.get('no90_announced', False):
            game_data['no90_announced'] = True
            game_data['multiplier'] = 3  # Set multiplier to 3 for No 90
        elif announcement == 'no60' and game_data.get('no90_announced', False) and not game_data.get('no60_announced', False):
            game_data['no60_announced'] = True
            game_data['multiplier'] = 4  # Set multiplier to 4 for No 60
        elif announcement == 'no30' and game_data.get('no60_announced', False) and not game_data.get('no30_announced', False):
            game_data['no30_announced'] = True
            game_data['multiplier'] = 5  # Set multiplier to 5 for No 30
        elif announcement == 'black' and game_data.get('no30_announced', False) and not game_data.get('black_announced', False):
            game_data['black_announced'] = True
            game_data['multiplier'] = 6  # Set multiplier to 6 for Black
        else:
            return jsonify({'error': 'Invalid announcement order'}), 400
    else:
        return jsonify({'error': 'Invalid announcement'}), 400
    
    # Set legal actions for the player if it's their turn
    if game['current_player'] == 0:
        game['legal_actions'] = get_legal_actions(game, 0)
        print(f"Setting legal actions for player after announcement: {game['legal_actions']}")
    
    return jsonify({
        'state': get_game_state(game_id),
        're_announced': game_data.get('re_announced', False),
        'contra_announced': game_data.get('contra_announced', False),
        'no90_announced': game_data.get('no90_announced', False),
        'no60_announced': game_data.get('no60_announced', False),
        'no30_announced': game_data.get('no30_announced', False),
        'black_announced': game_data.get('black_announced', False),
        'multiplier': game_data.get('multiplier', 1)
    })
