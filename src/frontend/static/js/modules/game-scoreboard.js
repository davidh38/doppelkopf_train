/**
 * Game scoreboard
 */
import { gameState } from './game-core.js';
import { reScoreEl, kontraScoreEl } from './game-ui-core.js';

/**
 * Update the game scores
 */
export function updateGameScores() {
  if (!reScoreEl || !kontraScoreEl) return;
  
  // Update the score displays
  reScoreEl.textContent = gameState.scores[0];
  kontraScoreEl.textContent = gameState.scores[1];
  
  // Fetch the scoreboard data from the server
  fetch('/get_scoreboard')
    .then(response => response.json())
    .then(scoreboard => {
      console.log('Fetched scoreboard:', scoreboard);
      
      // Update individual player scores in the sidebar
      const playerScoreEl = document.getElementById('player-score');
      const player1ScoreEl = document.getElementById('player-1-score-sidebar');
      const player2ScoreEl = document.getElementById('player-2-score-sidebar');
      const player3ScoreEl = document.getElementById('player-3-score-sidebar');
      
      // Update the player scores from the scoreboard
      if (scoreboard && scoreboard.player_scores && scoreboard.player_scores.length === 4) {
        if (playerScoreEl) playerScoreEl.textContent = scoreboard.player_scores[0];
        if (player1ScoreEl) player1ScoreEl.textContent = scoreboard.player_scores[1];
        if (player2ScoreEl) player2ScoreEl.textContent = scoreboard.player_scores[2];
        if (player3ScoreEl) player3ScoreEl.textContent = scoreboard.player_scores[3];
      }
    })
    .catch(error => {
      console.error('Error fetching scoreboard:', error);
      
      // Fallback to using the scores from the game state
      const playerScoreEl = document.getElementById('player-score');
      const player1ScoreEl = document.getElementById('player-1-score-sidebar');
      const player2ScoreEl = document.getElementById('player-2-score-sidebar');
      const player3ScoreEl = document.getElementById('player-3-score-sidebar');
      
      if (gameState.playerScores && gameState.playerScores.length === 4) {
        if (playerScoreEl) playerScoreEl.textContent = gameState.playerScores[0];
        if (player1ScoreEl) player1ScoreEl.textContent = gameState.playerScores[1];
        if (player2ScoreEl) player2ScoreEl.textContent = gameState.playerScores[2];
        if (player3ScoreEl) player3ScoreEl.textContent = gameState.playerScores[3];
      }
    });
}
