/**
 * Game variant display
 */
import { gameState } from './game-core.js';
import { gameVariantEl } from './game-ui-core.js';

/**
 * Handle AI selecting variant event
 * @param {Object} data - AI selecting variant data
 */
export function handleAiSelectingVariant(data) {
  console.log('Handling AI selecting variant:', data);
  
  // Update the UI to show which AI player is selecting a variant
  const playerIdx = data.player;
  const variant = data.variant;
  
  // Get the player element
  const playerElement = document.querySelector(`.player-box[data-player-id="${playerIdx}"]`);
  if (playerElement) {
    // Add a visual indicator that this player is selecting a variant
    playerElement.classList.add('selecting-variant');
    
    // Show a message indicating the variant being selected
    const variantMessage = document.createElement('div');
    variantMessage.className = 'variant-message';
    variantMessage.textContent = `Selecting ${variant}...`;
    playerElement.appendChild(variantMessage);
    
    // Remove the indicator after a short delay
    setTimeout(() => {
      playerElement.classList.remove('selecting-variant');
      if (variantMessage.parentNode) {
        variantMessage.parentNode.removeChild(variantMessage);
      }
    }, 1500);
  }
}

/**
 * Update the game variant display
 */
export function updateGameVariantDisplay() {
  if (!gameVariantEl) return;
  
  // Create a more detailed variant display
  let variantText = gameState.gameVariant || 'NORMAL';
  gameVariantEl.textContent = variantText;
  
  // Add player variant selections and card giver information in a more visible way
  if (gameState.playerVariants && Object.keys(gameState.playerVariants).length > 0) {
    // Create or get the player variants container
    let variantsContainer = document.getElementById('player-variants-container');
    if (!variantsContainer) {
      variantsContainer = document.createElement('div');
      variantsContainer.id = 'player-variants-container';
      variantsContainer.style.marginTop = '15px';
      variantsContainer.style.padding = '10px';
      variantsContainer.style.backgroundColor = '#f8f9fa';
      variantsContainer.style.borderRadius = '5px';
      variantsContainer.style.border = '1px solid #ddd';
      
      // Add a title
      const title = document.createElement('h4');
      title.textContent = 'Game Information';
      title.style.marginTop = '0';
      title.style.marginBottom = '10px';
      title.style.color = '#3498db';
      variantsContainer.appendChild(title);
      
      // Add the container after the game variant element
      const rightSidebar = document.querySelector('.right-sidebar');
      if (rightSidebar) {
        rightSidebar.appendChild(variantsContainer);
      }
    }
    
    // Clear previous content
    variantsContainer.innerHTML = '';
    
    // Add the title back
    const title = document.createElement('h4');
    title.textContent = 'Game Information';
    title.style.marginTop = '0';
    title.style.marginBottom = '10px';
    title.style.color = '#3498db';
    variantsContainer.appendChild(title);
    
    // Add card giver information
    if (gameState.cardGiver !== undefined) {
      const cardGiverInfo = document.createElement('div');
      cardGiverInfo.style.marginBottom = '10px';
      cardGiverInfo.style.padding = '5px';
      cardGiverInfo.style.backgroundColor = '#e8f4f8';
      cardGiverInfo.style.borderRadius = '3px';
      
      const cardGiverName = gameState.cardGiver === 0 ? 'You' : `Player ${gameState.cardGiver}`;
      cardGiverInfo.innerHTML = `<strong>Card Giver:</strong> ${cardGiverName}`;
      
      variantsContainer.appendChild(cardGiverInfo);
    }
    
    // Add variant selections subtitle
    const variantsSubtitle = document.createElement('h5');
    variantsSubtitle.textContent = 'Player Variant Selections';
    variantsSubtitle.style.marginTop = '10px';
    variantsSubtitle.style.marginBottom = '5px';
    variantsSubtitle.style.color = '#3498db';
    variantsContainer.appendChild(variantsSubtitle);
    
    // Create a list of player variants
    const variantsList = document.createElement('ul');
    variantsList.style.listStyleType = 'none';
    variantsList.style.padding = '0';
    variantsList.style.margin = '0';
    
    for (let i = 0; i < 4; i++) {
      const playerVariant = gameState.playerVariants[i];
      if (playerVariant) {
        const listItem = document.createElement('li');
        listItem.style.padding = '5px 0';
        listItem.style.borderBottom = i < 3 ? '1px solid #eee' : 'none';
        
        // Format the variant name to be more readable
        const formattedVariant = playerVariant.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        // Add card giver indicator in brackets
        const isCardGiver = i === gameState.cardGiver;
        const cardGiverText = isCardGiver ? ' (Card Giver)' : '';
        
        listItem.textContent = i === 0 ? 
          `You${cardGiverText}: ${formattedVariant}` : 
          `Player ${i}${cardGiverText}: ${formattedVariant}`;
        
        // Add additional styling for card giver
        if (isCardGiver) {
            listItem.style.backgroundColor = '#f0f8ff'; // Light blue background
            listItem.style.padding = '5px';
            listItem.style.borderRadius = '3px';
        }
        
        // Highlight the player's own selection
        if (i === 0) {
          listItem.style.fontWeight = 'bold';
          listItem.style.color = '#2ecc71';
        }
        
        // Highlight the card giver
        if (i === gameState.cardGiver) {
          listItem.style.textDecoration = 'underline';
          listItem.style.fontStyle = 'italic';
        }
        
        variantsList.appendChild(listItem);
      }
    }
    
    variantsContainer.appendChild(variantsList);
  }
}
