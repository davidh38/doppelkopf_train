/**
 * UI-related functions
 */
import { gameState } from './game-core.js';
import { eventBus } from './event-bus.js';
import { createCardElement, sortCards } from './game-cards.js';

// DOM elements
let gameSetupScreen;
let gameBoard;
let gameOverScreen;
let playerHandEl;
let currentTrickEl;
let turnIndicatorEl;
let playerTeamEl;
let gameVariantEl;
let reScoreEl;
let kontraScoreEl;

/**
 * Initialize UI elements
 */
export function initUI() {
  console.log("Initializing UI elements...");
  
  // Get DOM elements
  gameSetupScreen = document.getElementById('game-setup');
  gameBoard = document.getElementById('game-board');
  gameOverScreen = document.getElementById('game-over');
  
  console.log("DOM elements initialized:");
  console.log("gameSetupScreen:", gameSetupScreen);
  console.log("gameBoard:", gameBoard);
  console.log("gameOverScreen:", gameOverScreen);
  
  playerHandEl = document.getElementById('player-hand');
  currentTrickEl = document.getElementById('hardcoded-trick');
  turnIndicatorEl = document.getElementById('turn-indicator');
  playerTeamEl = document.getElementById('player-team');
  gameVariantEl = document.getElementById('game-variant');
  reScoreEl = document.getElementById('re-score');
  kontraScoreEl = document.getElementById('kontra-score');
  
  // Set up event listeners
  eventBus.on('gameStateUpdated', renderUI);
  eventBus.on('gameOver', showGameOverScreen);
}

/**
 * Render the UI based on the current game state
 */
export function renderUI() {
  renderHand();
  renderCurrentTrick();
  updateTurnIndicator();
  updateGameVariantDisplay();
  updateAICardVisualization();
  updateAnnouncementButtons();
  updateGameScores();
}

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
    playerLabel.textContent = pos.playerIdx === 0 ? 'You' : `Player ${pos.playerIdx}`;
    
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
      
      // No team information shown, just the player name
      playerLabel.textContent = pos.playerIdx === 0 ? 'You' : `Player ${pos.playerIdx}`;
      
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
 * Update the turn indicator
 */
export function updateTurnIndicator() {
  if (!turnIndicatorEl) return;
  
  if (gameState.currentPlayer === 0) {
    turnIndicatorEl.textContent = "Your turn";
  } else {
    turnIndicatorEl.textContent = `Waiting for Player ${gameState.currentPlayer}...`;
  }
}

/**
 * Update the game variant display
 */
export function updateGameVariantDisplay() {
  if (!gameVariantEl) return;
  
  // Create a more detailed variant display
  let variantText = gameState.gameVariant || 'NORMAL';
  gameVariantEl.textContent = variantText;
  
  // Add player variant selections in a more visible way
  if (gameState.playerVariants && Object.keys(gameState.playerVariants).length > 0) {
    // Create or get the player variants container
    let variantsContainer = document.getElementById('player-variants-container');
    if (!variantsContainer) {
      variantsContainer = document.createElement('div');
      variantsContainer.id = 'player-variants-container';
      variantsContainer.style.marginTop = '15px';
      variantsContainer.style.padding = '10px';
      variantsContainer.style.backgroundColor = '#f8f9fa';
      variantsContainer.style.borderRadius = '5px';
      variantsContainer.style.border = '1px solid #ddd';
      
      // Add a title
      const title = document.createElement('h4');
      title.textContent = 'Player Variant Selections';
      title.style.marginTop = '0';
      title.style.marginBottom = '10px';
      title.style.color = '#3498db';
      variantsContainer.appendChild(title);
      
      // Add the container after the game variant element
      const rightSidebar = document.querySelector('.right-sidebar');
      if (rightSidebar) {
        rightSidebar.appendChild(variantsContainer);
      }
    }
    
    // Clear previous content
    variantsContainer.innerHTML = '';
    
    // Add the title back
    const title = document.createElement('h4');
    title.textContent = 'Player Variant Selections';
    title.style.marginTop = '0';
    title.style.marginBottom = '10px';
    title.style.color = '#3498db';
    variantsContainer.appendChild(title);
    
    // Create a list of player variants
    const variantsList = document.createElement('ul');
    variantsList.style.listStyleType = 'none';
    variantsList.style.padding = '0';
    variantsList.style.margin = '0';
    
    for (let i = 0; i < 4; i++) {
      const playerVariant = gameState.playerVariants[i];
      if (playerVariant) {
        const listItem = document.createElement('li');
        listItem.style.padding = '5px 0';
        listItem.style.borderBottom = i < 3 ? '1px solid #eee' : 'none';
        
        // Format the variant name to be more readable
        const formattedVariant = playerVariant.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        listItem.textContent = i === 0 ? 
          `You: ${formattedVariant}` : 
          `Player ${i}: ${formattedVariant}`;
        
        // Highlight the player's own selection
        if (i === 0) {
          listItem.style.fontWeight = 'bold';
          listItem.style.color = '#2ecc71';
        }
        
        variantsList.appendChild(listItem);
      }
    }
    
    variantsContainer.appendChild(variantsList);
  }
}

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
 * Update the announcement buttons visibility
 */
