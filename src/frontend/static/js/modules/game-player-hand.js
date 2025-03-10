/**
 * Player's hand management
 */
import { gameState } from './game-core.js';
import { playerHandEl } from './game-ui-core.js';
import { createCardElement, sortCards } from './game-cards.js';

/**
 * Render the player's hand
 */
export function renderHand() {
  if (!playerHandEl) return;
  
  playerHandEl.innerHTML = '';
  
  // Debug output to help diagnose issues
  console.log("Rendering hand with state:", {
    currentPlayer: gameState.currentPlayer,
    hand: gameState.hand,
    legalActions: gameState.legalActions
  });
  
  // Sort the cards: trumps first, then clubs, spades, hearts
  const sortedHand = sortCards(gameState.hand);
  
  // Render the sorted hand
  sortedHand.forEach(card => {
    // Check if the card is in the legal actions
    const isPlayable = gameState.currentPlayer === 0 && 
                       gameState.legalActions && 
                       gameState.legalActions.some(legalCard => legalCard.id === card.id);
    
    console.log(`Card ${card.id} (${card.rank} of ${card.suit}) isPlayable:`, isPlayable);
    
    // Only make cards playable if they are legal moves
    const cardElement = createCardElement(card, isPlayable);
    
    // Add a debug click handler to the card container
    cardElement.addEventListener('click', () => {
      console.log(`Card container clicked: ${card.id} (${card.rank} of ${card.suit}), isPlayable: ${isPlayable}`);
      
      // If it's not playable, show a message
      if (!isPlayable) {
        console.log("This card is not playable right now");
        
        // Add a temporary visual feedback
        cardElement.style.border = "2px solid red";
        setTimeout(() => {
          cardElement.style.border = "";
        }, 500);
      }
    });
    
    playerHandEl.appendChild(cardElement);
  });
  
  // If it's the player's turn, add a message to indicate they can play
  if (gameState.currentPlayer === 0) {
    const messageEl = document.createElement('div');
    messageEl.style.textAlign = 'center';
    messageEl.style.marginTop = '10px';
    messageEl.style.fontWeight = 'bold';
    messageEl.style.color = '#2ecc71';
    messageEl.textContent = 'Your turn! Click a card to play it.';
    playerHandEl.appendChild(messageEl);
  }
}
