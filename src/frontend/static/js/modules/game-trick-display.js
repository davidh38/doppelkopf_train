/**
 * Trick visualization
 */
import { gameState } from './game-core.js';
import { currentTrickEl } from './game-ui-core.js';
import { createCardElement } from './game-cards.js';

/**
 * Render the current trick
 */
export function renderCurrentTrick() {
  console.log("Rendering current trick, player turn:", gameState.currentPlayer === 0);
  
  // Get the hardcoded trick element
  if (!currentTrickEl) return;
  
  // Clear the trick element
  currentTrickEl.innerHTML = '';
  
  // Add a class to the trick element to enforce the grid layout
  currentTrickEl.className = 'trick-grid';
  
  // ALWAYS set up the grid layout, even if there are no cards yet
  // This ensures the layout doesn't change when it's the user's turn
  // Force grid display with !important to override any other styles
  currentTrickEl.style.cssText = `
    display: grid !important;
    grid-template-areas: 
        ".     top    ."
        "left  .      right"
        ".     bottom .";
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: 1fr 1fr 1fr;
    gap: 10px;
    width: 300px;
    height: 300px;
    margin: 0 auto;
    position: relative;
  `;
  
  // Calculate the starting player for this trick
  // Use ((n % m) + m) % m to ensure positive modulo result
  const startingPlayer = ((gameState.currentPlayer - gameState.currentTrick.length) % 4 + 4) % 4;
  
  // Create placeholders for all four positions
  const positions = [
    { position: "bottom", playerIdx: 0, gridArea: "bottom", justifySelf: "center" },
    { position: "left", playerIdx: 1, gridArea: "left", justifySelf: "start" },
    { position: "top", playerIdx: 2, gridArea: "top", justifySelf: "center" },
    { position: "right", playerIdx: 3, gridArea: "right", justifySelf: "end" }
  ];
  
  // Create a container for each position (whether there's a card or not)
  positions.forEach(pos => {
    // Create a container for the card and player label
    const cardContainer = document.createElement('div');
    cardContainer.className = 'trick-card-container';
    cardContainer.style.gridArea = pos.gridArea;
    cardContainer.style.justifySelf = pos.justifySelf;
    
    // Create a player label
    const playerLabel = document.createElement('div');
    playerLabel.className = 'player-label';
    
    // Add card giver indicator in brackets if applicable
    const isCardGiver = pos.playerIdx === gameState.cardGiver;
    const cardGiverText = isCardGiver ? ' (Card Giver)' : '';
    playerLabel.textContent = pos.playerIdx === 0 ? 
      `You${cardGiverText}` : 
      `Player ${pos.playerIdx}${cardGiverText}`;
    
    // Position the label based on the position
    if (pos.position === "bottom") {
      cardContainer.style.flexDirection = "column";
      playerLabel.style.order = "1"; // Label below card
    } else if (pos.position === "top") {
      cardContainer.style.flexDirection = "column";
      playerLabel.style.order = "-1"; // Label above card
    } else if (pos.position === "left") {
      cardContainer.style.flexDirection = "row";
      playerLabel.style.marginRight = "10px";
    } else if (pos.position === "right") {
      cardContainer.style.flexDirection = "row-reverse";
      playerLabel.style.marginLeft = "10px";
    }
    
    // Add the player label to the container
    cardContainer.appendChild(playerLabel);
    
    // Check if there's a card for this position
    const cardIndex = (4 + pos.playerIdx - startingPlayer) % 4;
    if (gameState.currentTrick && gameState.currentTrick.length > cardIndex) {
      const card = gameState.currentTrick[cardIndex];
      
      // Create the card element
      const cardElement = createCardElement(card, false); // Cards in the trick are not playable
      
      // Add card giver indicator in brackets if applicable
      const isCardGiver = pos.playerIdx === gameState.cardGiver;
      const cardGiverText = isCardGiver ? ' (Card Giver)' : '';
      playerLabel.textContent = pos.playerIdx === 0 ? 
        `You${cardGiverText}` : 
        `Player ${pos.playerIdx}${cardGiverText}`;
      
      // Add the card to the container
      cardContainer.appendChild(cardElement);
    } else {
      // Add an empty placeholder for the card
      const emptyCard = document.createElement('div');
      emptyCard.style.width = '120px';
      emptyCard.style.height = '170px';
      emptyCard.style.visibility = 'hidden';
      cardContainer.appendChild(emptyCard);
    }
    
    // Add the container to the trick display
    currentTrickEl.appendChild(cardContainer);
  });
}

/**
 * Show the last trick
 */
export function showLastTrick() {
  console.log('Showing last trick');
  
  // Get the last trick container
  const lastTrickContainer = document.querySelector('.last-trick-container');
  const lastTrickEl = document.getElementById('last-trick');
  const trickWinnerEl = document.getElementById('trick-winner');
  
  if (!lastTrickContainer || !lastTrickEl || !trickWinnerEl) {
    console.error('Last trick elements not found');
    return;
  }
  
  // Make an API request to get the last trick
  fetch(`/get_last_trick?game_id=${gameState.gameId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Last trick data:', data);
      
      // Clear the last trick element
      lastTrickEl.innerHTML = '';
      
      // If there's no last trick, show a message
      if (!data.last_trick || data.last_trick.length === 0) {
        trickWinnerEl.textContent = 'No last trick available';
        return;
      }
      
      // Create a container for each card with player information
      for (let i = 0; i < data.last_trick.length; i++) {
        const card = data.last_trick[i];
        
        // Create the card element
        const cardElement = createCardElement(card, false); // Cards in the last trick are not playable
        
        // Add the card to the last trick display
        lastTrickEl.appendChild(cardElement);
      }
      
      // Show the trick winner
      const winnerName = data.winner === 0 ? 'You' : `Player ${data.winner}`;
      trickWinnerEl.textContent = `Winner: ${winnerName} (${data.trick_points} points)`;
      
      // Show the last trick container
      lastTrickContainer.classList.remove('hidden');
      
      // Hide the current trick container
      const trickArea = document.querySelector('.trick-area');
      if (trickArea) {
        trickArea.style.display = 'none';
      }
      
      // Check if a close button already exists
      const existingCloseButton = lastTrickContainer.querySelector('.close-trick-btn');
      
      if (!existingCloseButton) {
        // Add a close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'btn close-trick-btn';
        closeButton.style.marginTop = '10px';
        closeButton.addEventListener('click', () => {
          // Hide the last trick container
          lastTrickContainer.classList.add('hidden');
          
          // Show the current trick container
          if (trickArea) {
            trickArea.style.display = 'block';
          }
        });
        
        // Add the close button to the last trick container
        lastTrickContainer.appendChild(closeButton);
      }
    })
    .catch(error => {
      console.error('Error getting last trick:', error);
      trickWinnerEl.textContent = 'Error getting last trick';
    });
}
