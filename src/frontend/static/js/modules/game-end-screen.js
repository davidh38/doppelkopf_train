/**
 * Game over screen
 */
import { gameState } from './game-core.js';
import { gameBoard, gameOverScreen } from './game-ui-core.js';

/**
 * Show the game over screen
 */
export function showGameOverScreen() {
  console.log("Showing game over screen");
  
  // Redirect to the game summary page
  if (gameState.gameId) {
    window.location.href = `/game-summary/${gameState.gameId}`;
  } else {
    console.error("Game ID not found, cannot redirect to game summary");
    
    // Fallback to the old behavior if game ID is not available
    // Hide the game board
    if (gameBoard) {
      gameBoard.classList.add('hidden');
    }
    
    // Show the game over screen
    if (gameOverScreen) {
      gameOverScreen.classList.remove('hidden');
      
      // Get the winner display element
      const gameResultEl = document.getElementById('game-result');
      if (gameResultEl) {
        // Clear any previous content
        gameResultEl.innerHTML = '';
        
        const winnerTeam = gameState.winner === 1 ? 'RE' : 'KONTRA';
        const winnerHeader = document.createElement('h3');
        winnerHeader.id = 'winner';
        winnerHeader.textContent = `Team ${winnerTeam} wins!`;
        winnerHeader.style.color = winnerTeam === 'RE' ? '#2ecc71' : '#e74c3c';
        gameResultEl.appendChild(winnerHeader);
        
        // Add game summary if available
        if (gameState.gameSummary) {
          console.log("Adding game summary to game over screen");
          const summaryEl = document.createElement('pre');
          summaryEl.textContent = gameState.gameSummary;
          summaryEl.style.textAlign = 'left';
          summaryEl.style.margin = '20px auto';
          summaryEl.style.padding = '15px';
          summaryEl.style.backgroundColor = '#f8f9fa';
          summaryEl.style.border = '1px solid #ddd';
          summaryEl.style.borderRadius = '5px';
          summaryEl.style.maxWidth = '600px';
          summaryEl.style.whiteSpace = 'pre-wrap';
          summaryEl.style.fontSize = '14px';
          summaryEl.style.fontFamily = 'monospace';
          gameResultEl.appendChild(summaryEl);
        } else {
          console.log("No game summary available");
        }
      }
      
      // Update the final score elements
      const finalReScoreEl = document.getElementById('final-re-score');
      const finalKontraScoreEl = document.getElementById('final-kontra-score');
      
      if (finalReScoreEl) {
        finalReScoreEl.textContent = gameState.scores[0];
      }
      
      if (finalKontraScoreEl) {
        finalKontraScoreEl.textContent = gameState.scores[1];
      }
      
      // Update the announcement status elements
      const finalReStatus = document.getElementById('final-re-status');
      const finalContraStatus = document.getElementById('final-contra-status');
      const finalNo90Status = document.getElementById('final-no90-status');
      const finalNo60Status = document.getElementById('final-no60-status');
      const finalNo30Status = document.getElementById('final-no30-status');
      const finalBlackStatus = document.getElementById('final-black-status');
      
      if (finalReStatus) {
        finalReStatus.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.re));
      }
      
      if (finalContraStatus) {
        finalContraStatus.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.contra));
      }
      
      if (finalNo90Status) {
        finalNo90Status.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.no90));
      }
      
      if (finalNo60Status) {
        finalNo60Status.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.no60));
      }
      
      if (finalNo30Status) {
        finalNo30Status.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.no30));
      }
      
      if (finalBlackStatus) {
        finalBlackStatus.classList.toggle('hidden', !(gameState.announcements && gameState.announcements.black));
      }
    }
  }
}
