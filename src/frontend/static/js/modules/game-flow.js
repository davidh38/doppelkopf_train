/**
 * Game flow functions
 */
import { gameState, resetGameState } from './game-core.js';
import { eventBus } from './event-bus.js';

/**
 * Start a new game
 */
export function startNewGame() {
  console.log("Starting new game...");
  
  // Show progress container and hide the new game button
  const newGameBtn = document.getElementById('new-game-btn');
  const progressContainer = document.getElementById('progress-container');
  const progressBarFill = document.getElementById('progress-bar-fill');
  const progressMessage = document.getElementById('progress-message');
  const gameSetupScreen = document.getElementById('game-setup');
  const gameBoard = document.getElementById('game-board');
  
  if (newGameBtn) newGameBtn.classList.add('hidden');
  if (progressContainer) progressContainer.classList.remove('hidden');
  
  // Hide the game setup screen and show the game board
  if (gameSetupScreen) gameSetupScreen.classList.add('hidden');
  if (gameBoard) {
    gameBoard.style.display = 'grid';
    console.log("Game board display set to grid");
  }
  
  // Reset progress bar
  if (progressBarFill) progressBarFill.style.width = '10%';
  if (progressMessage) progressMessage.textContent = "Initializing game...";
  
  // Make the API request
  fetch('/new_game', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("New game response:", data);
    
    gameState.gameId = data.game_id;
    
    // Join the Socket.IO room for this game
    eventBus.emit('joinRoom', { game_id: gameState.gameId });
    
    // Update game state with the response data
    if (data.state) {
      gameState.hand = data.state.hand || [];
      gameState.currentPlayer = data.state.current_player;
      gameState.playerTeam = data.state.player_team;
      gameState.gameVariant = data.state.game_variant;
      gameState.legalActions = data.state.legal_actions || [];
      gameState.cardGiver = data.state.card_giver;
      
      // Update the card giver display in the variant selection area
      const cardGiverName = document.getElementById('card-giver-name');
      if (cardGiverName) {
        cardGiverName.textContent = gameState.cardGiver === 0 ? 'You' : `Player ${gameState.cardGiver}`;
      }
      
      // Update hasHochzeit property to control Hochzeit button visibility
      if (data.state.has_hochzeit !== undefined) {
        console.log("Updating hasHochzeit from new_game response:", data.state.has_hochzeit);
        gameState.hasHochzeit = data.state.has_hochzeit;
      }
      
      // Update canAnnounce property
      if (data.state.can_announce !== undefined) {
        gameState.canAnnounce = data.state.can_announce;
      }
      
      // Emit event that game state has been updated
      eventBus.emit('gameStateUpdated', gameState);
    }
  })
  .catch(error => {
    console.error('Error starting new game:', error);
    
    // Show error message
    if (progressMessage) {
      progressMessage.textContent = "Error starting game. Please try again.";
      progressMessage.style.color = "#e74c3c";
    }
    
    // Show the new game button again
    if (newGameBtn) newGameBtn.classList.remove('hidden');
  });
}

/**
 * Set the game variant
 * @param {string} variant - Game variant
 */
