/**
 * AI players visualization
 */
import { gameState } from './game-core.js';
import { createCardElement } from './game-cards.js';

/**
 * Update AI card visualization
 */
export function updateAICardVisualization() {
  // Get the AI card visualization containers
  const player1Cards = document.getElementById('player1-cards');
  const player2Cards = document.getElementById('player2-cards');
  const player3Cards = document.getElementById('player3-cards');
  
  if (!player1Cards || !player2Cards || !player3Cards) return;
  
  // Clear previous content
  player1Cards.innerHTML = '';
  player2Cards.innerHTML = '';
  player3Cards.innerHTML = '';
  
  // Get the current trick container
  const hardcodedTrickEl = document.getElementById('hardcoded-trick');
  if (!hardcodedTrickEl) return;
  
  // Set up the trick area as a relative positioning context
  const trickArea = document.querySelector('.trick-area');
  if (trickArea) {
    trickArea.style.position = 'relative';
    
    // Get the parent containers for each player
    const player1Container = player1Cards.parentElement;
    const player2Container = player2Cards.parentElement;
    const player3Container = player3Cards.parentElement;
    
    if (player1Container && player2Container && player3Container) {
      // Move the player containers out of the AI card visualization and into the trick area
      trickArea.appendChild(player1Container);
      trickArea.appendChild(player2Container);
      trickArea.appendChild(player3Container);
      
      // Style the containers to position them around the current trick
      // Position Player 2 above the current trick
      player2Container.style.position = 'absolute';
      player2Container.style.top = '40px'; // Position above the "Current Trick" heading
      player2Container.style.left = '50%';
      player2Container.style.transform = 'translateX(-50%)';
      player2Container.style.width = '80%'; // Reduced from 100% to center more
      player2Container.style.textAlign = 'center';
      player2Container.style.zIndex = '10';
      
      // Position Player 1 on the left side of the current trick
      player1Container.style.position = 'absolute';
      player1Container.style.left = '25px'; // Moved more to the center (was 10px)
      player1Container.style.top = '50%';
      player1Container.style.transform = 'translateY(-50%)';
      player1Container.style.zIndex = '10';
      
      // Position Player 3 on the right side of the current trick
      player3Container.style.position = 'absolute';
      player3Container.style.right = '25px'; // Moved more to the center (was 10px)
      player3Container.style.top = '50%';
      player3Container.style.transform = 'translateY(-50%)';
      player3Container.style.zIndex = '10';
      
      // Adjust the styling of the player containers
      player1Container.style.border = 'none';
      player2Container.style.border = 'none';
      player3Container.style.border = 'none';
      player1Container.style.background = 'transparent';
      player2Container.style.background = 'transparent';
      player3Container.style.background = 'transparent';
      
      // Hide the headings
      const headings = [player1Container, player2Container, player3Container].map(
        container => container.querySelector('h5')
      );
      headings.forEach(heading => {
        if (heading) heading.style.display = 'none';
      });
    }
  }
  
  // Create mock cards for AI players
  for (let i = 1; i <= 3; i++) {
    const playerCardsEl = document.getElementById(`player${i}-cards`);
    if (!playerCardsEl) continue;
    
    // Get the number of cards for this AI player
    const cardCount = gameState.otherPlayers && gameState.otherPlayers[i-1] ? 
                      gameState.otherPlayers[i-1].card_count : 10;
    
    // Create a container for the cards
    const cardsContainer = document.createElement('div');
    
    // Set different layout for each player
    if (i === 1 || i === 3) {
      // Vertical layout for Players 1 and 3
      cardsContainer.style.display = 'flex';
      cardsContainer.style.flexDirection = 'column';
      cardsContainer.style.gap = '2px';
      cardsContainer.style.alignItems = 'center';
    } else {
      // Horizontal layout for Player 2
      cardsContainer.style.display = 'flex';
      cardsContainer.style.flexDirection = 'row';
      cardsContainer.style.gap = '2px';
      cardsContainer.style.justifyContent = 'center';
    }
    
    // Create card back images
    for (let j = 0; j < cardCount; j++) {
      const cardImg = document.createElement('img');
      cardImg.src = '/static/images/cards/back.png';
      cardImg.alt = 'Card back';
      cardImg.className = 'ai-card';
      
      if (i === 1 || i === 3) {
        // Smaller cards for vertical layout
        cardImg.style.width = '25px';
        cardImg.style.height = 'auto';
        cardImg.style.margin = '1px';
      } else {
        // Normal size for horizontal layout
        cardImg.style.width = '30px';
        cardImg.style.height = 'auto';
        cardImg.style.margin = '2px';
      }
      
      cardsContainer.appendChild(cardImg);
    }
    
    playerCardsEl.appendChild(cardsContainer);
    
    // Show team information only if the player has revealed their team (by playing a Queen of Clubs)
    if (gameState.otherPlayers && 
        gameState.otherPlayers[i-1] && 
        gameState.otherPlayers[i-1].team && 
        gameState.otherPlayers[i-1].revealed_team) {
      const team = gameState.otherPlayers[i-1].team;
      
      const teamInfo = document.createElement('div');
      teamInfo.textContent = `Team: ${team}`;
      teamInfo.style.marginTop = '5px';
      teamInfo.style.fontWeight = 'bold';
      
      // Add color coding for teams
      if (team === 'RE') {
        teamInfo.style.color = '#2ecc71'; // Green for RE
      } else if (team === 'KONTRA') {
        teamInfo.style.color = '#e74c3c'; // Red for KONTRA
      }
      
      playerCardsEl.appendChild(teamInfo);
    }
  }
  
  // Make sure the AI card visualization container is visible
  const aiCardVisualization = document.getElementById('ai-card-visualization');
  if (aiCardVisualization) {
    aiCardVisualization.style.display = 'block';
  }
}

