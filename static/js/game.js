document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    const socket = io();
    
    // Store model path
    let MODEL_PATH = 'the server';
    
    // Game state
    let gameState = {
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
        revealed_team: false,
        revealed_teams: [false, false, false, false],
        player_team_type: '',
        player_team_types: ['', '', '', '']
    };
    
    // DOM elements
    const gameSetupScreen = document.getElementById('game-setup');
    const gameBoard = document.getElementById('game-board');
    const gameOverScreen = document.getElementById('game-over');
    
    console.log("DOM elements initialized:");
    console.log("gameSetupScreen:", gameSetupScreen);
    console.log("gameBoard:", gameBoard);
    console.log("gameOverScreen:", gameOverScreen);
    
    const newGameBtn = document.getElementById('new-game-btn');
    const normalBtn = document.getElementById('normal-btn');
    const hochzeitBtn = document.getElementById('hochzeit-btn');
    const queenSoloBtn = document.getElementById('queen-solo-btn');
    const jackSoloBtn = document.getElementById('jack-solo-btn');
    const fleshlessBtn = document.getElementById('fleshless-btn');
    const playAgainBtn = document.getElementById('play-again-btn');
    
    const playerTeamEl = document.getElementById('player-team');
    const gameVariantEl = document.getElementById('game-variant');
    const reScoreEl = document.getElementById('re-score');
    const kontraScoreEl = document.getElementById('kontra-score');
    const turnIndicatorEl = document.getElementById('turn-indicator');
    
    const otherPlayersEl = document.getElementById('other-players');
    const playerHandEl = document.getElementById('player-hand');
    const currentTrickEl = document.getElementById('current-trick');
    
    // Event listeners
    if (newGameBtn) newGameBtn.addEventListener('click', startNewGame);
    
    // Add event listeners for variant selection buttons
    if (normalBtn) normalBtn.addEventListener('click', () => setGameVariant('normal'));
    if (hochzeitBtn) hochzeitBtn.addEventListener('click', () => setGameVariant('hochzeit'));
    if (queenSoloBtn) queenSoloBtn.addEventListener('click', () => setGameVariant('queen_solo'));
    if (jackSoloBtn) jackSoloBtn.addEventListener('click', () => setGameVariant('jack_solo'));
    if (fleshlessBtn) fleshlessBtn.addEventListener('click', () => setGameVariant('fleshless'));
    
    // Add event listeners for Re and Contra announcement buttons
    const reBtn = document.getElementById('re-btn');
    const contraBtn = document.getElementById('contra-btn');
    const gameReBtn = document.getElementById('game-re-btn');
    const gameContraBtn = document.getElementById('game-contra-btn');
    
    if (reBtn) reBtn.addEventListener('click', () => makeAnnouncement('re'));
    if (contraBtn) contraBtn.addEventListener('click', () => makeAnnouncement('contra'));
    if (gameReBtn) gameReBtn.addEventListener('click', () => makeAnnouncement('re'));
    if (gameContraBtn) gameContraBtn.addEventListener('click', () => makeAnnouncement('contra'));
    
    // Add event listeners for additional announcement buttons
    const no90Btn = document.getElementById('no90-btn');
    const no60Btn = document.getElementById('no60-btn');
    const no30Btn = document.getElementById('no30-btn');
    const blackBtn = document.getElementById('black-btn');
    const gameNo90Btn = document.getElementById('game-no90-btn');
    const gameNo60Btn = document.getElementById('game-no60-btn');
    const gameNo30Btn = document.getElementById('game-no30-btn');
    const gameBlackBtn = document.getElementById('game-black-btn');
    
    if (no90Btn) no90Btn.addEventListener('click', () => makeAnnouncement('no90'));
    if (no60Btn) no60Btn.addEventListener('click', () => makeAnnouncement('no60'));
    if (no30Btn) no30Btn.addEventListener('click', () => makeAnnouncement('no30'));
    if (blackBtn) blackBtn.addEventListener('click', () => makeAnnouncement('black'));
    if (gameNo90Btn) gameNo90Btn.addEventListener('click', () => makeAnnouncement('no90'));
    if (gameNo60Btn) gameNo60Btn.addEventListener('click', () => makeAnnouncement('no60'));
    if (gameNo30Btn) gameNo30Btn.addEventListener('click', () => makeAnnouncement('no30'));
    if (gameBlackBtn) gameBlackBtn.addEventListener('click', () => makeAnnouncement('black'));
    
    // Add event listener for the Show Last Trick button
    const showLastTrickBtn = document.getElementById('show-last-trick-btn');
    if (showLastTrickBtn) {
        showLastTrickBtn.addEventListener('click', showLastTrick);
    }
    
    // Add event listener for the Reveal AI Hands button
    const revealAIHandsBtn = document.getElementById('reveal-ai-hands-btn');
    if (revealAIHandsBtn) {
        revealAIHandsBtn.addEventListener('click', revealAIHands);
    }
    
    // Socket.IO event handlers
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('game_update', function(data) {
        console.log('Received game update:', data);
        
        // Update game state with the response data
        if (data) {
            gameState.hand = data.hand || [];
            gameState.currentTrick = data.current_trick || [];
            gameState.currentPlayer = data.current_player;
            gameState.playerTeam = data.player_team;
            gameState.gameVariant = data.game_variant;
            gameState.scores = data.scores || [0, 0];
            gameState.gameOver = data.game_over;
            gameState.winner = data.winner;
            gameState.legalActions = data.legal_actions || [];
            gameState.otherPlayers = data.other_players || [];
            gameState.canAnnounceRe = data.can_announce_re || false;
            gameState.canAnnounceContra = data.can_announce_contra || false;
            gameState.canAnnounceNo90 = data.can_announce_no90 || false;
            gameState.canAnnounceNo60 = data.can_announce_no60 || false;
            gameState.canAnnounceNo30 = data.can_announce_no30 || false;
            gameState.canAnnounceBlack = data.can_announce_black || false;
            gameState.multiplier = data.multiplier || 1;
            
            // Store player announcements if available
            if (data.announcements) {
                gameState.announcements = data.announcements;
            }
            
            // Store player variant selections if available
            if (data.player_variants) {
                gameState.playerVariants = data.player_variants;
            }
            
            // Update announcement buttons visibility
            updateAnnouncementButtons();
        }
        
        // Render the player's hand and current trick
        renderHand();
        renderCurrentTrick();
        
        // Update turn indicator
        updateTurnIndicator();
        
        // Update game variant display
        updateGameVariantDisplay();
        
        // Update AI card visualization
        updateAICardVisualization();
    });
    
    // Function to update AI card visualization
    function updateAICardVisualization() {
        // Get the AI card visualization containers
        const player1Cards = document.getElementById('player1-cards');
        const player2Cards = document.getElementById('player2-cards');
        const player3Cards = document.getElementById('player3-cards');
        
        if (!player1Cards || !player2Cards || !player3Cards) return;
        
        // Clear previous content
        player1Cards.innerHTML = '';
        player2Cards.innerHTML = '';
        player3Cards.innerHTML = '';
        
        // Create mock cards for AI players
        for (let i = 1; i <= 3; i++) {
            const playerCardsEl = document.getElementById(`player${i}-cards`);
            if (!playerCardsEl) continue;
            
            // Get the number of cards for this AI player
            const cardCount = gameState.otherPlayers && gameState.otherPlayers[i-1] ? 
                              gameState.otherPlayers[i-1].card_count : 10;
            
            // Create card back images
            for (let j = 0; j < cardCount; j++) {
                const cardImg = document.createElement('img');
                cardImg.src = '/static/images/cards/back.png';
                cardImg.alt = 'Card back';
                cardImg.className = 'ai-card';
                cardImg.style.width = '30px';
                cardImg.style.height = 'auto';
                cardImg.style.margin = '2px';
                playerCardsEl.appendChild(cardImg);
            }
            
            // Show team information only if the player has revealed their team (by playing a Queen of Clubs)
            if (gameState.otherPlayers && 
                gameState.otherPlayers[i-1] && 
                gameState.otherPlayers[i-1].team && 
                gameState.otherPlayers[i-1].revealed_team) {
                const team = gameState.otherPlayers[i-1].team;
                
                const teamInfo = document.createElement('div');
                teamInfo.textContent = `Team: ${team}`;
                teamInfo.style.marginTop = '5px';
                teamInfo.style.fontWeight = 'bold';
                
                // Add color coding for teams
                if (team === 'RE') {
                    teamInfo.style.color = '#2ecc71'; // Green for RE
                } else if (team === 'KONTRA') {
                    teamInfo.style.color = '#e74c3c'; // Red for KONTRA
                }
                
                playerCardsEl.appendChild(teamInfo);
            }
        }
    }
    
    // Function to update the game variant display
    function updateGameVariantDisplay() {
        const gameVariantEl = document.getElementById('game-variant');
        if (!gameVariantEl) return;
        
        // Create a more detailed variant display
        let variantText = gameState.gameVariant || 'NORMAL';
        gameVariantEl.textContent = variantText;
        
        // Add player variant selections in a more visible way
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
                title.textContent = 'Player Variant Selections';
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
            title.textContent = 'Player Variant Selections';
            title.style.marginTop = '0';
            title.style.marginBottom = '10px';
            title.style.color = '#3498db';
            variantsContainer.appendChild(title);
            
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
                    
                    listItem.textContent = i === 0 ? 
                        `You: ${formattedVariant}` : 
                        `Player ${i}: ${formattedVariant}`;
                    
                    // Highlight the player's own selection
                    if (i === 0) {
                        listItem.style.fontWeight = 'bold';
                        listItem.style.color = '#2ecc71';
                    }
                    
                    variantsList.appendChild(listItem);
                }
            }
            
            variantsContainer.appendChild(variantsList);
        }
    }
    
    // Handle progress updates from the server
    socket.on('progress_update', function(data) {
        console.log('Progress update:', data);
        
        // Get progress elements
        const progressMessage = document.getElementById('progress-message');
        const progressBarFill = document.getElementById('progress-bar-fill');
        
        if (!progressMessage || !progressBarFill) return;
        
        // Update the progress message
        progressMessage.textContent = data.message;
        
        // Update progress bar based on the step
        switch(data.step) {
            case 'model_loading_start':
                progressBarFill.style.width = '30%';
                break;
            case 'model_loading_details':
                progressBarFill.style.width = '35%';
                break;
            case 'model_loading_success':
                progressBarFill.style.width = '40%';
                progressMessage.style.color = "#2ecc71"; // Green color for success
                break;
            case 'model_loading_error':
            case 'model_loading_fallback':
                progressBarFill.style.width = '40%';
                progressMessage.style.color = "#e74c3c"; // Red color for error
                break;
            case 'setup_other_agents':
                progressBarFill.style.width = '60%';
                progressMessage.style.color = ""; // Reset color
                break;
            case 'game_preparation':
                progressBarFill.style.width = '80%';
                break;
            case 'game_ready':
                progressBarFill.style.width = '100%';
                // Hide the progress container
                const progressContainer = document.getElementById('progress-container');
                if (progressContainer) {
                    progressContainer.classList.add('hidden');
                }
                
                // Show the game board with variant selection if we have a game ID
                if (gameState.gameId) {
                    console.log("Game ready, showing game board with variant selection");
                    
                    if (gameSetupScreen) {
                        console.log("Hiding game setup screen");
                        gameSetupScreen.classList.add('hidden');
                    }
                    
                    if (gameBoard) {
                        console.log("Showing game board");
                        // First make sure the element is visible in the DOM
                        gameBoard.style.display = "grid";
                        
                        // Then remove the hidden class
                        gameBoard.classList.remove('hidden');
                        
                        // Force a reflow to ensure the DOM updates
                        void gameBoard.offsetWidth;
                        
                        // Make sure the variant selection is visible
                        const gameVariantSelection = document.getElementById('game-variant-selection');
                        if (gameVariantSelection) {
                            console.log("Showing variant selection");
                            gameVariantSelection.classList.remove('hidden');
                            gameVariantSelection.style.display = "block";
                            
                            // Force a reflow to ensure the DOM updates
                            void gameVariantSelection.offsetWidth;
                            
                            console.log("Variant selection display:", gameVariantSelection.style.display);
                            console.log("Variant selection classes:", gameVariantSelection.className);
                        }
                    }
                    
                    // Render the player's hand - make sure this happens even during variant selection
                    console.log("Rendering player's hand during variant selection");
                    renderHand();
                    
                    // Update turn indicator
                    updateTurnIndicator();
                }
                break;
        }
    });
    
    socket.on('trick_completed', function(data) {
        console.log('Trick completed:', data);
        
        // Check if there were special captures (Diamond Aces or 40+ point tricks)
        if (gameState.diamond_ace_captured && Array.isArray(gameState.diamond_ace_captured)) {
            // Group captures by type
            const diamondAceCaptures = gameState.diamond_ace_captured.filter(capture => capture.type === 'diamond_ace' || !capture.type);
            const fortyPlusCaptures = gameState.diamond_ace_captured.filter(capture => capture.type === 'forty_plus');
            
            // Process Diamond Ace captures
            if (diamondAceCaptures.length > 0) {
                // Create a notification for Diamond Ace captures
                const notification = document.createElement('div');
                notification.className = 'special-notification diamond-ace-notification';
                notification.style.position = 'fixed';
                notification.style.top = '50%';
                notification.style.left = '50%';
                notification.style.transform = 'translate(-50%, -50%)';
                notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                notification.style.color = 'white';
                notification.style.padding = '20px';
                notification.style.borderRadius = '10px';
                notification.style.zIndex = '1000';
                notification.style.textAlign = 'center';
                notification.style.boxShadow = '0 0 20px rgba(255, 215, 0, 0.7)';
                notification.style.border = '2px solid gold';
                
                // Get the first capture for basic information
                const firstCapture = diamondAceCaptures[0];
                const winnerTeam = firstCapture.winner_team;
                const loserTeam = firstCapture.loser_team;
                
                // Create capture details for each Diamond Ace
                let captureDetails = '';
                diamondAceCaptures.forEach(capture => {
                    const winnerName = capture.winner === 0 ? 'You' : `Player ${capture.winner}`;
                    const loserName = capture.loser === 0 ? 'You' : `Player ${capture.loser}`;
                    captureDetails += `<p>${winnerName} (${capture.winner_team}) captured a Diamond Ace from ${loserName} (${capture.loser_team})!</p>`;
                });
                
                // Set the notification text
                notification.innerHTML = `
                    <h3 style="color: gold; margin-top: 0;">${diamondAceCaptures.length > 1 ? 'Diamond Aces Captured!' : 'Diamond Ace Captured!'}</h3>
                    ${captureDetails}
                    <p>+${diamondAceCaptures.length} ${diamondAceCaptures.length > 1 ? 'points' : 'point'} for team ${winnerTeam}, -${diamondAceCaptures.length} ${diamondAceCaptures.length > 1 ? 'points' : 'point'} for team ${loserTeam}</p>
                    <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
                        ${Array(diamondAceCaptures.length).fill('<img src="/static/images/cards/AD.png" style="width: 60px; height: auto; filter: drop-shadow(0 0 10px gold);">').join('')}
                    </div>
                `;
                
                // Add the notification to the document
                document.body.appendChild(notification);
                
                // Remove the notification after 3 seconds
                setTimeout(() => {
                    notification.style.opacity = '0';
                    notification.style.transition = 'opacity 0.5s ease-out';
                    
                    // Remove from DOM after fade out
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }, 500);
                }, 3000);
            }
            
            // Process 40+ point tricks
            if (fortyPlusCaptures.length > 0) {
                // Wait a bit if we also showed a Diamond Ace notification
                const delay = diamondAceCaptures.length > 0 ? 3500 : 0;
                
                setTimeout(() => {
                    // Create a notification for 40+ point tricks
                    const notification = document.createElement('div');
                    notification.className = 'special-notification forty-plus-notification';
                    notification.style.position = 'fixed';
                    notification.style.top = '50%';
                    notification.style.left = '50%';
                    notification.style.transform = 'translate(-50%, -50%)';
                    notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                    notification.style.color = 'white';
                    notification.style.padding = '20px';
                    notification.style.borderRadius = '10px';
                    notification.style.zIndex = '1000';
                    notification.style.textAlign = 'center';
                    notification.style.boxShadow = '0 0 20px rgba(65, 105, 225, 0.7)'; // Royal blue shadow
                    notification.style.border = '2px solid royalblue';
                    
                    // Get the first capture for basic information
                    const capture = fortyPlusCaptures[0];
                    const winnerName = capture.winner === 0 ? 'You' : `Player ${capture.winner}`;
                    const winnerTeam = capture.winner_team;
                    
                    // Set the notification text
                    notification.innerHTML = `
                        <h3 style="color: royalblue; margin-top: 0;">40+ Point Trick!</h3>
                        <p>${winnerName} (${winnerTeam}) won a trick worth ${capture.points} points!</p>
                        <p>+1 bonus point for team ${winnerTeam}</p>
                        <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
                            <div style="background-color: royalblue; color: white; font-size: 24px; width: 60px; height: 60px; display: flex; justify-content: center; align-items: center; border-radius: 50%; filter: drop-shadow(0 0 10px royalblue);">
                                ${capture.points}
                            </div>
                        </div>
                    `;
                    
                    // Add the notification to the document
                    document.body.appendChild(notification);
                    
                    // Remove the notification after 3 seconds
                    setTimeout(() => {
                        notification.style.opacity = '0';
                        notification.style.transition = 'opacity 0.5s ease-out';
                        
                        // Remove from DOM after fade out
                        setTimeout(() => {
                            if (notification.parentNode) {
                                notification.parentNode.removeChild(notification);
                            }
                        }, 500);
                    }, 3000);
                }, delay);
            }
            
            // Clear the diamond_ace_captured flag
            delete gameState.diamond_ace_captured;
        }
    });
    
    // Function to check if a card is a trump card
    function isTrumpCard(card) {
        if (!card) return false;
        
        // In normal Doppelkopf, trumps are:
        // - All Diamonds (except for some variants)
        // - All Jacks
        // - All Queens
        
        // Check game variant for special rules
        if (gameState.gameVariant === 'FLESHLESS') {
            // In Fleshless, only Jacks and Queens are trump
            return card.rank === 'JACK' || card.rank === 'QUEEN';
        } else if (gameState.gameVariant === 'JACK_SOLO') {
            // In Jack Solo, only Jacks are trump
            return card.rank === 'JACK';
        } else if (gameState.gameVariant === 'QUEEN_SOLO') {
            // In Queen Solo, only Queens are trump
            return card.rank === 'QUEEN';
        } else if (gameState.gameVariant === 'TRUMP_SOLO') {
            // In Trump Solo, all normal trumps are trump
            return card.suit === 'DIAMONDS' || card.rank === 'JACK' || card.rank === 'QUEEN';
        } else {
            // Normal game
            return card.suit === 'DIAMONDS' || card.rank === 'JACK' || card.rank === 'QUEEN' || 
                   (card.suit === 'HEARTS' && card.rank === 'TEN'); // 10 of Hearts is also trump
        }
    }
    
    // Function to create a card element
    function createCardElement(card, isPlayable) {
        const cardContainer = document.createElement('div');
        cardContainer.className = 'card-container';
        cardContainer.dataset.cardId = card.id;
        
        const cardElement = document.createElement('img');
        cardElement.className = 'card';
        
        // Use the card's suit and rank to determine the image path
        const suitMap = {
            'CLUBS': 'C',
            'SPADES': 'S',
            'HEARTS': 'H',
            'DIAMONDS': 'D'
        };
        
        const rankMap = {
            'NINE': '9',
            'TEN': '0', // Use '0' for 10s since we have 0C.png, 0D.png, etc.
            'JACK': 'J',
            'QUEEN': 'Q',
            'KING': 'K',
            'ACE': 'A'
        };
        
        // Use the format without the blue "2" markers (e.g., "9C.png" instead of "9_of_clubs.png")
        const cardCode = rankMap[card.rank] + suitMap[card.suit];
        const cardSrc = `/static/images/cards/${cardCode}.png`;
        
        cardElement.src = cardSrc;
        cardElement.alt = `${card.rank} of ${card.suit}`;
        
        cardContainer.appendChild(cardElement);
        
        // Add click event for playable cards
        if (isPlayable) {
            cardContainer.classList.add('playable');
            cardContainer.addEventListener('click', () => playCard(card.id));
        }
        
        return cardContainer;
    }
    
    // Function to sort cards in the desired order: trumps first, then clubs, spades, hearts
    function sortCards(cards) {
        return [...cards].sort((a, b) => {
            // First check if either card is a trump
            const aIsTrump = isTrumpCard(a);
            const bIsTrump = isTrumpCard(b);
            
            // If one is trump and the other isn't, the trump comes first
            if (aIsTrump && !bIsTrump) return -1;
            if (!aIsTrump && bIsTrump) return 1;
            
            // If both are trumps or both are not trumps, sort by suit
            if (aIsTrump && bIsTrump) {
                // Check for 10 of Hearts (highest trump)
                if (a.suit === 'HEARTS' && a.rank === 'TEN') return -1;
                if (b.suit === 'HEARTS' && b.rank === 'TEN') return 1;
                
                // For trumps, sort by rank first (Queens, Jacks, then Diamonds)
                if (a.rank === 'QUEEN' && b.rank !== 'QUEEN') return -1;
                if (a.rank !== 'QUEEN' && b.rank === 'QUEEN') return 1;
                if (a.rank === 'JACK' && b.rank !== 'JACK') return -1;
                if (a.rank !== 'JACK' && b.rank === 'JACK') return 1;
                
                // If both are the same rank (both Queens or both Jacks), sort by suit
                if ((a.rank === 'QUEEN' && b.rank === 'QUEEN') || (a.rank === 'JACK' && b.rank === 'JACK')) {
                    // Clubs, Spades, Hearts, Diamonds
                    const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
                    return suitOrder[a.suit] - suitOrder[b.suit];
                }
                
                // If both are diamonds but not Queens or Jacks, sort by rank
                const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
                return rankOrder[a.rank] - rankOrder[b.rank];
            } else {
                // For non-trumps, sort by suit first: clubs, spades, hearts
                const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
                if (a.suit !== b.suit) {
                    return suitOrder[a.suit] - suitOrder[b.suit];
                }
                
                // If same suit, sort by rank: Ace, 10, King, Queen, Jack, 9
                const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
                return rankOrder[a.rank] - rankOrder[b.rank];
            }
        });
    }
    
    // Function to update the announcement buttons visibility
    function updateAnnouncementButtons() {
        // Get the announcement buttons
        const gameReBtn = document.getElementById('game-re-btn');
        const gameContraBtn = document.getElementById('game-contra-btn');
        
        // Get the announcement areas
        const gameAnnouncementArea = document.getElementById('game-announcement-area');
        
        // Determine which announcement button to show based on the game state
        // For RE team
        if (gameState.playerTeam === 'RE') {
            
            // Same for game Re button
            if (gameReBtn) {
                if (!gameState.announcements || !gameState.announcements.re) {
                    gameReBtn.textContent = 'Re';
                    gameReBtn.onclick = () => makeAnnouncement('re');
                    gameReBtn.disabled = !gameState.canAnnounceRe;
                    gameReBtn.style.opacity = gameState.canAnnounceRe ? '1' : '0.5';
                } else if (gameState.canAnnounceNo90) {
                    gameReBtn.textContent = 'No 90';
                    gameReBtn.onclick = () => makeAnnouncement('no90');
                    gameReBtn.disabled = !gameState.canAnnounceNo90;
                    gameReBtn.style.opacity = gameState.canAnnounceNo90 ? '1' : '0.5';
                } else if (gameState.canAnnounceNo60) {
                    gameReBtn.textContent = 'No 60';
                    gameReBtn.onclick = () => makeAnnouncement('no60');
                    gameReBtn.disabled = !gameState.canAnnounceNo60;
                    gameReBtn.style.opacity = gameState.canAnnounceNo60 ? '1' : '0.5';
                } else if (gameState.canAnnounceNo30) {
                    gameReBtn.textContent = 'No 30';
                    gameReBtn.onclick = () => makeAnnouncement('no30');
                    gameReBtn.disabled = !gameState.canAnnounceNo30;
                    gameReBtn.style.opacity = gameState.canAnnounceNo30 ? '1' : '0.5';
                } else if (gameState.canAnnounceBlack) {
                    gameReBtn.textContent = 'Black';
                    gameReBtn.onclick = () => makeAnnouncement('black');
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
            
            // Same for game Contra button
            if (gameContraBtn) {
                if (!gameState.announcements || !gameState.announcements.contra) {
                    gameContraBtn.textContent = 'Contra';
                    gameContraBtn.onclick = () => makeAnnouncement('contra');
                    gameContraBtn.disabled = !gameState.canAnnounceContra;
                    gameContraBtn.style.opacity = gameState.canAnnounceContra ? '1' : '0.5';
                } else if (gameState.canAnnounceNo90) {
                    gameContraBtn.textContent = 'No 90';
                    gameContraBtn.onclick = () => makeAnnouncement('no90');
                    gameContraBtn.disabled = !gameState.canAnnounceNo90;
                    gameContraBtn.style.opacity = gameState.canAnnounceNo90 ? '1' : '0.5';
                } else if (gameState.canAnnounceNo60) {
                    gameContraBtn.textContent = 'No 60';
                    gameContraBtn.onclick = () => makeAnnouncement('no60');
                    gameContraBtn.disabled = !gameState.canAnnounceNo60;
                    gameContraBtn.style.opacity = gameState.canAnnounceNo60 ? '1' : '0.5';
                } else if (gameState.canAnnounceNo30) {
                    gameContraBtn.textContent = 'No 30';
                    gameContraBtn.onclick = () => makeAnnouncement('no30');
                    gameContraBtn.disabled = !gameState.canAnnounceNo30;
                    gameContraBtn.style.opacity = gameState.canAnnounceNo30 ? '1' : '0.5';
                } else if (gameState.canAnnounceBlack) {
                    gameContraBtn.textContent = 'Black';
                    gameContraBtn.onclick = () => makeAnnouncement('black');
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
        }
        
        // Show/hide the announcement areas based on whether announcements are allowed
        
        if (gameAnnouncementArea) {
            const canAnnounce = (gameState.playerTeam === 'RE' && (gameState.canAnnounceRe || gameState.canAnnounceNo90 || 
                                gameState.canAnnounceNo60 || gameState.canAnnounceNo30 || gameState.canAnnounceBlack)) ||
                               (gameState.playerTeam === 'KONTRA' && (gameState.canAnnounceContra || gameState.canAnnounceNo90 || 
                                gameState.canAnnounceNo60 || gameState.canAnnounceNo30 || gameState.canAnnounceBlack));
            
            gameAnnouncementArea.classList.toggle('hidden', !canAnnounce);
        }
        
        // Update announcement status displays
        const reStatus = document.getElementById('re-status');
        const contraStatus = document.getElementById('contra-status');
        const gameReStatus = document.getElementById('game-re-status');
        const gameContraStatus = document.getElementById('game-contra-status');
        
        if (reStatus && gameState.announcements && gameState.announcements.re) {
            reStatus.classList.remove('hidden');
        } else if (reStatus) {
            reStatus.classList.add('hidden');
        }
        
        if (contraStatus && gameState.announcements && gameState.announcements.contra) {
            contraStatus.classList.remove('hidden');
        } else if (contraStatus) {
            contraStatus.classList.add('hidden');
        }
        
        if (gameReStatus && gameState.announcements && gameState.announcements.re) {
            gameReStatus.classList.remove('hidden');
        } else if (gameReStatus) {
            gameReStatus.classList.add('hidden');
        }
        
        if (gameContraStatus && gameState.announcements && gameState.announcements.contra) {
            gameContraStatus.classList.remove('hidden');
        } else if (gameContraStatus) {
            gameContraStatus.classList.add('hidden');
        }
        
        // Update additional announcement status displays
        const no90Status = document.getElementById('no90-status');
        const no60Status = document.getElementById('no60-status');
        const no30Status = document.getElementById('no30-status');
        const blackStatus = document.getElementById('black-status');
        const gameNo90Status = document.getElementById('game-no90-status');
        const gameNo60Status = document.getElementById('game-no60-status');
        const gameNo30Status = document.getElementById('game-no30-status');
        const gameBlackStatus = document.getElementById('game-black-status');
        
        if (no90Status && gameState.announcements && gameState.announcements.no90) {
            no90Status.classList.remove('hidden');
        } else if (no90Status) {
            no90Status.classList.add('hidden');
        }
        
        if (no60Status && gameState.announcements && gameState.announcements.no60) {
            no60Status.classList.remove('hidden');
        } else if (no60Status) {
            no60Status.classList.add('hidden');
        }
        
        if (no30Status && gameState.announcements && gameState.announcements.no30) {
            no30Status.classList.remove('hidden');
        } else if (no30Status) {
            no30Status.classList.add('hidden');
        }
        
        if (blackStatus && gameState.announcements && gameState.announcements.black) {
            blackStatus.classList.remove('hidden');
        } else if (blackStatus) {
            blackStatus.classList.add('hidden');
        }
        
        if (gameNo90Status && gameState.announcements && gameState.announcements.no90) {
            gameNo90Status.classList.remove('hidden');
        } else if (gameNo90Status) {
            gameNo90Status.classList.add('hidden');
        }
        
        if (gameNo60Status && gameState.announcements && gameState.announcements.no60) {
            gameNo60Status.classList.remove('hidden');
        } else if (gameNo60Status) {
            gameNo60Status.classList.add('hidden');
        }
        
        if (gameNo30Status && gameState.announcements && gameState.announcements.no30) {
            gameNo30Status.classList.remove('hidden');
        } else if (gameNo30Status) {
            gameNo30Status.classList.add('hidden');
        }
        
        if (gameBlackStatus && gameState.announcements && gameState.announcements.black) {
            gameBlackStatus.classList.remove('hidden');
        } else if (gameBlackStatus) {
            gameBlackStatus.classList.add('hidden');
        }
        
        // Update multiplier displays
        const multiplierEl = document.getElementById('multiplier');
        const gameMultiplierEl = document.getElementById('game-multiplier');
        
        if (multiplierEl) {
            multiplierEl.textContent = `${gameState.multiplier || 1}x`;
        }
        
        if (gameMultiplierEl) {
            gameMultiplierEl.textContent = `${gameState.multiplier || 1}x`;
        }
    }
    
    // Function to make an announcement (Re, Contra, or additional announcements)
    function makeAnnouncement(announcement) {
        console.log(`Making announcement: ${announcement}`);
        
        fetch('/announce', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                announcement: announcement
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Announcement response:", data);
            
            // Update game state with the response data
            if (data.state) {
                // Update the game state
                gameState.hand = data.state.hand || gameState.hand;
                gameState.currentTrick = data.state.current_trick || gameState.currentTrick;
                gameState.currentPlayer = data.state.current_player;
                gameState.legalActions = data.state.legal_actions || gameState.legalActions;
                gameState.canAnnounceRe = data.state.can_announce_re || false;
                gameState.canAnnounceContra = data.state.can_announce_contra || false;
                gameState.canAnnounceNo90 = data.state.can_announce_no90 || false;
                gameState.canAnnounceNo60 = data.state.can_announce_no60 || false;
                gameState.canAnnounceNo30 = data.state.can_announce_no30 || false;
                gameState.canAnnounceBlack = data.state.can_announce_black || false;
                
                // Update announcements
                if (!gameState.announcements) {
                    gameState.announcements = {};
                }
                
                // Update the specific announcement that was made
                if (announcement === 're') {
                    gameState.announcements.re = true;
                } else if (announcement === 'contra') {
                    gameState.announcements.contra = true;
                } else if (announcement === 'no90') {
                    gameState.announcements.no90 = true;
                } else if (announcement === 'no60') {
                    gameState.announcements.no60 = true;
                } else if (announcement === 'no30') {
                    gameState.announcements.no30 = true;
                } else if (announcement === 'black') {
                    gameState.announcements.black = true;
                }
                
                // Update multiplier
                gameState.multiplier = data.multiplier || gameState.multiplier;
            } else {
                // If no state is returned, update from the individual fields
                if (data.re_announced !== undefined) gameState.announcements.re = data.re_announced;
                if (data.contra_announced !== undefined) gameState.announcements.contra = data.contra_announced;
                if (data.no90_announced !== undefined) gameState.announcements.no90 = data.no90_announced;
                if (data.no60_announced !== undefined) gameState.announcements.no60 = data.no60_announced;
                if (data.no30_announced !== undefined) gameState.announcements.no30 = data.no30_announced;
                if (data.black_announced !== undefined) gameState.announcements.black = data.black_announced;
                
                if (data.multiplier !== undefined) gameState.multiplier = data.multiplier;
            }
            
            // Update the announcement buttons
            updateAnnouncementButtons();
        })
        .catch(error => {
            console.error('Error making announcement:', error);
            alert(`Error: ${error.message}`);
        });
    }
    
    // Function to update the turn indicator
    function updateTurnIndicator() {
        if (!turnIndicatorEl) return;
        
        if (gameState.currentPlayer === 0) {
            turnIndicatorEl.textContent = "Your turn";
        } else {
            turnIndicatorEl.textContent = `Waiting for Player ${gameState.currentPlayer}...`;
        }
    }
    
    // Function to render the player's hand
    function renderHand() {
        if (!playerHandEl) return;
        
        playerHandEl.innerHTML = '';
        
        // Sort the cards: trumps first, then clubs, spades, hearts
        const sortedHand = sortCards(gameState.hand);
        
        // Render the sorted hand
        sortedHand.forEach(card => {
            // Check if the card is in the legal actions
            const isPlayable = gameState.currentPlayer === 0 && 
                               gameState.legalActions.some(legalCard => legalCard.id === card.id);
            
            // Only make cards playable if they are legal moves
            const cardElement = createCardElement(card, isPlayable);
            playerHandEl.appendChild(cardElement);
        });
    }
    
    // Function to render the current trick
    function renderCurrentTrick() {
        // Get the hardcoded trick element
        const hardcodedTrickEl = document.getElementById('hardcoded-trick');
        if (!hardcodedTrickEl) return;
        
        // Clear the trick element
        hardcodedTrickEl.innerHTML = '';
        
        // Always set up the grid layout, even if there are no cards yet
        // This ensures the layout doesn't change when it's the user's turn
        hardcodedTrickEl.style.display = "grid";
        hardcodedTrickEl.style.gridTemplateAreas = `
            ".     top    ."
            "left  .      right"
            ".     bottom ."
        `;
        hardcodedTrickEl.style.gridTemplateColumns = "1fr 1fr 1fr";
        hardcodedTrickEl.style.gridTemplateRows = "1fr 1fr 1fr";
        hardcodedTrickEl.style.gap = "10px";
        hardcodedTrickEl.style.width = "300px";
        hardcodedTrickEl.style.height = "300px";
        hardcodedTrickEl.style.margin = "0 auto";
        
        // If there are no cards in the trick, just return after setting up the grid
        if (!gameState.currentTrick || gameState.currentTrick.length === 0) {
            return;
        }
        
        // Calculate the starting player for this trick
        const startingPlayer = (gameState.currentPlayer - gameState.currentTrick.length) % 4;
        
        // Create a container for each card with player information
        for (let i = 0; i < gameState.currentTrick.length; i++) {
            const card = gameState.currentTrick[i];
            
            // Calculate which player played this card
            const playerIdx = (startingPlayer + i) % 4;
            
            // Create a container for the card and player label
            const cardContainer = document.createElement('div');
            cardContainer.className = 'trick-card-container';
            
            // Position the card based on the player's position relative to the user
            // Player 0 is the user (bottom), Player 1 is left, Player 2 is top, Player 3 is right
            let position;
            if (playerIdx === 0) {
                position = "bottom";
                cardContainer.style.gridArea = "bottom";
                cardContainer.style.justifySelf = "center";
            } else if (playerIdx === 1) {
                position = "left";
                cardContainer.style.gridArea = "left";
                cardContainer.style.justifySelf = "start";
            } else if (playerIdx === 2) {
                position = "top";
                cardContainer.style.gridArea = "top";
                cardContainer.style.justifySelf = "center";
            } else if (playerIdx === 3) {
                position = "right";
                cardContainer.style.gridArea = "right";
                cardContainer.style.justifySelf = "end";
            }
            
            // Create the card element
            const cardElement = createCardElement(card, false); // Cards in the trick are not playable
            
            // Create a player label
            const playerLabel = document.createElement('div');
            playerLabel.className = 'player-label';
            
            // Determine if this is the first round (trick)
            const isFirstRound = gameState.currentTrick.length <= 4;
            
            // Add team information for the first round
            if (isFirstRound) {
                // Determine the player's team based on their cards
                let teamInfo = "";
                
                // Check if the card is a Queen of Clubs (indicates RE team)
                if (card.suit === 'CLUBS' && card.rank === 'QUEEN') {
                    teamInfo = " (RE)";
                } else if (card.suit === 'SPADES' && card.rank === 'QUEEN') {
                    teamInfo = " (likely RE)";
                } else if (card.suit === 'HEARTS' && card.rank === 'QUEEN') {
                    teamInfo = " (likely RE)";
                } else if (card.suit === 'DIAMONDS' && card.rank === 'QUEEN') {
                    teamInfo = " (likely RE)";
                } else if (card.rank === 'JACK') {
                    teamInfo = " (unknown)";
                } else {
                    teamInfo = " (likely KONTRA)";
                }
                
                playerLabel.textContent = playerIdx === 0 ? `You${teamInfo}` : `Player ${playerIdx}${teamInfo}`;
            } else {
                playerLabel.textContent = playerIdx === 0 ? 'You' : `Player ${playerIdx}`;
            }
            
            // Position the label based on the player's position
            if (position === "bottom") {
                playerLabel.style.order = "1"; // Label below card
            } else if (position === "top") {
                playerLabel.style.order = "-1"; // Label above card
            } else if (position === "left") {
                cardContainer.style.flexDirection = "row";
                playerLabel.style.marginRight = "10px";
            } else if (position === "right") {
                cardContainer.style.flexDirection = "row-reverse";
                playerLabel.style.marginLeft = "10px";
            }
            
            // Add the player label and card to the container
            cardContainer.appendChild(playerLabel);
            cardContainer.appendChild(cardElement);
            
            // Add the container to the trick display
            hardcodedTrickEl.appendChild(cardContainer);
        }
    }
    
    // Function to start a new game
    function startNewGame() {
        console.log("Starting new game...");
        
        // Show progress container and hide the new game button
        const newGameBtn = document.getElementById('new-game-btn');
        const progressContainer = document.getElementById('progress-container');
        const progressBarFill = document.getElementById('progress-bar-fill');
        const progressMessage = document.getElementById('progress-message');
        const gameSetupScreen = document.getElementById('game-setup');
        const gameBoard = document.getElementById('game-board');
        
        if (newGameBtn) newGameBtn.classList.add('hidden');
        if (progressContainer) progressContainer.classList.remove('hidden');
        
        // Hide the game setup screen and show the game board
        if (gameSetupScreen) gameSetupScreen.classList.add('hidden');
        if (gameBoard) {
            gameBoard.style.display = 'grid';
            console.log("Game board display set to grid");
        }
        
        // Reset progress bar
        if (progressBarFill) progressBarFill.style.width = '10%';
        if (progressMessage) progressMessage.textContent = "Initializing game...";
        
        // Make the API request
        fetch('/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("New game response:", data);
            
            gameState.gameId = data.game_id;
            
            // Join the Socket.IO room for this game
            socket.emit('join', { game_id: gameState.gameId });
            
            // Update game state with the response data
            if (data.state) {
                gameState.hand = data.state.hand || [];
                gameState.currentPlayer = data.state.current_player;
                gameState.playerTeam = data.state.player_team;
                gameState.gameVariant = data.state.game_variant;
                gameState.legalActions = data.state.legal_actions || [];
                
                // Immediately render the player's hand to ensure it's visible during variant selection
                console.log("Rendering player's hand after receiving game state");
                renderHand();
            }
        })
        .catch(error => {
            console.error('Error starting new game:', error);
            
            // Show error message
            if (progressMessage) {
                progressMessage.textContent = "Error starting game. Please try again.";
                progressMessage.style.color = "#e74c3c";
            }
            
            // Show the new game button again
            if (newGameBtn) newGameBtn.classList.remove('hidden');
        });
    }
    
    // Function to set the game variant
    function setGameVariant(variant) {
        console.log("Setting game variant:", variant);
        
        // Make sure the player's hand is visible during variant selection
        renderHand();
        
        fetch('/set_variant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                variant: variant
            })
        })
        .then(response => {
            if (!response.ok) {
                console.log(`Server returned ${response.status}: ${response.statusText}`);
                // If we get a 400 error, the game is likely not in variant selection phase anymore
                // Just show the game board
                if (response.status === 400) {
                    console.log("Got 400 response, showing game board anyway");
                    
                    // Make sure the game board is visible
                    if (gameBoard) {
                        console.log("Showing game board");
                        // First make sure the element is visible in the DOM
                        gameBoard.style.display = "grid";
                        
                        // Then remove the hidden class
                        gameBoard.classList.remove('hidden');
                        
                        // Force a reflow to ensure the DOM updates
                        void gameBoard.offsetWidth;
                        
                        console.log("gameBoard classes after showing:", gameBoard.className);
                        console.log("gameBoard style.display:", gameBoard.style.display);
                    }
                    
                    // Hide the variant selection area in the game board
                    const gameVariantSelection = document.getElementById('game-variant-selection');
                    if (gameVariantSelection) {
                        gameVariantSelection.classList.add('hidden');
                    }
                }
                return Promise.resolve({state: {}}); // Return an empty state object to avoid errors
            }
            return response.json();
        })
        .then(data => {
            console.log("Set variant response:", data);
            
            // Update game state with the response data
            if (data.state) {
                gameState.hand = data.state.hand || [];
                gameState.gameVariant = data.state.game_variant;
                gameState.legalActions = data.state.legal_actions || [];
                
                if (data.state.current_player !== undefined) {
                    gameState.currentPlayer = data.state.current_player;
                }
            }
            
            // Make sure the game board is visible
            if (gameBoard) {
                console.log("Showing game board");
                // First make sure the element is visible in the DOM
                gameBoard.style.display = "grid";
                
                // Then remove the hidden class
                gameBoard.classList.remove('hidden');
                
                // Force a reflow to ensure the DOM updates
                void gameBoard.offsetWidth;
                
                console.log("gameBoard classes after showing:", gameBoard.className);
                console.log("gameBoard style.display:", gameBoard.style.display);
            }
            
            // Hide the variant selection area in the game board
            const gameVariantSelection = document.getElementById('game-variant-selection');
            if (gameVariantSelection) {
                gameVariantSelection.classList.add('hidden');
            }
            
            // Render the player's hand
            renderHand();
            
            // Update turn indicator
            updateTurnIndicator();
        })
        .catch(error => {
            console.error('Error setting game variant:', error);
            
            // Even if there's an error, make sure the game board is visible
            if (gameBoard) {
                console.log("Showing game board despite error");
                gameBoard.style.display = "grid";
                gameBoard.classList.remove('hidden');
            }
        });
    }
    
    // Function to show the last trick
    function showLastTrick() {
        console.log('Showing last trick');
        
        // Get the last trick container
        const lastTrickContainer = document.querySelector('.last-trick-container');
        const lastTrickEl = document.getElementById('last-trick');
        const trickWinnerEl = document.getElementById('trick-winner');
        
        if (!lastTrickContainer || !lastTrickEl || !trickWinnerEl) {
            console.error('Last trick elements not found');
            return;
        }
        
        // Make an API request to get the last trick
        fetch(`/get_last_trick?game_id=${gameState.gameId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Last trick data:', data);
                
                // Clear the last trick element
                lastTrickEl.innerHTML = '';
                
                // If there's no last trick, show a message
                if (!data.last_trick || data.last_trick.length === 0) {
                    trickWinnerEl.textContent = 'No last trick available';
                    return;
                }
                
                // Create a container for each card with player information
                for (let i = 0; i < data.last_trick.length; i++) {
                    const card = data.last_trick[i];
                    
                    // Create the card element
                    const cardElement = createCardElement(card, false); // Cards in the last trick are not playable
                    
                    // Add the card to the last trick display
                    lastTrickEl.appendChild(cardElement);
                }
                
                // Show the trick winner
                const winnerName = data.winner === 0 ? 'You' : `Player ${data.winner}`;
                trickWinnerEl.textContent = `Winner: ${winnerName} (${data.trick_points} points)`;
                
                // Show the last trick container
                lastTrickContainer.classList.remove('hidden');
                
                // Hide the current trick container
                const trickArea = document.querySelector('.trick-area');
                if (trickArea) {
                    trickArea.style.display = 'none';
                }
                
                // Check if a close button already exists
                const existingCloseButton = lastTrickContainer.querySelector('.close-trick-btn');
                
                if (!existingCloseButton) {
                    // Add a close button
                    const closeButton = document.createElement('button');
                    closeButton.textContent = 'Close';
                    closeButton.className = 'btn close-trick-btn';
                    closeButton.style.marginTop = '10px';
                    closeButton.addEventListener('click', () => {
                        // Hide the last trick container
                        lastTrickContainer.classList.add('hidden');
                        
                        // Show the current trick container
                        if (trickArea) {
                            trickArea.style.display = 'block';
                        }
                    });
                    
                    // Add the close button to the last trick container
                    lastTrickContainer.appendChild(closeButton);
                }
            })
            .catch(error => {
                console.error('Error getting last trick:', error);
                trickWinnerEl.textContent = 'Error getting last trick';
            });
    }
    
    // Function to play a card
    function playCard(cardId) {
        console.log('Playing card:', cardId);
        
        // Find the card in the hand
        const card = gameState.hand.find(c => c.id === cardId);
        if (!card) {
            console.error("Card not found in hand:", cardId);
            return;
        }
        
        // Optimistically update the UI to show the card being played
        // Add the card to the current trick
        const currentTrick = gameState.currentTrick || [];
        currentTrick.push(card);
        gameState.currentTrick = currentTrick;
        
        // Remove the card from the hand
        gameState.hand = gameState.hand.filter(c => c.id !== cardId);
        
        // Render the updated hand and trick
        renderHand();
        renderCurrentTrick();
        
        // Send the card to the server
        fetch('/play_card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                card_id: cardId
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Play card response:", data);
            
            // Update game state with the response data
            if (data.state) {
                gameState.hand = data.state.hand || [];
                gameState.currentTrick = data.state.current_trick || [];
                gameState.currentPlayer = data.state.current_player;
                gameState.legalActions = data.state.legal_actions || [];
            }
            
            // Render the player's hand and current trick
            renderHand();
            renderCurrentTrick();
            
            // Update turn indicator
            updateTurnIndicator();
        })
        .catch(error => {
            console.error('Error playing card:', error);
            
            // Revert the optimistic update
            gameState.hand.push(card);
            gameState.currentTrick = gameState.currentTrick.filter(c => c.id !== cardId);
            
            // Render the reverted hand and trick
            renderHand();
            renderCurrentTrick();
        });
    }
    
    // Function to reveal AI hands
    function revealAIHands() {
        console.log('Revealing AI hands');
        
        // Make an API request to get the AI hands
        fetch(`/get_ai_hands?game_id=${gameState.gameId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('AI hands data:', data);
                
                // Get the AI card visualization containers
                const player1Cards = document.getElementById('player1-cards');
                const player2Cards = document.getElementById('player2-cards');
                const player3Cards = document.getElementById('player3-cards');
                
                if (!player1Cards || !player2Cards || !player3Cards) {
                    console.error('AI card containers not found');
                    return;
                }
                
                // Clear previous content
                player1Cards.innerHTML = '';
                player2Cards.innerHTML = '';
                player3Cards.innerHTML = '';
                
                // Display Player 1's cards
                if (data.player1 && data.player1.length > 0) {
                    // Create a container for all cards
                    const cardsContainer = document.createElement('div');
                    
                    // Split cards into two rows
                    const firstRowContainer = document.createElement('div');
                    firstRowContainer.style.display = 'flex';
                    firstRowContainer.style.flexDirection = 'row';
                    firstRowContainer.style.gap = '2px';
                    firstRowContainer.style.marginBottom = '4px';
                    
                    const secondRowContainer = document.createElement('div');
                    secondRowContainer.style.display = 'flex';
                    secondRowContainer.style.flexDirection = 'row';
                    secondRowContainer.style.gap = '2px';
                    
                    // Calculate how many cards go in each row
                    const halfLength = Math.ceil(data.player1.length / 2);
                    
                    // Add cards to the first row
                    data.player1.slice(0, halfLength).forEach(card => {
                        const cardElement = createCardElement(card, false);
                        // Make the cards larger
                        const cardImg = cardElement.querySelector('img');
                        if (cardImg) {
                            cardImg.style.width = '40px';
                            cardImg.style.height = 'auto';
                        }
                        firstRowContainer.appendChild(cardElement);
                    });
                    
                    // Add cards to the second row
                    data.player1.slice(halfLength).forEach(card => {
                        const cardElement = createCardElement(card, false);
                        // Make the cards larger
                        const cardImg = cardElement.querySelector('img');
                        if (cardImg) {
                            cardImg.style.width = '40px';
                            cardImg.style.height = 'auto';
                        }
                        secondRowContainer.appendChild(cardElement);
                    });
                    
                    // Add both rows to the container
                    cardsContainer.appendChild(firstRowContainer);
                    cardsContainer.appendChild(secondRowContainer);
                    
                    player1Cards.appendChild(cardsContainer);
                    
                    // Add team information
                    const teamInfo = document.createElement('div');
                    teamInfo.textContent = `Team: ${gameState.otherPlayers[0].team}`;
                    teamInfo.style.marginTop = '5px';
                    teamInfo.style.fontWeight = 'bold';
                    
                    // Add color coding for teams
                    if (gameState.otherPlayers[0].team === 'RE') {
                        teamInfo.style.color = '#2ecc71'; // Green for RE
                    } else if (gameState.otherPlayers[0].team === 'KONTRA') {
                        teamInfo.style.color = '#e74c3c'; // Red for KONTRA
                    }
                    
                    player1Cards.appendChild(teamInfo);
                }
                
                // Display Player 2's cards
                if (data.player2 && data.player2.length > 0) {
                    // Create a container for all cards
                    const cardsContainer = document.createElement('div');
                    
                    // Split cards into two rows
                    const firstRowContainer = document.createElement('div');
                    firstRowContainer.style.display = 'flex';
                    firstRowContainer.style.flexDirection = 'row';
                    firstRowContainer.style.gap = '2px';
                    firstRowContainer.style.marginBottom = '4px';
                    
                    const secondRowContainer = document.createElement('div');
                    secondRowContainer.style.display = 'flex';
                    secondRowContainer.style.flexDirection = 'row';
                    secondRowContainer.style.gap = '2px';
                    
                    // Calculate how many cards go in each row
                    const halfLength = Math.ceil(data.player2.length / 2);
                    
                    // Add cards to the first row
                    data.player2.slice(0, halfLength).forEach(card => {
                        const cardElement = createCardElement(card, false);
                        // Make the cards larger
                        const cardImg = cardElement.querySelector('img');
                        if (cardImg) {
                            cardImg.style.width = '40px';
                            cardImg.style.height = 'auto';
                        }
                        firstRowContainer.appendChild(cardElement);
                    });
                    
                    // Add cards to the second row
                    data.player2.slice(halfLength).forEach(card => {
                        const cardElement = createCardElement(card, false);
                        // Make the cards larger
                        const cardImg = cardElement.querySelector('img');
                        if (cardImg) {
                            cardImg.style.width = '40px';
                            cardImg.style.height = 'auto';
                        }
                        secondRowContainer.appendChild(cardElement);
                    });
                    
                    // Add both rows to the container
                    cardsContainer.appendChild(firstRowContainer);
                    cardsContainer.appendChild(secondRowContainer);
                    
                    player2Cards.appendChild(cardsContainer);
                    
                    // Add team information
                    const teamInfo = document.createElement('div');
                    teamInfo.textContent = `Team: ${gameState.otherPlayers[1].team}`;
                    teamInfo.style.marginTop = '5px';
                    teamInfo.style.fontWeight = 'bold';
                    
                    // Add color coding for teams
                    if (gameState.otherPlayers[1].team === 'RE') {
                        teamInfo.style.color = '#2ecc71'; // Green for RE
                    } else if (gameState.otherPlayers[1].team === 'KONTRA') {
                        teamInfo.style.color = '#e74c3c'; // Red for KONTRA
                    }
                    
                    player2Cards.appendChild(teamInfo);
                }
                
                // Display Player 3's cards
                if (data.player3 && data.player3.length > 0) {
                    // Create a container for all cards
                    const cardsContainer = document.createElement('div');
                    
                    // Split cards into two rows
                    const firstRowContainer = document.createElement('div');
                    firstRowContainer.style.display = 'flex';
                    firstRowContainer.style.flexDirection = 'row';
                    firstRowContainer.style.gap = '2px';
                    firstRowContainer.style.marginBottom = '4px';
                    
                    const secondRowContainer = document.createElement('div');
                    secondRowContainer.style.display = 'flex';
                    secondRowContainer.style.flexDirection = 'row';
                    secondRowContainer.style.gap = '2px';
                    
                    // Calculate how many cards go in each row
                    const halfLength = Math.ceil(data.player3.length / 2);
                    
                    // Add cards to the first row
                    data.player3.slice(0, halfLength).forEach(card => {
                        const cardElement = createCardElement(card, false);
                        // Make the cards larger
                        const cardImg = cardElement.querySelector('img');
                        if (cardImg) {
                            cardImg.style.width = '40px';
                            cardImg.style.height = 'auto';
                        }
                        firstRowContainer.appendChild(cardElement);
                    });
                    
                    // Add cards to the second row
                    data.player3.slice(halfLength).forEach(card => {
                        const cardElement = createCardElement(card, false);
                        // Make the cards larger
                        const cardImg = cardElement.querySelector('img');
                        if (cardImg) {
                            cardImg.style.width = '40px';
                            cardImg.style.height = 'auto';
                        }
                        secondRowContainer.appendChild(cardElement);
                    });
                    
                    // Add both rows to the container
                    cardsContainer.appendChild(firstRowContainer);
                    cardsContainer.appendChild(secondRowContainer);
                    
                    player3Cards.appendChild(cardsContainer);
                    
                    // Add team information
                    const teamInfo = document.createElement('div');
                    teamInfo.textContent = `Team: ${gameState.otherPlayers[2].team}`;
                    teamInfo.style.marginTop = '5px';
                    teamInfo.style.fontWeight = 'bold';
                    
                    // Add color coding for teams
                    if (gameState.otherPlayers[2].team === 'RE') {
                        teamInfo.style.color = '#2ecc71'; // Green for RE
                    } else if (gameState.otherPlayers[2].team === 'KONTRA') {
                        teamInfo.style.color = '#e74c3c'; // Red for KONTRA
                    }
                    
                    player3Cards.appendChild(teamInfo);
                }
                
                // Change the button text to indicate that hands are revealed
                const revealAIHandsBtn = document.getElementById('reveal-ai-hands-btn');
                if (revealAIHandsBtn) {
                    revealAIHandsBtn.textContent = 'Refresh AI Hands';
                }
            })
            .catch(error => {
                console.error('Error revealing AI hands:', error);
                alert(`Error: ${error.message}`);
            });
    }
    
    // Fetch model info from the server
    fetch('/model_info')
        .then(response => response.json())
        .then(data => {
            MODEL_PATH = data.model_path || 'the server';
            console.log("Using model:", MODEL_PATH);
        })
        .catch(error => console.error('Error fetching model info:', error));
});
