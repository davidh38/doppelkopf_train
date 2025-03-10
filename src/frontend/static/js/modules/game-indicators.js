/**
 * Game indicators and simple UI elements
 */
import { gameState } from './game-core.js';
import { turnIndicatorEl } from './game-ui-core.js';

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
