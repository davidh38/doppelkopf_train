/**
 * Card-related functions
 */
import { gameState } from './game-core.js';
import { eventBus } from './event-bus.js';

/**
 * Check if a card is a trump card
 * @param {Object} card - Card object
 * @returns {boolean} - True if the card is a trump
 */
export function isTrumpCard(card) {
  if (!card) return false;
  
  // In normal Doppelkopf, trumps are:
  // - All Diamonds (except for some variants)
  // - All Jacks
  // - All Queens
  
  // Check game variant for special rules
  if (gameState.gameVariant === 'FLESHLESS') {
    // In Fleshless, only Jacks and Queens are trump
    return card.rank === 'JACK' || card.rank === 'QUEEN';
  } else if (gameState.gameVariant === 'JACK_SOLO') {
    // In Jack Solo, only Jacks are trump
    return card.rank === 'JACK';
  } else if (gameState.gameVariant === 'QUEEN_SOLO') {
    // In Queen Solo, only Queens are trump
    return card.rank === 'QUEEN';
  } else if (gameState.gameVariant === 'KING_SOLO') {
    // In King Solo, only Kings are trump
    return card.rank === 'KING';
  } else if (gameState.gameVariant === 'TRUMP_SOLO') {
    // In Trump Solo, all normal trumps are trump
    return card.suit === 'DIAMONDS' || card.rank === 'JACK' || card.rank === 'QUEEN';
  } else {
    // Normal game
    return card.suit === 'DIAMONDS' || card.rank === 'JACK' || card.rank === 'QUEEN' || 
           (card.suit === 'HEARTS' && card.rank === 'TEN'); // 10 of Hearts is also trump
  }
}

/**
 * Create a card element
 * @param {Object} card - Card object
 * @param {boolean} isPlayable - Whether the card is playable
 * @returns {HTMLElement} - Card element
 */
export function createCardElement(card, isPlayable) {
  console.log(`Creating card element for ${card.id}, isPlayable: ${isPlayable}`);
  
  const cardContainer = document.createElement('div');
  cardContainer.className = 'card-container';
  cardContainer.dataset.cardId = card.id;
  
  // Add playable class to the container if the card is playable
  if (isPlayable) {
    cardContainer.classList.add('playable');
    
    // Add a click event listener to the container
    cardContainer.addEventListener('click', () => {
      console.log('Card clicked:', card.id);
      eventBus.emit('cardPlayed', card.id);
    });
    
    // Add a style to indicate it's clickable
    cardContainer.style.cursor = 'pointer';
    cardContainer.style.border = '2px solid green';
    cardContainer.style.borderRadius = '5px';
    cardContainer.style.boxShadow = '0 0 10px rgba(0, 255, 0, 0.5)';
  } else {
    // Add a style to indicate it's not clickable
    cardContainer.style.opacity = '0.7';
    cardContainer.style.filter = 'grayscale(50%)';
  }
  
  const cardElement = document.createElement('img');
  cardElement.className = 'card';
  
  // Use the card's suit and rank to determine the image path
  const suitMap = {
    'CLUBS': 'C',
    'SPADES': 'S',
    'HEARTS': 'H',
    'DIAMONDS': 'D'
  };
  
  const rankMap = {
    'NINE': '9',
    'TEN': '0', // Use '0' for 10s since we have 0C.png, 0D.png, etc.
    'JACK': 'J',
    'QUEEN': 'Q',
    'KING': 'K',
    'ACE': 'A'
  };
  
  // Use the format without the blue "2" markers (e.g., "9C.png" instead of "9_of_clubs.png")
  const cardCode = rankMap[card.rank] + suitMap[card.suit];
  const cardSrc = `/static/images/cards/${cardCode}.png`;
  
  cardElement.src = cardSrc;
  cardElement.alt = `${card.rank} of ${card.suit}`;
  
  // Add a click event listener to the card image as well
  if (isPlayable) {
    cardElement.addEventListener('click', () => {
      console.log('Card image clicked:', card.id);
      eventBus.emit('cardPlayed', card.id);
    });
    
    // Make sure the card is fully visible
    cardElement.style.opacity = '1';
    cardElement.style.filter = 'none';
    cardElement.style.cursor = 'pointer';
  }
  
  cardContainer.appendChild(cardElement);
  
  return cardContainer;
}

/**
 * Sort cards in the desired order: trumps first, then clubs, spades, hearts
 * @param {Array} cards - Array of card objects
 * @returns {Array} - Sorted array of card objects
 */
