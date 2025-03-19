/**
 * Core UI initialization and coordination
 */
import { gameState } from './game-core.js';
import { eventBus } from './event-bus.js';
import { renderHand } from './game-player-hand.js';
import { renderCurrentTrick } from './game-trick-display.js';
import { updateTurnIndicator } from './game-indicators.js';
import { updateGameVariantDisplay, handleAiSelectingVariant } from './game-variant-display.js';
import { updateAICardVisualization } from './game-ai-visualization.js';
import { updateAnnouncementButtons } from './game-announcements.js';
import { updateGameScores } from './game-scoreboard.js';
import { showGameOverScreen } from './game-end-screen.js';
import { updatePlayerTeamIndicator } from './game-team-indicators.js';

// DOM elements
export let gameSetupScreen;
export let gameBoard;
export let gameOverScreen;
export let playerHandEl;
export let currentTrickEl;
export let gameIdEl;
export let turnIndicatorEl;
export let playerTeamEl;
export let gameVariantEl;
export let reScoreEl;
export let kontraScoreEl;

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
  gameIdEl = document.getElementById('game-id');
  turnIndicatorEl = document.getElementById('turn-indicator');
  playerTeamEl = document.getElementById('player-team');
  gameVariantEl = document.getElementById('game-variant');
  reScoreEl = document.getElementById('re-score');
  kontraScoreEl = document.getElementById('kontra-score');
  
  // Set up event listeners
  eventBus.on('gameStateUpdated', renderUI);
  eventBus.on('gameOver', showGameOverScreen);
  eventBus.on('aiSelectingVariant', handleAiSelectingVariant);
}

/**
 * Update the game ID display
 */
function updateGameId() {
  if (gameState.game_id) {
    gameIdEl.textContent = gameState.game_id;
  }
}

/**
 * Render the UI based on the current game state
 */
export function renderUI() {
  updateGameId();
  renderHand();
  renderCurrentTrick();
  updateTurnIndicator();
  updatePlayerTeamIndicator();
  updateGameVariantDisplay();
  updateAICardVisualization();
  updateAnnouncementButtons();
  updateGameScores();
}
