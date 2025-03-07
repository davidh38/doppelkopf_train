/**
 * Core game state and functions
 */
import { eventBus } from './event-bus.js';

// Game state
export const gameState = {
  gameId: null,
  currentPlayer: 0,
  playerTeam: null,
  gameVariant: null,
  hand: [],
  currentTrick: [],
  legalActions: [],
  scores: [0, 0],
  gameOver: false,
  winner: null,
  revealed_teams: [false, false, false, false],
  otherPlayers: [],
  announcements: {},
  canAnnounceRe: false,
  canAnnounceContra: false,
  canAnnounceNo90: false,
  canAnnounceNo60: false,
  canAnnounceNo30: false,
  canAnnounceBlack: false,
  multiplier: 1,
  playerScores: [0, 0, 0, 0],
  playerVariants: {}
};

// Store model path
export let MODEL_PATH = 'the server';

/**
 * Update the game state with new data
 * @param {Object} data - New game state data
 */
export function updateGameState(data) {
  if (!data) return;
  
  // Update game state properties
  gameState.hand = data.hand || gameState.hand;
  gameState.currentTrick = data.current_trick || gameState.currentTrick;
  gameState.currentPlayer = data.current_player !== undefined ? data.current_player : gameState.currentPlayer;
  gameState.playerTeam = data.player_team || gameState.playerTeam;
  gameState.gameVariant = data.game_variant || gameState.gameVariant;
  gameState.scores = data.scores || gameState.scores;
  gameState.gameOver = data.game_over !== undefined ? data.game_over : gameState.gameOver;
  gameState.winner = data.winner || gameState.winner;
  gameState.legalActions = data.legal_actions || gameState.legalActions;
  gameState.otherPlayers = data.other_players || gameState.otherPlayers;
  
  // Explicitly update announcement capabilities with default values of false if not provided
  gameState.canAnnounceRe = data.can_announce_re === true;
  gameState.canAnnounceContra = data.can_announce_contra === true;
  gameState.canAnnounceNo90 = data.can_announce_no90 === true;
  gameState.canAnnounceNo60 = data.can_announce_no60 === true;
  gameState.canAnnounceNo30 = data.can_announce_no30 === true;
  gameState.canAnnounceBlack = data.can_announce_black === true;
  
  gameState.multiplier = data.multiplier || gameState.multiplier;
  gameState.playerScores = data.player_scores || gameState.playerScores;
  gameState.revealed_teams = data.revealed_teams || gameState.revealed_teams;
  
  // Store player announcements if available
  if (data.announcements) {
    gameState.announcements = data.announcements;
  } else if (gameState.announcements === null) {
    // Initialize announcements object if it's null
    gameState.announcements = {};
  }
  
  // Store player variant selections if available
  if (data.player_variants) {
    gameState.playerVariants = data.player_variants;
  }
  
  // Store special tricks information if available
  if (data.diamond_ace_captured) {
    gameState.diamondAceCaptured = data.diamond_ace_captured;
  }
  
  // Store game summary if available
  if (data.game_summary) {
    gameState.gameSummary = data.game_summary;
  }
  
  // Log announcement capabilities for debugging
  console.log("Updated announcement capabilities:", {
    canAnnounceRe: gameState.canAnnounceRe,
    canAnnounceContra: gameState.canAnnounceContra,
    playerTeam: gameState.playerTeam
  });
  
  // Emit event that game state has been updated
  eventBus.emit('gameStateUpdated', gameState);
  
  // If the game is over, emit a gameOver event
  if (data.game_over) {
    eventBus.emit('gameOver', gameState);
  }
}

/**
 * Reset the game state
 */
export function resetGameState() {
  gameState.gameId = null;
  gameState.currentPlayer = 0;
  gameState.playerTeam = null;
  gameState.gameVariant = null;
  gameState.hand = [];
  gameState.currentTrick = [];
  gameState.legalActions = [];
  gameState.scores = [0, 0];
  gameState.gameOver = false;
  gameState.winner = null;
  gameState.revealed_teams = [false, false, false, false];
  gameState.otherPlayers = [];
  
  // Properly reset all announcement-related state
  gameState.announcements = null; // Set to null instead of empty object to ensure proper initialization
  gameState.canAnnounceRe = false;
  gameState.canAnnounceContra = false;
  gameState.canAnnounceNo90 = false;
  gameState.canAnnounceNo60 = false;
  gameState.canAnnounceNo30 = false;
  gameState.canAnnounceBlack = false;
  
  gameState.multiplier = 1;
  gameState.playerScores = [0, 0, 0, 0];
  gameState.playerVariants = {};
  
  // Emit event that game state has been reset
  eventBus.emit('gameStateReset');
}

/**
 * Set the model path
 * @param {string} path - Path to the model
 */
export function setModelPath(path) {
  MODEL_PATH = path || 'the server';
  console.log("Using model:", MODEL_PATH);
}

/**
 * Initialize the game core
 */
export function initGameCore() {
  console.log("Initializing game core...");
  
  // Fetch model info from the server
  fetch('/model_info')
    .then(response => response.json())
    .then(data => {
      setModelPath(data.model_path);
    })
    .catch(error => console.error('Error fetching model info:', error));
}