export function sortCards(cards) {
  return [...cards].sort((a, b) => {
    // First check if either card is a trump
    const aIsTrump = isTrumpCard(a);
    const bIsTrump = isTrumpCard(b);
    
    // If one is trump and the other isn't, the trump comes first
    if (aIsTrump && !bIsTrump) return -1;
    if (!aIsTrump && bIsTrump) return 1;
    
    // If both are trumps or both are not trumps, sort by suit
    if (aIsTrump && bIsTrump) {
      // Check for 10 of Hearts (highest trump)
      if (a.suit === 'HEARTS' && a.rank === 'TEN') return -1;
      if (b.suit === 'HEARTS' && b.rank === 'TEN') return 1;
      
      // For trumps, sort by rank first based on game variant
      if (gameState.gameVariant === 'KING_SOLO') {
        // In King Solo, Kings come first
        if (a.rank === 'KING' && b.rank !== 'KING') return -1;
        if (a.rank !== 'KING' && b.rank === 'KING') return 1;
        
        // If both are Kings, sort by suit
        if (a.rank === 'KING' && b.rank === 'KING') {
          // Clubs, Spades, Hearts, Diamonds
          const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
          return suitOrder[a.suit] - suitOrder[b.suit];
        }
      } else {
        // Normal sorting for other variants (Queens, Jacks, then Diamonds)
        if (a.rank === 'QUEEN' && b.rank !== 'QUEEN') return -1;
        if (a.rank !== 'QUEEN' && b.rank === 'QUEEN') return 1;
        if (a.rank === 'JACK' && b.rank !== 'JACK') return -1;
        if (a.rank !== 'JACK' && b.rank === 'JACK') return 1;
      }
      
      // If both are the same rank (both Queens, Kings, or Jacks), sort by suit
      if ((a.rank === 'QUEEN' && b.rank === 'QUEEN') || 
          (a.rank === 'KING' && b.rank === 'KING') || 
          (a.rank === 'JACK' && b.rank === 'JACK')) {
        // Clubs, Spades, Hearts, Diamonds
        const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
        return suitOrder[a.suit] - suitOrder[b.suit];
      }
      
      // If both are diamonds but not Queens or Jacks, sort by rank
      const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
      return rankOrder[a.rank] - rankOrder[b.rank];
    } else {
      // For non-trumps, sort by suit first: clubs, spades, hearts
      const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
      if (a.suit !== b.suit) {
        return suitOrder[a.suit] - suitOrder[b.suit];
      }
      
      // If same suit, sort by rank: Ace, 10, King, Queen, Jack, 9
      const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
      return rankOrder[a.rank] - rankOrder[b.rank];
    }
  });
}

/**
 * Play a card
 * @param {string} cardId - Card ID
 */
export function playCard(cardId) {
  console.log('Playing card:', cardId);
  
  // Debug output to help diagnose issues
  console.log("Current game state:", {
    currentPlayer: gameState.currentPlayer,
    hand: gameState.hand,
    legalActions: gameState.legalActions
  });
  
  // Find the card in the hand
  const card = gameState.hand.find(c => c.id === cardId);
  if (!card) {
    console.error("Card not found in hand:", cardId);
    return;
  }
  
  // Check if the card is in the legal actions
  const isPlayable = gameState.is_player_turn && 
                     gameState.legalActions && 
                     gameState.legalActions.some(legalCard => legalCard.id === cardId);
  
  console.log(`Card ${cardId} isPlayable:`, isPlayable);
  
  if (!isPlayable) {
    console.error("Card is not playable:", cardId);
    
    // Add a visual feedback for non-playable cards
    const cardElement = document.querySelector(`.card-container[data-card-id="${cardId}"]`);
    if (cardElement) {
      cardElement.style.border = "2px solid red";
      setTimeout(() => {
        cardElement.style.border = "";
      }, 500);
    }
    
    return;
  }
  
  // Optimistically update the UI to show the card being played
  // Add the card to the current trick
  const currentTrick = gameState.currentTrick || [];
  currentTrick.push(card);
  gameState.currentTrick = currentTrick;
  
  // Remove the card from the hand
  gameState.hand = gameState.hand.filter(c => c.id !== cardId);
  
  // Emit event that the game state has changed
  eventBus.emit('gameStateUpdated', gameState);
  
  // Send the card to the server
  fetch('/play_card', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      game_id: gameState.game_id,
      card_id: cardId
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log("Play card response:", data);
    
    // Update game state with the response data
    if (data.state) {
      // Update the game state
      gameState.hand = data.state.hand || [];
      gameState.currentTrick = data.state.current_trick || [];
      gameState.currentPlayer = data.state.current_player;
      gameState.is_player_turn = data.state.is_player_turn !== undefined ? data.state.is_player_turn : (gameState.currentPlayer === 0);
      gameState.legalActions = data.state.legal_actions || [];
      
      // Emit event that the game state has changed
      eventBus.emit('gameStateUpdated', gameState);
    }
    
    // Store the game summary if available
    if (data.game_summary) {
      gameState.gameSummary = data.game_summary;
    }
  })
  .catch(error => {
    console.error('Error playing card:', error);
    
    // Revert the optimistic update
    gameState.hand.push(card);
    gameState.currentTrick = gameState.currentTrick.filter(c => c.id !== cardId);
    
    // Emit event that the game state has changed
    eventBus.emit('gameStateUpdated', gameState);
  });
}

/**
 * Initialize card-related event listeners
 */
export function initCardEvents() {
  // Listen for card played events
  eventBus.on('cardPlayed', playCard);
}