export function updateAnnouncementButtons() {
  // Get the announcement buttons
  const gameReBtn = document.getElementById('game-re-btn');
  const gameContraBtn = document.getElementById('game-contra-btn');
  
  // Get the announcement areas
  const gameAnnouncementArea = document.getElementById('game-announcement-area');
  
  // Log current announcement state for debugging
  console.log("Updating announcement buttons with state:", {
    playerTeam: gameState.playerTeam,
    canAnnounceRe: gameState.canAnnounceRe,
    canAnnounceContra: gameState.canAnnounceContra,
    hasHochzeit: gameState.hasHochzeit,
    announcements: gameState.announcements
  });
  
  // First, determine if the player can announce Hochzeit
  const canAnnounceHochzeit = gameState.hasHochzeit && gameState.canAnnounce;
  console.log("Can announce hochzeit:", canAnnounceHochzeit, "hasHochzeit:", gameState.hasHochzeit, "canAnnounce:", gameState.canAnnounce);
  
  // Get the Hochzeit button if it exists
  let gameHochzeitBtn = document.getElementById('game-hochzeit-btn');
  
  // Get the announcement buttons container
  const announcementButtons = document.querySelector('.announcement-buttons');
  
  // Handle button creation/removal based on whether player has both Queens of Clubs
  if (gameState.hasHochzeit) {
    // Player has both Queens of Clubs - create button if it doesn't exist
    if (!gameHochzeitBtn && announcementButtons) {
      console.log("Creating Hochzeit button because player has both Queens of Clubs");
      gameHochzeitBtn = document.createElement('button');
      gameHochzeitBtn.id = 'game-hochzeit-btn';
      gameHochzeitBtn.className = 'btn announcement-btn';
      gameHochzeitBtn.textContent = 'Hochzeit (Marriage)';
      gameHochzeitBtn.onclick = () => eventBus.emit('makeAnnouncement', 'hochzeit');
      
      // Add the button to the announcement area
      announcementButtons.appendChild(gameHochzeitBtn);
    }
    
    // Now set visibility based on whether player can announce
    if (gameHochzeitBtn) {
      gameHochzeitBtn.style.display = canAnnounceHochzeit ? 'inline-block' : 'none';
      gameHochzeitBtn.disabled = !canAnnounceHochzeit;
      gameHochzeitBtn.style.opacity = canAnnounceHochzeit ? '1' : '0.5';
    }
  } else {
    // Player doesn't have both Queens of Clubs - remove button if it exists
    if (gameHochzeitBtn) {
      console.log("Removing Hochzeit button because player doesn't have both Queens of Clubs");
      gameHochzeitBtn.remove();
      gameHochzeitBtn = null;
    }
  }
  
  // Determine which announcement button to show based on the game state
  // For RE team
  if (gameState.playerTeam === 'RE') {
    
    // Show Re button for RE team
    if (gameReBtn) {
      gameReBtn.style.display = 'inline-block';
      
      // Check if announcements object exists and is properly initialized
      const hasAnnounced = gameState.announcements && gameState.announcements.re === true;
      
      if (!hasAnnounced) {
        gameReBtn.textContent = 'Re';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 're');
        gameReBtn.disabled = !gameState.canAnnounceRe;
        gameReBtn.style.opacity = gameState.canAnnounceRe ? '1' : '0.5';
      } else if (gameState.canAnnounceNo90) {
        gameReBtn.textContent = 'No 90';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no90');
        gameReBtn.disabled = !gameState.canAnnounceNo90;
        gameReBtn.style.opacity = gameState.canAnnounceNo90 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo60) {
        gameReBtn.textContent = 'No 60';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no60');
        gameReBtn.disabled = !gameState.canAnnounceNo60;
        gameReBtn.style.opacity = gameState.canAnnounceNo60 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo30) {
        gameReBtn.textContent = 'No 30';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no30');
        gameReBtn.disabled = !gameState.canAnnounceNo30;
        gameReBtn.style.opacity = gameState.canAnnounceNo30 ? '1' : '0.5';
      } else if (gameState.canAnnounceBlack) {
        gameReBtn.textContent = 'Black';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'black');
        gameReBtn.disabled = !gameState.canAnnounceBlack;
        gameReBtn.style.opacity = gameState.canAnnounceBlack ? '1' : '0.5';
      } else {
        gameReBtn.textContent = 'Re';
        gameReBtn.disabled = true;
        gameReBtn.style.opacity = '0.5';
      }
    }
    
    // Hide Contra button for RE team
    if (gameContraBtn) {
      gameContraBtn.style.display = 'none';
    }
  }
  // For KONTRA team
  else if (gameState.playerTeam === 'KONTRA') {
    
    // Show Contra button for KONTRA team
    if (gameContraBtn) {
      gameContraBtn.style.display = 'inline-block';
      
      // Check if announcements object exists and is properly initialized
      const hasAnnounced = gameState.announcements && gameState.announcements.contra === true;
      
      if (!hasAnnounced) {
        gameContraBtn.textContent = 'Contra';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'contra');
        gameContraBtn.disabled = !gameState.canAnnounceContra;
        gameContraBtn.style.opacity = gameState.canAnnounceContra ? '1' : '0.5';
      } else if (gameState.canAnnounceNo90) {
        gameContraBtn.textContent = 'No 90';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no90');
        gameContraBtn.disabled = !gameState.canAnnounceNo90;
        gameContraBtn.style.opacity = gameState.canAnnounceNo90 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo60) {
        gameContraBtn.textContent = 'No 60';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no60');
        gameContraBtn.disabled = !gameState.canAnnounceNo60;
        gameContraBtn.style.opacity = gameState.canAnnounceNo60 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo30) {
        gameContraBtn.textContent = 'No 30';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no30');
        gameContraBtn.disabled = !gameState.canAnnounceNo30;
        gameContraBtn.style.opacity = gameState.canAnnounceNo30 ? '1' : '0.5';
      } else if (gameState.canAnnounceBlack) {
        gameContraBtn.textContent = 'Black';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'black');
        gameContraBtn.disabled = !gameState.canAnnounceBlack;
        gameContraBtn.style.opacity = gameState.canAnnounceBlack ? '1' : '0.5';
      } else {
        gameContraBtn.textContent = 'Contra';
        gameContraBtn.disabled = true;
        gameContraBtn.style.opacity = '0.5';
      }
    }
    
    // Hide Re button for KONTRA team
    if (gameReBtn) {
      gameReBtn.style.display = 'none';
    }
  } else {
    // If player team is not yet determined, hide both buttons
    if (gameReBtn) gameReBtn.style.display = 'none';
    if (gameContraBtn) gameContraBtn.style.display = 'none';
  }
  
  // Show/hide the announcement areas based on whether announcements are allowed
  if (gameAnnouncementArea) {
    // Only show the announcement area if the player can make an announcement
    const canAnnounceRe = gameState.playerTeam === 'RE' && gameState.canAnnounceRe;
    const canAnnounceContra = gameState.playerTeam === 'KONTRA' && gameState.canAnnounceContra;
    const canAnnounceNo90 = gameState.canAnnounceNo90;
    const canAnnounceNo60 = gameState.canAnnounceNo60;
    const canAnnounceNo30 = gameState.canAnnounceNo30;
    const canAnnounceBlack = gameState.canAnnounceBlack;
    const canAnnounceHochzeit = gameState.hasHochzeit && gameState.canAnnounce;
    
    const canAnnounce = canAnnounceRe || canAnnounceContra || canAnnounceNo90 || 
                        canAnnounceNo60 || canAnnounceNo30 || canAnnounceBlack || 
                        canAnnounceHochzeit;
    
    console.log("Can announce anything:", canAnnounce, 
                "Re:", canAnnounceRe, 
                "Contra:", canAnnounceContra, 
                "Hochzeit:", canAnnounceHochzeit);
    
    gameAnnouncementArea.classList.toggle('hidden', !canAnnounce);
  }
  
  // Helper function to update announcement status visibility
  function updateAnnouncementStatus(elementId, isVisible) {
    const element = document.getElementById(elementId);
    if (element) {
      element.classList.toggle('hidden', !isVisible);
    }
  }
  
  // Update announcement status displays for all announcement types
  const announcementStatuses = [
    { id: 're-status', type: 're' },
    { id: 'contra-status', type: 'contra' },
    { id: 'game-re-status', type: 're' },
    { id: 'game-contra-status', type: 'contra' },
    { id: 'no90-status', type: 'no90' },
    { id: 'no60-status', type: 'no60' },
    { id: 'no30-status', type: 'no30' },
    { id: 'black-status', type: 'black' },
    { id: 'game-no90-status', type: 'no90' },
    { id: 'game-no60-status', type: 'no60' },
    { id: 'game-no30-status', type: 'no30' },
    { id: 'game-black-status', type: 'black' }
  ];
  
  // Update visibility for each announcement status element
  announcementStatuses.forEach(status => {
    const isVisible = gameState.announcements && gameState.announcements[status.type];
    updateAnnouncementStatus(status.id, isVisible);
  });
  
  // Update multiplier displays
  const multiplierEl = document.getElementById('multiplier');
  const gameMultiplierEl = document.getElementById('game-multiplier');
  
  if (multiplierEl) {
    multiplierEl.textContent = `${gameState.multiplier || 1}x`;
  }
  
  if (gameMultiplierEl) {
    gameMultiplierEl.textContent = `${gameState.multiplier || 1}x`;
  }
}

