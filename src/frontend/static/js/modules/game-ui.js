/**
 * UI-related functions - Main entry point
 * 
 * This file now serves as a facade that re-exports functions from the modular UI components.
 * It maintains backward compatibility with existing code that imports from this file.
 */

// Re-export everything from the modular components
export { initUI, renderUI } from './game-ui-core.js';
export { renderHand } from './game-player-hand.js';
export { renderCurrentTrick, showLastTrick } from './game-trick-display.js';
export { updateTurnIndicator } from './game-indicators.js';
export { updateGameVariantDisplay, handleAiSelectingVariant } from './game-variant-display.js';
export { updateAICardVisualization, revealAIHands } from './game-ai-visualization.js';
export { updateAnnouncementButtons } from './game-announcements.js';
export { updateGameScores } from './game-scoreboard.js';
export { showGameOverScreen } from './game-end-screen.js';

// Also export DOM elements for backward compatibility
import {
  gameSetupScreen,
  gameBoard,
  gameOverScreen,
  playerHandEl,
  currentTrickEl,
  turnIndicatorEl,
  playerTeamEl,
  gameVariantEl,
  reScoreEl,
  kontraScoreEl
} from './game-ui-core.js';

export {
  gameSetupScreen,
  gameBoard,
  gameOverScreen,
  playerHandEl,
  currentTrickEl,
  turnIndicatorEl,
  playerTeamEl,
  gameVariantEl,
  reScoreEl,
  kontraScoreEl
};