export function setGameVariant(variant) {
  console.log("Setting game variant:", variant);
  
  // Debug output to help diagnose issues
  console.log("Current game state before setting variant:", {
    currentPlayer: gameState.currentPlayer,
    hand: gameState.hand,
    legalActions: gameState.legalActions
  });
  
  // Emit event that game state has been updated to make sure the player's hand is visible during variant selection
  eventBus.emit('gameStateUpdated', gameState);
  
  fetch('/set_variant', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      game_id: gameState.gameId,
      variant: variant
    })
  })
  .then(response => {
    if (!response.ok) {
      console.log(`Server returned ${response.status}: ${response.statusText}`);
      // If we get a 400 error, the game is likely not in variant selection phase anymore
      // Just show the game board
      if (response.status === 400) {
        console.log("Got 400 response, showing game board anyway");
        
        // Make sure the game board is visible
        const gameBoard = document.getElementById('game-board');
        if (gameBoard) {
          console.log("Showing game board");
          // First make sure the element is visible in the DOM
          gameBoard.style.display = "grid";
          
          // Then remove the hidden class
          gameBoard.classList.remove('hidden');
          
          // Force a reflow to ensure the DOM updates
          void gameBoard.offsetWidth;
          
          console.log("gameBoard classes after showing:", gameBoard.className);
          console.log("gameBoard style.display:", gameBoard.style.display);
        }
        
        // Hide the variant selection area in the game board
        const gameVariantSelection = document.getElementById('game-variant-selection');
        if (gameVariantSelection) {
          gameVariantSelection.classList.add('hidden');
        }
      }
      return Promise.resolve({state: {}}); // Return an empty state object to avoid errors
    }
    return response.json();
  })
  .then(data => {
    console.log("Set variant response:", data);
    
    // Update game state with the response data
    if (data.state) {
      gameState.hand = data.state.hand || [];
      gameState.gameVariant = data.state.game_variant;
      gameState.legalActions = data.state.legal_actions || [];

      if (data.state.current_player !== undefined) {
        gameState.currentPlayer = data.state.current_player;
      }
      
      // Update announcement capabilities
      gameState.canAnnounceRe = data.state.can_announce_re || false;
      gameState.canAnnounceContra = data.state.can_announce_contra || false;
      gameState.canAnnounceNo90 = data.state.can_announce_no90 || false;
      gameState.canAnnounceNo60 = data.state.can_announce_no60 || false;
      gameState.canAnnounceNo30 = data.state.can_announce_no30 || false;
      gameState.canAnnounceBlack = data.state.can_announce_black || false;
      
      // Update hasHochzeit property to control Hochzeit button visibility
      if (data.state.has_hochzeit !== undefined) {
        console.log("Updating hasHochzeit from set_variant response:", data.state.has_hochzeit);
        gameState.hasHochzeit = data.state.has_hochzeit;
      }
      
      // Update canAnnounce property
      if (data.state.can_announce !== undefined) {
        gameState.canAnnounce = data.state.can_announce;
      }
      
      // Debug output to help diagnose issues
      console.log("Updated game state after setting variant:", {
        currentPlayer: gameState.currentPlayer,
        hand: gameState.hand,
        legalActions: gameState.legalActions
      });
      
      // Emit event that game state has been updated
      eventBus.emit('gameStateUpdated', gameState);
    }
    
    // Make sure the game board is visible
    const gameBoard = document.getElementById('game-board');
    if (gameBoard) {
      console.log("Showing game board");
      // First make sure the element is visible in the DOM
      gameBoard.style.display = "grid";
      
      // Then remove the hidden class
      gameBoard.classList.remove('hidden');
      
      // Force a reflow to ensure the DOM updates
      void gameBoard.offsetWidth;
      
      console.log("gameBoard classes after showing:", gameBoard.className);
      console.log("gameBoard style.display:", gameBoard.style.display);
    }
    
    // Hide the variant selection area in the game board
    const gameVariantSelection = document.getElementById('game-variant-selection');
    if (gameVariantSelection) {
      gameVariantSelection.classList.add('hidden');
    }
    
    // Force a re-render of the hand to make sure the cards are properly displayed
    eventBus.emit('gameStateUpdated', gameState);
  })
  .catch(error => {
    console.error('Error setting game variant:', error);
    
    // Even if there's an error, make sure the game board is visible
    const gameBoard = document.getElementById('game-board');
    if (gameBoard) {
      console.log("Showing game board despite error");
      gameBoard.style.display = "grid";
      gameBoard.classList.remove('hidden');
    }
  });
}

/**
 * Make an announcement (Re, Contra, or additional announcements)
 * @param {string} announcement - Announcement type
 */
export function makeAnnouncement(announcement) {
  console.log(`Making announcement: ${announcement}`);
  
  fetch('/announce', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      game_id: gameState.gameId,
      announcement: announcement
    })
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      });
    }
    return response.json();
  })
  .then(data => {
    console.log("Announcement response:", data);
    
    // Update game state with the response data
    if (data.state) {
      // Update the game state
      gameState.hand = data.state.hand || gameState.hand;
      gameState.currentTrick = data.state.current_trick || gameState.currentTrick;
      gameState.currentPlayer = data.state.current_player;
      gameState.legalActions = data.state.legal_actions || gameState.legalActions;
      gameState.canAnnounceRe = data.state.can_announce_re || false;
      gameState.canAnnounceContra = data.state.can_announce_contra || false;
      gameState.canAnnounceNo90 = data.state.can_announce_no90 || false;
      gameState.canAnnounceNo60 = data.state.can_announce_no60 || false;
      gameState.canAnnounceNo30 = data.state.can_announce_no30 || false;
      gameState.canAnnounceBlack = data.state.can_announce_black || false;
      
      // Update hasHochzeit property to control Hochzeit button visibility
      if (data.state.has_hochzeit !== undefined) {
        console.log("Updating hasHochzeit from announcement response:", data.state.has_hochzeit);
        gameState.hasHochzeit = data.state.has_hochzeit;
      }
      
      // Update canAnnounce property
      if (data.state.can_announce !== undefined) {
        gameState.canAnnounce = data.state.can_announce;
      }
      
      // Update announcements
      if (!gameState.announcements) {
        gameState.announcements = {};
      }
      
      // Update the specific announcement that was made
      if (announcement === 're') {
        gameState.announcements.re = true;
      } else if (announcement === 'contra') {
        gameState.announcements.contra = true;
      } else if (announcement === 'no90') {
        gameState.announcements.no90 = true;
      } else if (announcement === 'no60') {
        gameState.announcements.no60 = true;
      } else if (announcement === 'no30') {
        gameState.announcements.no30 = true;
      } else if (announcement === 'black') {
        gameState.announcements.black = true;
      }
      
      // Update multiplier
      gameState.multiplier = data.multiplier || gameState.multiplier;
    } else {
      // If no state is returned, update from the individual fields
      if (data.re_announced !== undefined) gameState.announcements.re = data.re_announced;
      if (data.contra_announced !== undefined) gameState.announcements.contra = data.contra_announced;
      if (data.no90_announced !== undefined) gameState.announcements.no90 = data.no90_announced;
      if (data.no60_announced !== undefined) gameState.announcements.no60 = data.no60_announced;
      if (data.no30_announced !== undefined) gameState.announcements.no30 = data.no30_announced;
      if (data.black_announced !== undefined) gameState.announcements.black = data.black_announced;
      
      if (data.multiplier !== undefined) gameState.multiplier = data.multiplier;
    }
    
    // Emit event that game state has been updated
    eventBus.emit('gameStateUpdated', gameState);
  })
  .catch(error => {
    console.error('Error making announcement:', error);
    alert(`Error: ${error.message}`);
  });
}

