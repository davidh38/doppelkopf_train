/**
 * Main entry point for the Doppelkopf game
 */
import { initGameCore, gameState } from './game-core.js';
import { initUI, showLastTrick, revealAIHands } from './game-ui.js';
import { initCardEvents } from './game-cards.js';
import { initGameFlowEvents } from './game-flow.js';
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
}

// Initialize the game when the DOM is loaded
document.addEventListener('DOMContentLoaded', initGame);