/**
 * Update the game scores
 */
export function updateGameScores() {
  if (!reScoreEl || !kontraScoreEl) return;
  
  // Update the score displays
  reScoreEl.textContent = gameState.scores[0];
  kontraScoreEl.textContent = gameState.scores[1];
  
  // Fetch the scoreboard data from the server
  fetch('/get_scoreboard')
    .then(response => response.json())
    .then(scoreboard => {
      console.log('Fetched scoreboard:', scoreboard);
      
      // Update individual player scores in the sidebar
      const playerScoreEl = document.getElementById('player-score');
      const player1ScoreEl = document.getElementById('player-1-score-sidebar');
      const player2ScoreEl = document.getElementById('player-2-score-sidebar');
      const player3ScoreEl = document.getElementById('player-3-score-sidebar');
      
      // Update the player scores from the scoreboard
      if (scoreboard && scoreboard.player_scores && scoreboard.player_scores.length === 4) {
        if (playerScoreEl) playerScoreEl.textContent = scoreboard.player_scores[0];
        if (player1ScoreEl) player1ScoreEl.textContent = scoreboard.player_scores[1];
        if (player2ScoreEl) player2ScoreEl.textContent = scoreboard.player_scores[2];
        if (player3ScoreEl) player3ScoreEl.textContent = scoreboard.player_scores[3];
      }
    })
    .catch(error => {
      console.error('Error fetching scoreboard:', error);
      
      // Fallback to using the scores from the game state
      const playerScoreEl = document.getElementById('player-score');
      const player1ScoreEl = document.getElementById('player-1-score-sidebar');
      const player2ScoreEl = document.getElementById('player-2-score-sidebar');
      const player3ScoreEl = document.getElementById('player-3-score-sidebar');
      
      if (gameState.playerScores && gameState.playerScores.length === 4) {
        if (playerScoreEl) playerScoreEl.textContent = gameState.playerScores[0];
        if (player1ScoreEl) player1ScoreEl.textContent = gameState.playerScores[1];
        if (player2ScoreEl) player2ScoreEl.textContent = gameState.playerScores[2];
        if (player3ScoreEl) player3ScoreEl.textContent = gameState.playerScores[3];
      }
    });
}

