/**
 * Game team indicators
 */
import { gameState } from './game-core.js';
import { playerTeamEl } from './game-ui-core.js';

/**
 * Update the player team indicator
 */
export function updatePlayerTeamIndicator() {
  if (!playerTeamEl) return;
  
  // Update the player team element with the current team
  playerTeamEl.textContent = gameState.playerTeam || 'UNKNOWN';
  
  // Add a tooltip to explain that team RE is determined by having a Queen of Clubs
  const teamInfoContainer = playerTeamEl.parentElement;
  
  // Check if we already added the tooltip
  let tooltipEl = teamInfoContainer.querySelector('.team-tooltip');
  
  if (!tooltipEl) {
    // Create a tooltip element
    tooltipEl = document.createElement('span');
    tooltipEl.className = 'team-tooltip';
    tooltipEl.style.display = 'block';
    tooltipEl.style.fontSize = '0.8em';
    tooltipEl.style.color = '#666';
    tooltipEl.style.marginTop = '5px';
    tooltipEl.style.fontStyle = 'italic';
    tooltipEl.textContent = 'Team RE members have a Queen of Clubs';
    
    // Add the tooltip after the team indicator
    teamInfoContainer.appendChild(tooltipEl);
  }
}
