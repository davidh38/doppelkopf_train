/**
 * Socket.IO event handling
 */
import { eventBus } from './event-bus.js';
import { updateGameState } from './game-core.js';
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
    
    // Update game state with the response data
    updateGameState(data);
    
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
      const gameState = window.gameState; // Access the global game state
      if (gameState && gameState.gameId) {
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
  if (window.gameState && window.gameState.diamondAceCaptured && Array.isArray(window.gameState.diamondAceCaptured)) {
    // Group captures by type
    const diamondAceCaptures = window.gameState.diamondAceCaptured.filter(capture => capture.type === 'diamond_ace' || !capture.type);
    const fortyPlusCaptures = window.gameState.diamondAceCaptured.filter(capture => capture.type === 'forty_plus');
    
    // Process Diamond Ace captures
    if (diamondAceCaptures.length > 0) {
      // Create a notification for Diamond Ace captures
      const notification = document.createElement('div');
      notification.className = 'special-notification diamond-ace-notification';
      notification.style.position = 'fixed';
      notification.style.top = '50%';
      notification.style.left = '50%';
      notification.style.transform = 'translate(-50%, -50%)';
      notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
      notification.style.color = 'white';
      notification.style.padding = '20px';
      notification.style.borderRadius = '10px';
      notification.style.zIndex = '1000';
      notification.style.textAlign = 'center';
      notification.style.boxShadow = '0 0 20px rgba(255, 215, 0, 0.7)';
      notification.style.border = '2px solid gold';
      
      // Get the first capture for basic information
      const firstCapture = diamondAceCaptures[0];
      const winnerTeam = firstCapture.winner_team;
      const loserTeam = firstCapture.loser_team;
      
      // Create capture details for each Diamond Ace
      let captureDetails = '';
      diamondAceCaptures.forEach(capture => {
        const winnerName = capture.winner === 0 ? 'You' : `Player ${capture.winner}`;
        const loserName = capture.loser === 0 ? 'You' : `Player ${capture.loser}`;
        captureDetails += `<p>${winnerName} (${capture.winner_team}) captured a Diamond Ace from ${loserName} (${capture.loser_team})!</p>`;
      });
      
      // Set the notification text
      notification.innerHTML = `
        <h3 style="color: gold; margin-top: 0;">${diamondAceCaptures.length > 1 ? 'Diamond Aces Captured!' : 'Diamond Ace Captured!'}</h3>
        ${captureDetails}
        <p>+${diamondAceCaptures.length} ${diamondAceCaptures.length > 1 ? 'points' : 'point'} for team ${winnerTeam}, -${diamondAceCaptures.length} ${diamondAceCaptures.length > 1 ? 'points' : 'point'} for team ${loserTeam}</p>
        <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
          ${Array(diamondAceCaptures.length).fill('<img src="/static/images/cards/AD.png" style="width: 60px; height: auto; filter: drop-shadow(0 0 10px gold);">').join('')}
        </div>
      `;
      
      // Add the notification to the document
      document.body.appendChild(notification);
      
      // Remove the notification after 3 seconds
      setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s ease-out';
        
        // Remove from DOM after fade out
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 500);
      }, 3000);
    }
    
    // Process 40+ point tricks
    if (fortyPlusCaptures.length > 0) {
      // Wait a bit if we also showed a Diamond Ace notification
      const delay = diamondAceCaptures.length > 0 ? 3500 : 0;
      
      setTimeout(() => {
        // Create a notification for 40+ point tricks
        const notification = document.createElement('div');
        notification.className = 'special-notification forty-plus-notification';
        notification.style.position = 'fixed';
        notification.style.top = '50%';
        notification.style.left = '50%';
        notification.style.transform = 'translate(-50%, -50%)';
        notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        notification.style.color = 'white';
        notification.style.padding = '20px';
        notification.style.borderRadius = '10px';
        notification.style.zIndex = '1000';
        notification.style.textAlign = 'center';
        notification.style.boxShadow = '0 0 20px rgba(65, 105, 225, 0.7)'; // Royal blue shadow
        notification.style.border = '2px solid royalblue';
        
        // Get the first capture for basic information
        const capture = fortyPlusCaptures[0];
        const winnerName = capture.winner === 0 ? 'You' : `Player ${capture.winner}`;
        const winnerTeam = capture.winner_team;
        
        // Set the notification text
        notification.innerHTML = `
          <h3 style="color: royalblue; margin-top: 0;">40+ Point Trick!</h3>
          <p>${winnerName} (${winnerTeam}) won a trick worth ${capture.points} points!</p>
          <p>+1 bonus point for team ${winnerTeam}</p>
          <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
            <div style="background-color: royalblue; color: white; font-size: 24px; width: 60px; height: 60px; display: flex; justify-content: center; align-items: center; border-radius: 50%; filter: drop-shadow(0 0 10px royalblue);">
              ${capture.points}
            </div>
          </div>
        `;
        
        // Add the notification to the document
        document.body.appendChild(notification);
        
        // Remove the notification after 3 seconds
        setTimeout(() => {
          notification.style.opacity = '0';
          notification.style.transition = 'opacity 0.5s ease-out';
          
          // Remove from DOM after fade out
          setTimeout(() => {
            if (notification.parentNode) {
              notification.parentNode.removeChild(notification);
            }
          }, 500);
        }, 3000);
      }, delay);
    }
    
    // Clear the diamond_ace_captured flag
    delete window.gameState.diamondAceCaptured;
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
}
