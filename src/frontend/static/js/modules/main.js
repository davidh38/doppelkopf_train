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
  
  // Get the current game state
  fetch(`/get_current_trick?game_id=${gameId}`)
    .then(response => response.json())
    .then(data => {
      console.log("Reconnected to game:", data);
      
      // Update the game state with the response data
      if (data) {
        // Update game state with the current trick data
        gameState.currentTrick = data.current_trick || [];
        gameState.currentPlayer = data.current_player;
        
        // Hide the progress container
        if (progressContainer) progressContainer.classList.add('hidden');
        
        // Show the game board
        const gameBoard = document.getElementById('game-board');
        if (gameBoard) {
          gameBoard.style.display = 'grid';
          gameBoard.classList.remove('hidden');
        }
        
        // The variant selection area will be shown or hidden based on the game state
        // when we receive the game_update event from the server
        
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
