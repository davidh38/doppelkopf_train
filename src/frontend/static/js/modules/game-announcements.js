/**
 * Announcement UI
 */
import { gameState } from './game-core.js';
import { eventBus } from './event-bus.js';

/**
 * Update the announcement buttons visibility
 */
export function updateAnnouncementButtons() {
  // Get the announcement buttons
  const gameReBtn = document.getElementById('game-re-btn');
  const gameContraBtn = document.getElementById('game-contra-btn');
  
  // Get the announcement areas
  const gameAnnouncementArea = document.getElementById('game-announcement-area');
  
  // Log current announcement state for debugging
  console.log("Updating announcement buttons with state:", {
    playerTeam: gameState.playerTeam,
    canAnnounceRe: gameState.canAnnounceRe,
    canAnnounceContra: gameState.canAnnounceContra,
    hasHochzeit: gameState.hasHochzeit,
    announcements: gameState.announcements
  });
  
  // Get the announcement buttons container
  const announcementButtons = document.querySelector('.announcement-buttons');
  
  // Determine which announcement button to show based on the game state
  // For RE team
  if (gameState.playerTeam === 'RE') {
    
    // Show Re button for RE team
    if (gameReBtn) {
      gameReBtn.style.display = 'inline-block';
      
      // Check if announcements object exists and is properly initialized
      const hasAnnounced = gameState.announcements && gameState.announcements.re === true;
      
      if (!hasAnnounced) {
        gameReBtn.textContent = 'Re';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 're');
        gameReBtn.disabled = !gameState.canAnnounceRe;
        gameReBtn.style.opacity = gameState.canAnnounceRe ? '1' : '0.5';
      } else if (gameState.canAnnounceNo90) {
        gameReBtn.textContent = 'No 90';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no90');
        gameReBtn.disabled = !gameState.canAnnounceNo90;
        gameReBtn.style.opacity = gameState.canAnnounceNo90 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo60) {
        gameReBtn.textContent = 'No 60';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no60');
        gameReBtn.disabled = !gameState.canAnnounceNo60;
        gameReBtn.style.opacity = gameState.canAnnounceNo60 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo30) {
        gameReBtn.textContent = 'No 30';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no30');
        gameReBtn.disabled = !gameState.canAnnounceNo30;
        gameReBtn.style.opacity = gameState.canAnnounceNo30 ? '1' : '0.5';
      } else if (gameState.canAnnounceBlack) {
        gameReBtn.textContent = 'Black';
        gameReBtn.onclick = () => eventBus.emit('makeAnnouncement', 'black');
        gameReBtn.disabled = !gameState.canAnnounceBlack;
        gameReBtn.style.opacity = gameState.canAnnounceBlack ? '1' : '0.5';
      } else {
        gameReBtn.textContent = 'Re';
        gameReBtn.disabled = true;
        gameReBtn.style.opacity = '0.5';
      }
    }
    
    // Hide Contra button for RE team
    if (gameContraBtn) {
      gameContraBtn.style.display = 'none';
    }
  }
  // For KONTRA team
  else if (gameState.playerTeam === 'KONTRA') {
    
    // Show Contra button for KONTRA team
    if (gameContraBtn) {
      gameContraBtn.style.display = 'inline-block';
      
      // Check if announcements object exists and is properly initialized
      const hasAnnounced = gameState.announcements && gameState.announcements.contra === true;
      
      if (!hasAnnounced) {
        gameContraBtn.textContent = 'Contra';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'contra');
        gameContraBtn.disabled = !gameState.canAnnounceContra;
        gameContraBtn.style.opacity = gameState.canAnnounceContra ? '1' : '0.5';
      } else if (gameState.canAnnounceNo90) {
        gameContraBtn.textContent = 'No 90';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no90');
        gameContraBtn.disabled = !gameState.canAnnounceNo90;
        gameContraBtn.style.opacity = gameState.canAnnounceNo90 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo60) {
        gameContraBtn.textContent = 'No 60';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no60');
        gameContraBtn.disabled = !gameState.canAnnounceNo60;
        gameContraBtn.style.opacity = gameState.canAnnounceNo60 ? '1' : '0.5';
      } else if (gameState.canAnnounceNo30) {
        gameContraBtn.textContent = 'No 30';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'no30');
        gameContraBtn.disabled = !gameState.canAnnounceNo30;
        gameContraBtn.style.opacity = gameState.canAnnounceNo30 ? '1' : '0.5';
      } else if (gameState.canAnnounceBlack) {
        gameContraBtn.textContent = 'Black';
        gameContraBtn.onclick = () => eventBus.emit('makeAnnouncement', 'black');
        gameContraBtn.disabled = !gameState.canAnnounceBlack;
        gameContraBtn.style.opacity = gameState.canAnnounceBlack ? '1' : '0.5';
      } else {
        gameContraBtn.textContent = 'Contra';
        gameContraBtn.disabled = true;
        gameContraBtn.style.opacity = '0.5';
      }
    }
    
    // Hide Re button for KONTRA team
    if (gameReBtn) {
      gameReBtn.style.display = 'none';
    }
  } else {
    // If player team is not yet determined, hide both buttons
    if (gameReBtn) gameReBtn.style.display = 'none';
    if (gameContraBtn) gameContraBtn.style.display = 'none';
  }
  
  // Show/hide the announcement areas based on whether announcements are allowed
  if (gameAnnouncementArea) {
    // Only show the announcement area if the player can make an announcement
    const canAnnounceRe = gameState.playerTeam === 'RE' && gameState.canAnnounceRe;
    const canAnnounceContra = gameState.playerTeam === 'KONTRA' && gameState.canAnnounceContra;
    const canAnnounceNo90 = gameState.canAnnounceNo90;
    const canAnnounceNo60 = gameState.canAnnounceNo60;
    const canAnnounceNo30 = gameState.canAnnounceNo30;
    const canAnnounceBlack = gameState.canAnnounceBlack;
    
    const canAnnounce = canAnnounceRe || canAnnounceContra || canAnnounceNo90 || 
                        canAnnounceNo60 || canAnnounceNo30 || canAnnounceBlack;
    
    console.log("Can announce anything:", canAnnounce, 
                "Re:", canAnnounceRe, 
                "Contra:", canAnnounceContra);
    
    gameAnnouncementArea.classList.toggle('hidden', !canAnnounce);
  }
  
  // Helper function to update announcement status visibility
  function updateAnnouncementStatus(elementId, isVisible) {
    const element = document.getElementById(elementId);
    if (element) {
      element.classList.toggle('hidden', !isVisible);
    }
  }
  
  // Update announcement status displays for all announcement types
  const announcementStatuses = [
    { id: 're-status', type: 're' },
    { id: 'contra-status', type: 'contra' },
    { id: 'game-re-status', type: 're' },
    { id: 'game-contra-status', type: 'contra' },
    { id: 'no90-status', type: 'no90' },
    { id: 'no60-status', type: 'no60' },
    { id: 'no30-status', type: 'no30' },
    { id: 'black-status', type: 'black' },
    { id: 'game-no90-status', type: 'no90' },
    { id: 'game-no60-status', type: 'no60' },
    { id: 'game-no30-status', type: 'no30' },
    { id: 'game-black-status', type: 'black' }
  ];
  
  // Update visibility for each announcement status element
  announcementStatuses.forEach(status => {
    const isVisible = gameState.announcements && gameState.announcements[status.type];
    updateAnnouncementStatus(status.id, isVisible);
  });
}
