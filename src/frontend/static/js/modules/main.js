/**
 * Main entry point for the Doppelkopf game
 */
import { initGameCore, gameState } from './game-core.js';
import { initUI, showLastTrick, revealAIHands } from './game-ui.js';
import { initCardEvents } from './game-cards.js';
import { initGameFlowEvents, startNewGame } from './game-flow.js';
import { initSocket, initSocketEvents } from './game-socket.js';
import { eventBus } from './event-bus.js';

/**
 * Initialize the game
 */
function initGame() {
  console.log("Initializing Doppelkopf game...");
  
  // Make gameState globally accessible for debugging
  window.gameState = gameState;
  
  // Initialize all modules
  initGameCore();
  initUI();
  initCardEvents();
  initGameFlowEvents();
  initSocket();
  initSocketEvents();
  
  // Set up additional event listeners
  eventBus.on('showLastTrick', showLastTrick);
  eventBus.on('revealAIHands', revealAIHands);
  
  console.log("Game initialization complete");
  
  // Check if there's session data passed from the server
  const sessionGameId = document.getElementById('session-game-id')?.value;
  const sessionPlayerIdx = document.getElementById('session-player-idx')?.value;
  
  if (sessionGameId && sessionPlayerIdx) {
    console.log(`Reconnecting to existing game: ${sessionGameId} as player ${sessionPlayerIdx}`);
    // Set the player index in the game state
    gameState.playerIdx = parseInt(sessionPlayerIdx);
    // Reconnect to the existing game
    reconnectToGame(sessionGameId);
  } else {
    // Check with the server if there's an active session
    checkForActiveSession();
  }
}

/**
 * Check if there's an active session on the server
 */
function checkForActiveSession() {
  fetch('/check_session')
    .then(response => response.json())
    .then(data => {
      if (data.has_session) {
        console.log(`Found active session for game: ${data.game_id} as player ${data.player_idx}`);
        // Set the player index in the game state
        gameState.playerIdx = data.player_idx;
        // Reconnect to the existing game
        reconnectToGame(data.game_id);
      } else {
        // No active session, start a new game
        startNewGame();
      }
    })
    .catch(error => {
      console.error('Error checking for active session:', error);
      // If there's an error, just start a new game
      startNewGame();
    });
}

/**
 * Reconnect to an existing game
 * @param {string} gameId - The ID of the game to reconnect to
 */
function reconnectToGame(gameId) {
  console.log(`Reconnecting to game: ${gameId}`);
  
  // Show progress container
  const progressContainer = document.getElementById('progress-container');
  const progressBarFill = document.getElementById('progress-bar-fill');
  const progressMessage = document.getElementById('progress-message');
  
  if (progressContainer) progressContainer.classList.remove('hidden');
  if (progressBarFill) progressBarFill.style.width = '50%';
  if (progressMessage) progressMessage.textContent = "Reconnecting to game...";
  
  // Set the game ID
  gameState.game_id = gameId;
  
  // Join the Socket.IO room for this game with the correct player index
  eventBus.emit('joinRoom', { game_id: gameId, player_idx: gameState.playerIdx });
  
  // Update the UI to show which player this client is controlling
  const playerIndicator = document.createElement('div');
  playerIndicator.id = 'player-indicator';
  playerIndicator.style.position = 'fixed';
  playerIndicator.style.top = '10px';
  playerIndicator.style.right = '10px';
  playerIndicator.style.backgroundColor = '#3498db';
  playerIndicator.style.color = 'white';
  playerIndicator.style.padding = '5px 10px';
  playerIndicator.style.borderRadius = '4px';
  playerIndicator.style.zIndex = '1000';
  playerIndicator.textContent = `Playing as Player ${gameState.playerIdx}`;
  document.body.appendChild(playerIndicator);
  
  // Get the full game state
  fetch('/get_game_state')
    .then(response => response.json())
    .then(data => {
      console.log("Reconnected to game:", data);
      
      // Update the game state with the response data
      if (data.success && data.state) {
        // Update game state with the full state data
        gameState.hand = data.state.hand || [];
        gameState.currentTrick = data.state.current_trick || [];
        gameState.currentPlayer = data.state.current_player;
        gameState.is_player_turn = data.state.is_player_turn !== undefined ? data.state.is_player_turn : (data.state.current_player === gameState.playerIdx);
        gameState.legalActions = data.state.legal_actions || [];
        gameState.variant_selection_phase = data.state.variant_selection_phase || false;
        gameState.gameVariant = data.state.game_variant || 'NORMAL';
        
        // Hide the progress container
        if (progressContainer) progressContainer.classList.add('hidden');
        
        // Show the game board
        const gameBoard = document.getElementById('game-board');
        if (gameBoard) {
          gameBoard.style.display = 'grid';
          gameBoard.classList.remove('hidden');
        }
        
        // Show or hide the variant selection area based on the game state
        const variantSelectionArea = document.getElementById('game-variant-selection');
        if (variantSelectionArea) {
          if (gameState.variant_selection_phase) {
            variantSelectionArea.style.display = 'block';
          } else {
            variantSelectionArea.style.display = 'none';
          }
        }
        
        // Emit event that game state has been updated
        eventBus.emit('gameStateUpdated', gameState);
      }
    })
    .catch(error => {
      console.error('Error reconnecting to game:', error);
      
      // Show error message
      if (progressMessage) {
        progressMessage.textContent = "Error reconnecting to game. Starting a new game...";
        progressMessage.style.color = "#e74c3c";
      }
      
      // If there's an error, start a new game
      setTimeout(() => {
        startNewGame();
      }, 2000);
    });
}

// Initialize the game when the DOM is loaded
document.addEventListener('DOMContentLoaded', initGame);
