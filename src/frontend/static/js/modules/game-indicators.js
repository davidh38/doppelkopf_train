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
  
  // Debug output to help diagnose issues
  console.log("Updating turn indicator with state:", {
    currentPlayer: gameState.currentPlayer,
    isPlayerTurn: gameState.is_player_turn,
    cardGiver: gameState.cardGiver,
    playerIsCardGiver: gameState.cardGiver === 0
  });
  
  // Special case: If player is the card giver, they don't play first
  // The player to the left of the card giver (player 1) plays first
  if (gameState.cardGiver === 0 && gameState.currentPlayer === 1) {
    turnIndicatorEl.textContent = `Waiting for Player 1 (First Player)...`;
    return;
  }
  
  // Strictly use the is_player_turn flag from the server to determine whose turn it is
  if (gameState.is_player_turn === true) {
    turnIndicatorEl.textContent = "Your turn";
  } else {
    // When it's not the player's turn, show who's turn it is
    // Special case: if currentPlayer is 0 but is_player_turn is false, 
    // there's a state inconsistency - show a more appropriate message
    if (gameState.currentPlayer === 0) {
      turnIndicatorEl.textContent = "Processing game state...";
    } else {
      // Show which AI player's turn it is
      // If this player is the card giver, indicate that
      if (gameState.cardGiver === gameState.currentPlayer) {
        turnIndicatorEl.textContent = `Waiting for Player ${gameState.currentPlayer} (Card Giver)...`;
      } else {
        turnIndicatorEl.textContent = `Waiting for Player ${gameState.currentPlayer}...`;
      }
    }
  }
}
