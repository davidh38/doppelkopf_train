/**
 * Socket.IO event handling
 */
import { eventBus } from './event-bus.js';
import { updateGameState, gameState } from './game-core.js';
import { showGameOverScreen } from './game-ui.js';

// Socket.IO instance
let socket;

/**
 * Initialize Socket.IO
 */
export function initSocket() {
  console.log("Initializing Socket.IO...");
  
  // Initialize Socket.IO
  socket = io();
  
  // Socket.IO event handlers
  socket.on('connect', function() {
    console.log('Connected to server');
  });
  
  socket.on('game_update', function(data) {
    console.log('Received game update:', data);
    
    // Debug output to help diagnose issues
    console.log("Current game state before update:", {
      currentPlayer: gameState.currentPlayer,
      hand: gameState.hand,
      legalActions: gameState.legalActions
    });
    
    // Update game state with the response data
    updateGameState(data);
    
    // Debug output to help diagnose issues
    console.log("Updated game state after update:", {
      currentPlayer: gameState.currentPlayer,
      hand: gameState.hand,
      legalActions: gameState.legalActions
    });
    
    // Check if the game is over
    if (data.game_over) {
      console.log("Game over detected, showing game over screen directly");
      showGameOverScreen();
    }
  });
  
  socket.on('trick_completed', function(data) {
    console.log('Trick completed:', data);
    eventBus.emit('trickCompleted', data);
  });
  
  socket.on('progress_update', function(data) {
    console.log('Progress update:', data);
    eventBus.emit('progressUpdate', data);
  });
  
  socket.on('ai_selecting_variant', function(data) {
    console.log('AI selecting variant:', data);
    eventBus.emit('aiSelectingVariant', data);
  });
  
  // Listen for events from other modules
  eventBus.on('joinRoom', function(data) {
    socket.emit('join', { game_id: data.game_id });
    console.log(`Joined game room: ${data.game_id}`);
  });
}

/**
 * Handle progress updates
 * @param {Object} data - Progress update data
 */
export function handleProgressUpdate(data) {
  // Get progress elements
  const progressMessage = document.getElementById('progress-message');
  const progressBarFill = document.getElementById('progress-bar-fill');
  
  if (!progressMessage || !progressBarFill) return;
  
  // Update the progress message
  progressMessage.textContent = data.message;
  
  // Update progress bar based on the step
  switch(data.step) {
    case 'model_loading_start':
      progressBarFill.style.width = '30%';
      break;
    case 'model_loading_details':
      progressBarFill.style.width = '35%';
      break;
    case 'model_loading_success':
      progressBarFill.style.width = '40%';
      progressMessage.style.color = "#2ecc71"; // Green color for success
      break;
    case 'model_loading_error':
    case 'model_loading_fallback':
      progressBarFill.style.width = '40%';
      progressMessage.style.color = "#e74c3c"; // Red color for error
      break;
    case 'setup_other_agents':
      progressBarFill.style.width = '60%';
      progressMessage.style.color = ""; // Reset color
      break;
    case 'game_preparation':
      progressBarFill.style.width = '80%';
      break;
    case 'game_ready':
      progressBarFill.style.width = '100%';
      // Hide the progress container
      const progressContainer = document.getElementById('progress-container');
      if (progressContainer) {
        progressContainer.classList.add('hidden');
      }
      
      // Show the game board with variant selection if we have a game ID
      if (gameState && gameState.game_id) {
        console.log("Game ready, showing game board with variant selection");
        
        const gameSetupScreen = document.getElementById('game-setup');
        if (gameSetupScreen) {
          console.log("Hiding game setup screen");
          gameSetupScreen.classList.add('hidden');
        }
        
        const gameBoard = document.getElementById('game-board');
        if (gameBoard) {
          console.log("Showing game board");
          // First make sure the element is visible in the DOM
          gameBoard.style.display = "grid";
          
          // Then remove the hidden class
          gameBoard.classList.remove('hidden');
          
          // Force a reflow to ensure the DOM updates
          void gameBoard.offsetWidth;
          
          // Make sure the variant selection is visible
          const gameVariantSelection = document.getElementById('game-variant-selection');
          if (gameVariantSelection) {
            console.log("Showing variant selection");
            gameVariantSelection.classList.remove('hidden');
            gameVariantSelection.style.display = "block";
            
            // Force a reflow to ensure the DOM updates
            void gameVariantSelection.offsetWidth;
            
            console.log("Variant selection display:", gameVariantSelection.style.display);
            console.log("Variant selection classes:", gameVariantSelection.className);
          }
        }
        
        // Emit event that game state has been updated
        eventBus.emit('gameStateUpdated');
      }
      break;
  }
}

/**
 * Handle trick completed event
 * @param {Object} data - Trick completed data
 */
export function handleTrickCompleted(data) {
  console.log('Handling trick completed:', data);
  
  // Check if there were special captures (Diamond Aces or 40+ point tricks)
  if (gameState && gameState.diamondAceCaptured && Array.isArray(gameState.diamondAceCaptured)) {
    // Just clear the diamond_ace_captured flag without showing popups
    delete gameState.diamondAceCaptured;
  }
}

/**
 * Handle AI selecting variant event
 * @param {Object} data - AI selecting variant data
 */
export function handleAiSelectingVariant(data) {
  console.log('Handling AI selecting variant:', data);
  
  // Update the UI to show which AI player is selecting a variant
  const playerIdx = data.player;
  const variant = data.variant;
  
  // Get the player element
  const playerElement = document.querySelector(`.player-${playerIdx}`);
  if (playerElement) {
    // Add a visual indicator that this player is selecting a variant
    playerElement.classList.add('selecting-variant');
    
    // Show a message indicating the variant being selected
    const variantMessage = document.createElement('div');
    variantMessage.className = 'variant-message';
    variantMessage.textContent = `Selecting ${variant}...`;
    playerElement.appendChild(variantMessage);
    
    // Remove the indicator after a short delay
    setTimeout(() => {
      playerElement.classList.remove('selecting-variant');
      if (variantMessage.parentNode) {
        variantMessage.parentNode.removeChild(variantMessage);
      }
    }, 1500);
  }
}

/**
 * Initialize socket event listeners
 */
export function initSocketEvents() {
  // Listen for progress update events
  eventBus.on('progressUpdate', handleProgressUpdate);
  
  // Listen for trick completed events
  eventBus.on('trickCompleted', handleTrickCompleted);
  
  // Listen for AI selecting variant events
  eventBus.on('aiSelectingVariant', handleAiSelectingVariant);
}