/**
 * Reveal AI hands
 */
export function revealAIHands() {
  console.log('Revealing AI hands');
  
  // Make an API request to get the AI hands
  fetch(`/get_ai_hands?game_id=${gameState.game_id}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('AI hands data:', data);
      
      // Get the AI card visualization containers
      const player1Cards = document.getElementById('player1-cards');
      const player2Cards = document.getElementById('player2-cards');
      const player3Cards = document.getElementById('player3-cards');
      
      if (!player1Cards || !player2Cards || !player3Cards) {
        console.error('AI card containers not found');
        return;
      }
      
      // Make sure the AI card visualization container is visible
      const aiCardVisualization = document.getElementById('ai-card-visualization');
      if (aiCardVisualization) {
        aiCardVisualization.style.display = 'block';
      }
      
      // Clear previous content
      player1Cards.innerHTML = '';
      player2Cards.innerHTML = '';
      player3Cards.innerHTML = '';
      
      // Helper function to display AI player cards
      function displayAIPlayerCards(playerIndex, cards, container) {
        if (!cards || cards.length === 0) return;
        
        // Create a container for all cards
        const cardsContainer = document.createElement('div');
        
        // Split cards into two rows
        const firstRowContainer = document.createElement('div');
        firstRowContainer.style.display = 'flex';
        firstRowContainer.style.flexDirection = 'row';
        firstRowContainer.style.gap = '2px';
        firstRowContainer.style.marginBottom = '4px';
        
        const secondRowContainer = document.createElement('div');
        secondRowContainer.style.display = 'flex';
        secondRowContainer.style.flexDirection = 'row';
        secondRowContainer.style.gap = '2px';
        
        // Calculate how many cards go in each row
        const halfLength = Math.ceil(cards.length / 2);
        
        // Function to add cards to a row
        const addCardsToRow = (rowContainer, cardsToAdd) => {
          cardsToAdd.forEach(card => {
            const cardElement = createCardElement(card, false);
            // Make the cards larger
            const cardImg = cardElement.querySelector('img');
            if (cardImg) {
              cardImg.style.width = '40px';
              cardImg.style.height = 'auto';
            }
            rowContainer.appendChild(cardElement);
          });
        };
        
        // Add cards to both rows
        addCardsToRow(firstRowContainer, cards.slice(0, halfLength));
        addCardsToRow(secondRowContainer, cards.slice(halfLength));
        
        // Add both rows to the container
        cardsContainer.appendChild(firstRowContainer);
        cardsContainer.appendChild(secondRowContainer);
        
        container.appendChild(cardsContainer);
        
        // Add team information
        const otherPlayerIndex = playerIndex - 1; // Convert from 1-based to 0-based index for otherPlayers array
        if (gameState.otherPlayers && 
            gameState.otherPlayers[otherPlayerIndex] && 
            gameState.otherPlayers[otherPlayerIndex].team) {
          
          const team = gameState.otherPlayers[otherPlayerIndex].team;
          
          const teamInfo = document.createElement('div');
          teamInfo.textContent = `Team: ${team}`;
          teamInfo.style.marginTop = '5px';
          teamInfo.style.fontWeight = 'bold';
          
          // Add color coding for teams
          if (team === 'RE') {
            teamInfo.style.color = '#2ecc71'; // Green for RE
          } else if (team === 'KONTRA') {
            teamInfo.style.color = '#e74c3c'; // Red for KONTRA
          }
          
          container.appendChild(teamInfo);
        }
      }
      
      // Display cards for each AI player
      displayAIPlayerCards(1, data.player1, player1Cards);
      displayAIPlayerCards(2, data.player2, player2Cards);
      displayAIPlayerCards(3, data.player3, player3Cards);
      
      // Change the button text to indicate that hands are revealed
      const revealAIHandsBtn = document.getElementById('reveal-ai-hands-btn');
      if (revealAIHandsBtn) {
        revealAIHandsBtn.textContent = 'Refresh AI Hands';
      }
    })
    .catch(error => {
      console.error('Error revealing AI hands:', error);
      alert(`Error: ${error.message}`);
    });
}