/**
 * Play again (start a new game after game over)
 */
export function playAgain() {
  // Hide the game over screen
  const gameOverScreen = document.getElementById('game-over');
  if (gameOverScreen) {
    gameOverScreen.classList.add('hidden');
  }
  
  // Reset the game state
  resetGameState();
  
  // Start a new game directly
  startNewGame();
}

/**
 * Initialize game flow event listeners
 */
export function initGameFlowEvents() {
  // Listen for announcement events
  eventBus.on('makeAnnouncement', makeAnnouncement);
  
  // Add event listener for the play again button
  const playAgainBtn = document.getElementById('play-again-btn');
  if (playAgainBtn) {
    playAgainBtn.addEventListener('click', playAgain);
  }
  
  // Add event listener for the new game buttons
  const newGameBtn = document.getElementById('new-game-btn');
  const newGameSidebarBtn = document.getElementById('new-game-sidebar-btn');
  
  if (newGameBtn) {
    newGameBtn.addEventListener('click', startNewGame);
  }
  
  if (newGameSidebarBtn) {
    newGameSidebarBtn.addEventListener('click', startNewGame);
  }
  
  // Add event listeners for variant selection buttons
  const normalBtn = document.getElementById('normal-btn');
  const hochzeitBtn = document.getElementById('hochzeit-btn');
  const queenSoloBtn = document.getElementById('queen-solo-btn');
  const jackSoloBtn = document.getElementById('jack-solo-btn');
  const kingSoloBtn = document.getElementById('king-solo-btn');
  const fleshlessBtn = document.getElementById('fleshless-btn');
  const trumpSoloBtn = document.getElementById('trump-btn');
  
  if (normalBtn) normalBtn.addEventListener('click', () => setGameVariant('normal'));
  if (trumpSoloBtn) trumpSoloBtn.addEventListener('click', () => setGameVariant('trump_solo'));
  if (hochzeitBtn) {
    // Disable the hochzeit button if the player doesn't have two Queens of Clubs
    eventBus.on('gameStateUpdated', () => {
      if (hochzeitBtn) {
        if (!gameState.hasHochzeit) {
          hochzeitBtn.disabled = true;
          hochzeitBtn.classList.add('disabled');
          hochzeitBtn.title = "You need two Queens of Clubs to select Hochzeit";
        } else {
          hochzeitBtn.disabled = false;
          hochzeitBtn.classList.remove('disabled');
          hochzeitBtn.title = "";
        }
      }
    });
    
    hochzeitBtn.addEventListener('click', () => {
      // Only allow hochzeit if the player has two Queens of Clubs
      if (gameState.hasHochzeit) {
        setGameVariant('hochzeit');
      } else {
        console.log("Cannot select Hochzeit: Player does not have two Queens of Clubs");
        // Provide visual feedback to the user
        hochzeitBtn.classList.add('btn-error');
        setTimeout(() => {
          hochzeitBtn.classList.remove('btn-error');
        }, 1000);
        // Optionally show a message to the user
        alert("You can only select Hochzeit (Marriage) if you have two Queens of Clubs");
      }
    });
  }
  if (queenSoloBtn) queenSoloBtn.addEventListener('click', () => setGameVariant('queen_solo'));
  if (jackSoloBtn) jackSoloBtn.addEventListener('click', () => setGameVariant('jack_solo'));
  if (kingSoloBtn) kingSoloBtn.addEventListener('click', () => setGameVariant('king_solo'));
  if (fleshlessBtn) fleshlessBtn.addEventListener('click', () => setGameVariant('fleshless'));
  
  // Add event listener for the Show Last Trick button
  const showLastTrickBtn = document.getElementById('show-last-trick-btn');
  if (showLastTrickBtn) {
    showLastTrickBtn.addEventListener('click', () => eventBus.emit('showLastTrick'));
  }
  
  // Add event listener for the Reveal AI Hands button
  const revealAIHandsBtn = document.getElementById('reveal-ai-hands-btn');
  if (revealAIHandsBtn) {
    revealAIHandsBtn.addEventListener('click', () => eventBus.emit('revealAIHands'));
  }
}