/**
 * Show the game over screen
 */
export function showGameOverScreen() {
  console.log("Showing game over screen");
  
  // Redirect to the game summary page
  if (gameState.gameId) {
    window.location.href = `/game-summary/${gameState.gameId}`;
  } else {
    console.error("Game ID not found, cannot redirect to game summary");
    
    // Fallback to the old behavior if game ID is not available
    // Hide the game board
    if (gameBoard) {
      gameBoard.classList.add('hidden');
    }
    
    // Show the game over screen
    if (gameOverScreen) {
      gameOverScreen.classList.remove('hidden');
      
      // Get the winner display element
      const gameResultEl = document.getElementById('game-result');
      if (gameResultEl) {
        // Clear any previous content
        gameResultEl.innerHTML = '';
        
        const winnerTeam = gameState.winner === 'RE' ? 'RE' : 'KONTRA';
        const winnerHeader = document.createElement('h3');
        winnerHeader.id = 'winner';
        winnerHeader.textContent = `Team ${winnerTeam} wins!`;
        winnerHeader.style.color = winnerTeam === 'RE' ? '#2ecc71' : '#e74c3c';
        gameResultEl.appendChild(winnerHeader);
        
        // Add game summary if available
        if (gameState.gameSummary) {
          console.log("Adding game summary to game over screen");
          const summaryEl = document.createElement('pre');
          summaryEl.textContent = gameState.gameSummary;
          summaryEl.style.textAlign = 'left';
          summaryEl.style.margin = '20px auto';
          summaryEl.style.padding = '15px';
          summaryEl.style.backgroundColor = '#f8f9fa';
          summaryEl.style.border = '1px solid #ddd';
          summaryEl.style.borderRadius = '5px';
          summaryEl.style.maxWidth = '600px';
          summaryEl.style.whiteSpace = 'pre-wrap';
          summaryEl.style.fontSize = '14px';
          summaryEl.style.fontFamily = 'monospace';
          gameResultEl.appendChild(summaryEl);
        } else {
          console.log("No game summary available");
        }
      }
      
      // Update the final score elements
      const finalReScoreEl = document.getElementById('final-re-score');
      const finalKontraScoreEl = document.getElementById('final-kontra-score');
      const finalMultiplierEl = document.getElementById('final-multiplier');
      
      if (finalReScoreEl) {
        finalReScoreEl.textContent = gameState.scores[0];
      }
      
      if (finalKontraScoreEl) {
        finalKontraScoreEl.textContent = gameState.scores[1];
      }
      
      if (finalMultiplierEl) {
        finalMultiplierEl.textContent = `${gameState.multiplier || 1}x`;
      }
      
      // Update the announcement status elements
      const finalReStatus = document.getElementById('final-re-status');
      const finalContraStatus = document.getElementById('final-contra-status');
      const finalNo90Status = document.getElementById('final-no90-status');
      const finalNo60Status = document.getElementById('final-no60-status');
      const finalNo30Status = document.getElementById('final-no30-status');
      const finalBlackStatus = document.getElementById('final-black-status');
      
      if (finalReStatus) {
        finalReStatus.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.re));
      }
      
      if (finalContraStatus) {
        finalContraStatus.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.contra));
      }
      
      if (finalNo90Status) {
        finalNo90Status.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.no90));
      }
      
      if (finalNo60Status) {
        finalNo60Status.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.no60));
      }
      
      if (finalNo30Status) {
        finalNo30Status.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.no30));
      }
      
      if (finalBlackStatus) {
        finalBlackStatus.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.black));
      }
    }
  }
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

/**
 * Reveal AI hands
 */
export function revealAIHands() {
  console.log('Revealing AI hands');
  
  // Make an API request to get the AI hands
  fetch(`/get_ai_hands?game_id=${gameState.gameId}`)
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
