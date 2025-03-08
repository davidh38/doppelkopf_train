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
    
    // Helper function to add announcement button event listeners
    function addAnnouncementButtonListener(buttonId, announcementType) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', () => makeAnnouncement(announcementType));
        }
    }
    
    // Add event listeners for all announcement buttons
    const announcementButtons = [
        { id: 're-btn', type: 're' },
        { id: 'contra-btn', type: 'contra' },
        { id: 'game-re-btn', type: 're' },
        { id: 'game-contra-btn', type: 'contra' },
        { id: 'no90-btn', type: 'no90' },
        { id: 'no60-btn', type: 'no60' },
        { id: 'no30-btn', type: 'no30' },
        { id: 'black-btn', type: 'black' },
        { id: 'game-no90-btn', type: 'no90' },
        { id: 'game-no60-btn', type: 'no60' },
        { id: 'game-no30-btn', type: 'no30' },
        { id: 'game-black-btn', type: 'black' }
    ];
    
    announcementButtons.forEach(button => {
        addAnnouncementButtonListener(button.id, button.type);
    });
    
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
            gameState.playerScores = data.player_scores || [0, 0, 0, 0];
            
            // Store player announcements if available
            if (data.announcements) {
                gameState.announcements = data.announcements;
            }
            
            // Store player variant selections if available
            if (data.player_variants) {
                gameState.playerVariants = data.player_variants;
            }
            
            // Store special tricks information if available
            if (data.diamond_ace_captured) {
                gameState.diamondAceCaptured = data.diamond_ace_captured;
            }
            
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
            
            // Make sure the game scores are visible
            const gameScores = document.getElementById('game-scores');
            if (gameScores) {
                gameScores.classList.remove('hidden');
            }
            
            // Update the game scores
            updateGameScores();
            
    // Check if the game is over
    if (data.game_over) {
        gameState.gameOver = true;
        gameState.winner = data.winner;
        
        // Make sure we have the game summary if available
        if (data.game_summary) {
            gameState.gameSummary = data.game_summary;
            console.log("Game summary received:", data.game_summary);
        }
        
        // Skip the modal and directly show the game over screen
        console.log("Game over detected, showing game over screen directly");
        showGameOverScreen();
    }
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
        
        // Get the current trick container
        const hardcodedTrickEl = document.getElementById('hardcoded-trick');
        if (!hardcodedTrickEl) return;
        
        // Set up the trick area as a relative positioning context
        const trickArea = document.querySelector('.trick-area');
        if (trickArea) {
            trickArea.style.position = 'relative';
            
            // Get the parent containers for each player
            const player1Container = player1Cards.parentElement;
            const player2Container = player2Cards.parentElement;
            const player3Container = player3Cards.parentElement;
            
            if (player1Container && player2Container && player3Container) {
                // Move the player containers out of the AI card visualization and into the trick area
                trickArea.appendChild(player1Container);
                trickArea.appendChild(player2Container);
                trickArea.appendChild(player3Container);
                
                // Style the containers to position them around the current trick
                // Position Player 2 above the current trick
                player2Container.style.position = 'absolute';
                player2Container.style.top = '40px'; // Position above the "Current Trick" heading
                player2Container.style.left = '50%';
                player2Container.style.transform = 'translateX(-50%)';
                player2Container.style.width = '80%'; // Reduced from 100% to center more
                player2Container.style.textAlign = 'center';
                player2Container.style.zIndex = '10';
                
                // Position Player 1 on the left side of the current trick
                player1Container.style.position = 'absolute';
                player1Container.style.left = '25px'; // Moved more to the center (was 10px)
                player1Container.style.top = '50%';
                player1Container.style.transform = 'translateY(-50%)';
                player1Container.style.zIndex = '10';
                
                // Position Player 3 on the right side of the current trick
                player3Container.style.position = 'absolute';
                player3Container.style.right = '25px'; // Moved more to the center (was 10px)
                player3Container.style.top = '50%';
                player3Container.style.transform = 'translateY(-50%)';
                player3Container.style.zIndex = '10';
                
                // Adjust the styling of the player containers
                player1Container.style.border = 'none';
                player2Container.style.border = 'none';
                player3Container.style.border = 'none';
                player1Container.style.background = 'transparent';
                player2Container.style.background = 'transparent';
                player3Container.style.background = 'transparent';
                
                // Hide the headings
                const headings = [player1Container, player2Container, player3Container].map(
                    container => container.querySelector('h5')
                );
                headings.forEach(heading => {
                    if (heading) heading.style.display = 'none';
                });
            }
        }
        
                // Create mock cards for AI players
                for (let i = 1; i <= 3; i++) {
                    const playerCardsEl = document.getElementById(`player${i}-cards`);
                    if (!playerCardsEl) continue;
                    
                    // Get the number of cards for this AI player
                    const cardCount = gameState.otherPlayers && gameState.otherPlayers[i-1] ? 
                                      gameState.otherPlayers[i-1].card_count : 10;
                    
                    // Create a container for the cards
                    const cardsContainer = document.createElement('div');
                    
                    // Set different layout for each player
                    if (i === 1 || i === 3) {
                        // Vertical layout for Players 1 and 3
                        cardsContainer.style.display = 'flex';
                        cardsContainer.style.flexDirection = 'column';
                        cardsContainer.style.gap = '2px';
                        cardsContainer.style.alignItems = 'center';
                    } else {
                        // Horizontal layout for Player 2
                        cardsContainer.style.display = 'flex';
                        cardsContainer.style.flexDirection = 'row';
                        cardsContainer.style.gap = '2px';
                        cardsContainer.style.justifyContent = 'center';
                    }
                    
                    // Create card back images
                    for (let j = 0; j < cardCount; j++) {
                        const cardImg = document.createElement('img');
                        cardImg.src = '/static/images/cards/back.png';
                        cardImg.alt = 'Card back';
                        cardImg.className = 'ai-card';
                        
                        if (i === 1 || i === 3) {
                            // Smaller cards for vertical layout
                            cardImg.style.width = '25px';
                            cardImg.style.height = 'auto';
                            cardImg.style.margin = '1px';
                        } else {
                            // Normal size for horizontal layout
                            cardImg.style.width = '30px';
                            cardImg.style.height = 'auto';
                            cardImg.style.margin = '2px';
                        }
                        
                        cardsContainer.appendChild(cardImg);
                    }
                    
                    playerCardsEl.appendChild(cardsContainer);
                    
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
                
                // Make sure the AI card visualization container is visible
                const aiCardVisualization = document.getElementById('ai-card-visualization');
                if (aiCardVisualization) {
                    aiCardVisualization.style.display = 'block';
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
        console.log("Rendering current trick, player turn:", gameState.currentPlayer === 0);
        
        // Get the hardcoded trick element
        const hardcodedTrickEl = document.getElementById('hardcoded-trick');
        if (!hardcodedTrickEl) return;
        
        // Clear the trick element
        hardcodedTrickEl.innerHTML = '';
        
        // Add a class to the trick element to enforce the grid layout
        hardcodedTrickEl.className = 'trick-grid';
        
        // ALWAYS set up the grid layout, even if there are no cards yet
        // This ensures the layout doesn't change when it's the user's turn
        // Force grid display with !important to override any other styles
        hardcodedTrickEl.style.cssText = `
            display: grid !important;
            grid-template-areas: 
                ".     top    ."
                "left  .      right"
                ".     bottom .";
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: 1fr 1fr 1fr;
            gap: 10px;
            width: 300px;
            height: 300px;
            margin: 0 auto;
            position: relative;
        `;
        
        // Calculate the starting player for this trick
        // Use ((n % m) + m) % m to ensure positive modulo result
        const startingPlayer = ((gameState.currentPlayer - gameState.currentTrick.length) % 4 + 4) % 4;
        
        // Create placeholders for all four positions
        const positions = [
            { position: "bottom", playerIdx: 0, gridArea: "bottom", justifySelf: "center" },
            { position: "left", playerIdx: 1, gridArea: "left", justifySelf: "start" },
            { position: "top", playerIdx: 2, gridArea: "top", justifySelf: "center" },
            { position: "right", playerIdx: 3, gridArea: "right", justifySelf: "end" }
        ];
        
        // Create a container for each position (whether there's a card or not)
        positions.forEach(pos => {
            // Create a container for the card and player label
            const cardContainer = document.createElement('div');
            cardContainer.className = 'trick-card-container';
            cardContainer.style.gridArea = pos.gridArea;
            cardContainer.style.justifySelf = pos.justifySelf;
            
            // Create a player label
            const playerLabel = document.createElement('div');
            playerLabel.className = 'player-label';
            playerLabel.textContent = pos.playerIdx === 0 ? 'You' : `Player ${pos.playerIdx}`;
            
            // Position the label based on the position
            if (pos.position === "bottom") {
                cardContainer.style.flexDirection = "column";
                playerLabel.style.order = "1"; // Label below card
            } else if (pos.position === "top") {
                cardContainer.style.flexDirection = "column";
                playerLabel.style.order = "-1"; // Label above card
            } else if (pos.position === "left") {
                cardContainer.style.flexDirection = "row";
                playerLabel.style.marginRight = "10px";
            } else if (pos.position === "right") {
                cardContainer.style.flexDirection = "row-reverse";
                playerLabel.style.marginLeft = "10px";
            }
            
            // Add the player label to the container
            cardContainer.appendChild(playerLabel);
            
            // Check if there's a card for this position
            const cardIndex = (4 + pos.playerIdx - startingPlayer) % 4;
            if (gameState.currentTrick && gameState.currentTrick.length > cardIndex) {
                const card = gameState.currentTrick[cardIndex];
                
                // Create the card element
                const cardElement = createCardElement(card, false); // Cards in the trick are not playable
                
                // No team information shown, just the player name
                playerLabel.textContent = pos.playerIdx === 0 ? 'You' : `Player ${pos.playerIdx}`;
                
                // Add the card to the container
                cardContainer.appendChild(cardElement);
            } else {
            // Add an empty placeholder for the card
            const emptyCard = document.createElement('div');
            emptyCard.style.width = '120px';
            emptyCard.style.height = '170px';
            emptyCard.style.visibility = 'hidden';
                cardContainer.appendChild(emptyCard);
            }
            
            // Add the container to the trick display
            hardcodedTrickEl.appendChild(cardContainer);
        });
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
                
                // Update announcement capabilities
                gameState.canAnnounceRe = data.state.can_announce_re || false;
                gameState.canAnnounceContra = data.state.can_announce_contra || false;
                gameState.canAnnounceNo90 = data.state.can_announce_no90 || false;
                gameState.canAnnounceNo60 = data.state.can_announce_no60 || false;
                gameState.canAnnounceNo30 = data.state.can_announce_no30 || false;
                gameState.canAnnounceBlack = data.state.can_announce_black || false;
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
            
            // Store the game summary if available
            if (data.game_summary) {
                gameState.gameSummary = data.game_summary;
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
                
                // Make sure the AI card visualization container is visible
                const aiCardVisualization = document.getElementById('ai-card-visualization');
                if (aiCardVisualization) {
                    aiCardVisualization.style.display = 'block';
                }
                
                // Clear previous content
                player1Cards.innerHTML = '';
                player2Cards.innerHTML = '';
                player3Cards.innerHTML = '';
                
                // Helper function to display AI player cards
                function displayAIPlayerCards(playerIndex, cards, container) {
                    if (!cards || cards.length === 0) return;
                    
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
                    const halfLength = Math.ceil(cards.length / 2);
                    
                    // Function to add cards to a row
                    const addCardsToRow = (rowContainer, cardsToAdd) => {
                        cardsToAdd.forEach(card => {
                            const cardElement = createCardElement(card, false);
                            // Make the cards larger
                            const cardImg = cardElement.querySelector('img');
                            if (cardImg) {
                                cardImg.style.width = '40px';
                                cardImg.style.height = 'auto';
                            }
                            rowContainer.appendChild(cardElement);
                        });
                    };
                    
                    // Add cards to both rows
                    addCardsToRow(firstRowContainer, cards.slice(0, halfLength));
                    addCardsToRow(secondRowContainer, cards.slice(halfLength));
                    
                    // Add both rows to the container
                    cardsContainer.appendChild(firstRowContainer);
                    cardsContainer.appendChild(secondRowContainer);
                    
                    container.appendChild(cardsContainer);
                    
                    // Add team information
                    const otherPlayerIndex = playerIndex - 1; // Convert from 1-based to 0-based index for otherPlayers array
                    if (gameState.otherPlayers && 
                        gameState.otherPlayers[otherPlayerIndex] && 
                        gameState.otherPlayers[otherPlayerIndex].team) {
                        
                        const team = gameState.otherPlayers[otherPlayerIndex].team;
                        
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
                        
                        container.appendChild(teamInfo);
                    }
                }
                
                // Display cards for each AI player
                displayAIPlayerCards(1, data.player1, player1Cards);
                displayAIPlayerCards(2, data.player2, player2Cards);
                displayAIPlayerCards(3, data.player3, player3Cards);
                
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
    
    // Function to update the game scores
    function updateGameScores() {
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
    
// Function to show the game over screen
function showGameOverScreen() {
    console.log("Showing game over screen");
    
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
            
            const winnerTeam = gameState.winner === 'RE' ? 'RE' : 'KONTRA';
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
            const finalMultiplierEl = document.getElementById('final-multiplier');
            
            if (finalReScoreEl) {
                finalReScoreEl.textContent = gameState.scores[0];
            }
            
            if (finalKontraScoreEl) {
                finalKontraScoreEl.textContent = gameState.scores[1];
            }
            
            if (finalMultiplierEl) {
                finalMultiplierEl.textContent = `${gameState.multiplier || 1}x`;
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
            
            // Update the player scores in the game over screen - showing game points instead of trick scores
            for (let i = 0; i < 4; i++) {
                const playerScoreEl = document.getElementById(`game-over-player-${i}-score`);
                if (playerScoreEl) {
                    const playerTeam = i === 0 ? gameState.playerTeam : 
                                      (gameState.otherPlayers && gameState.otherPlayers[i-1] ? 
                                       gameState.otherPlayers[i-1].team : '');
                    
                    // Determine if player is on winning team
                    const isWinningTeam = (gameState.winner === 'RE' && playerTeam === 'RE') || 
                                         (gameState.winner === 'KONTRA' && playerTeam === 'KONTRA');
                    
                    // Count players in each team
                    const rePlayers = gameState.otherPlayers ? 
                                     gameState.otherPlayers.filter(p => p.team === 'RE').length + 
                                     (gameState.playerTeam === 'RE' ? 1 : 0) : 
                                     (gameState.playerTeam === 'RE' ? 1 : 0);
                    
                    const kontraPlayers = gameState.otherPlayers ? 
                                         gameState.otherPlayers.filter(p => p.team === 'KONTRA').length + 
                                         (gameState.playerTeam === 'KONTRA' ? 1 : 0) : 
                                         (gameState.playerTeam === 'KONTRA' ? 1 : 0);
                    
                    // Calculate points based on winner and multiplier
                    let points = 0;
                    if (playerTeam === 'RE') {
                        // RE team: +kontraPlayers if won, -kontraPlayers if lost
                        points = isWinningTeam ? kontraPlayers : -kontraPlayers;
                    } else if (playerTeam === 'KONTRA') {
                        // KONTRA team: +rePlayers if won, -rePlayers if lost
                        points = isWinningTeam ? rePlayers : -rePlayers;
                    }
                    
                    // Apply multiplier
                    points *= (gameState.multiplier || 1);
                    
                    // Display the points with a + sign for positive values
                    playerScoreEl.textContent = points > 0 ? `+${points}` : points;
                    
                    // Add color coding for positive/negative points
                    playerScoreEl.style.color = points > 0 ? '#2ecc71' : (points < 0 ? '#e74c3c' : 'inherit');
                }
            }
            
            // Get the score calculation container
            const scoreCalculationEl = document.getElementById('score-calculation-details');
            if (scoreCalculationEl) {
                // Clear previous content
                scoreCalculationEl.innerHTML = '';
                
                // Create a detailed score breakdown
                const scoreBreakdown = document.createElement('div');
                scoreBreakdown.className = 'score-breakdown';
                
                // Format the score calculation based on the winner and announcements
                let basePoints = 1; // Start with 1 point for winning
                let scoreCalcHTML = '';
                
                // Count players in each team for point calculation
                const rePlayers = gameState.otherPlayers ? 
                                 gameState.otherPlayers.filter(p => p.team === 'RE').length + 
                                 (gameState.playerTeam === 'RE' ? 1 : 0) : 
                                 (gameState.playerTeam === 'RE' ? 1 : 0);
                
                const kontraPlayers = gameState.otherPlayers ? 
                                     gameState.otherPlayers.filter(p => p.team === 'KONTRA').length + 
                                     (gameState.playerTeam === 'KONTRA' ? 1 : 0) : 
                                     (gameState.playerTeam === 'KONTRA' ? 1 : 0);
                
                // Create a table for the score calculation
                const table = document.createElement('table');
                table.style.width = '100%';
                table.style.borderCollapse = 'collapse';
                table.style.marginBottom = '15px';
                
                // Add table header
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                
                const announcementHeader = document.createElement('th');
                announcementHeader.textContent = 'Announcement';
                announcementHeader.style.padding = '8px';
                announcementHeader.style.borderBottom = '2px solid #ddd';
                announcementHeader.style.textAlign = 'left';
                
                const pointsHeader = document.createElement('th');
                pointsHeader.textContent = 'Points';
                pointsHeader.style.padding = '8px';
                pointsHeader.style.borderBottom = '2px solid #ddd';
                pointsHeader.style.textAlign = 'right';
                
                headerRow.appendChild(announcementHeader);
                headerRow.appendChild(pointsHeader);
                thead.appendChild(headerRow);
                table.appendChild(thead);
                
                // Add table body
                const tbody = document.createElement('tbody');
                
                // Add base win row
                const baseRow = document.createElement('tr');
                
                const baseLabel = document.createElement('td');
                baseLabel.textContent = gameState.winner === 'RE' ? 'RE win' : 'KONTRA win';
                baseLabel.style.padding = '8px';
                baseLabel.style.borderBottom = '1px solid #eee';
                
                const basePointsCell = document.createElement('td');
                basePointsCell.textContent = '1 point';
                basePointsCell.style.padding = '8px';
                basePointsCell.style.borderBottom = '1px solid #eee';
                basePointsCell.style.textAlign = 'right';
                
                baseRow.appendChild(baseLabel);
                baseRow.appendChild(basePointsCell);
                tbody.appendChild(baseRow);
                
                // Add rows for announcements
                let totalPoints = 1; // Start with 1 for the win
                
                if (gameState.announcements) {
                    // Re/Contra announcement
                    if (gameState.announcements.re && gameState.winner === 'RE') {
                        const reRow = document.createElement('tr');
                        
                        const reLabel = document.createElement('td');
                        reLabel.textContent = 'RE announced';
                        reLabel.style.padding = '8px';
                        reLabel.style.borderBottom = '1px solid #eee';
                        
                        const rePoints = document.createElement('td');
                        rePoints.textContent = '1 point';
                        rePoints.style.padding = '8px';
                        rePoints.style.borderBottom = '1px solid #eee';
                        rePoints.style.textAlign = 'right';
                        
                        reRow.appendChild(reLabel);
                        reRow.appendChild(rePoints);
                        tbody.appendChild(reRow);
                        
                        totalPoints++;
                    }
                    
                    if (gameState.announcements.contra && gameState.winner === 'KONTRA') {
                        const contraRow = document.createElement('tr');
                        
                        const contraLabel = document.createElement('td');
                        contraLabel.textContent = 'CONTRA announced';
                        contraLabel.style.padding = '8px';
                        contraLabel.style.borderBottom = '1px solid #eee';
                        
                        const contraPoints = document.createElement('td');
                        contraPoints.textContent = '1 point';
                        contraPoints.style.padding = '8px';
                        contraPoints.style.borderBottom = '1px solid #eee';
                        contraPoints.style.textAlign = 'right';
                        
                        contraRow.appendChild(contraLabel);
                        contraRow.appendChild(contraPoints);
                        tbody.appendChild(contraRow);
                        
                        totalPoints++;
                    }
                    
                    // Additional announcements
                    if (gameState.announcements.no90) {
                        const no90Row = document.createElement('tr');
                        
                        const no90Label = document.createElement('td');
                        no90Label.textContent = 'No 90 announced';
                        no90Label.style.padding = '8px';
                        no90Label.style.borderBottom = '1px solid #eee';
                        
                        const no90Points = document.createElement('td');
                        no90Points.textContent = '1 point';
                        no90Points.style.padding = '8px';
                        no90Points.style.borderBottom = '1px solid #eee';
                        no90Points.style.textAlign = 'right';
                        
                        no90Row.appendChild(no90Label);
                        no90Row.appendChild(no90Points);
                        tbody.appendChild(no90Row);
                        
                        totalPoints++;
                    }
                    
                    if (gameState.announcements.no60) {
                        const no60Row = document.createElement('tr');
                        
                        const no60Label = document.createElement('td');
                        no60Label.textContent = 'No 60 announced';
                        no60Label.style.padding = '8px';
                        no60Label.style.borderBottom = '1px solid #eee';
                        
                        const no60Points = document.createElement('td');
                        no60Points.textContent = '1 point';
                        no60Points.style.padding = '8px';
                        no60Points.style.borderBottom = '1px solid #eee';
                        no60Points.style.textAlign = 'right';
                        
                        no60Row.appendChild(no60Label);
                        no60Row.appendChild(no60Points);
                        tbody.appendChild(no60Row);
                        
                        totalPoints++;
                    }
                    
                    if (gameState.announcements.no30) {
                        const no30Row = document.createElement('tr');
                        
                        const no30Label = document.createElement('td');
                        no30Label.textContent = 'No 30 announced';
                        no30Label.style.padding = '8px';
                        no30Label.style.borderBottom = '1px solid #eee';
                        
                        const no30Points = document.createElement('td');
                        no30Points.textContent = '1 point';
                        no30Points.style.padding = '8px';
                        no30Points.style.borderBottom = '1px solid #eee';
                        no30Points.style.textAlign = 'right';
                        
                        no30Row.appendChild(no30Label);
                        no30Row.appendChild(no30Points);
                        tbody.appendChild(no30Row);
                        
                        totalPoints++;
                    }
                    
                    if (gameState.announcements.black) {
                        const blackRow = document.createElement('tr');
                        
                        const blackLabel = document.createElement('td');
                        blackLabel.textContent = 'Black announced';
                        blackLabel.style.padding = '8px';
                        blackLabel.style.borderBottom = '1px solid #eee';
                        
                        const blackPoints = document.createElement('td');
                        blackPoints.textContent = '1 point';
                        blackPoints.style.padding = '8px';
                        blackPoints.style.borderBottom = '1px solid #eee';
                        blackPoints.style.textAlign = 'right';
                        
                        blackRow.appendChild(blackLabel);
                        blackRow.appendChild(blackPoints);
                        tbody.appendChild(blackRow);
                        
                        totalPoints++;
                    }
                }
                
                // Add total row
                const totalRow = document.createElement('tr');
                totalRow.style.fontWeight = 'bold';
                
                const totalLabel = document.createElement('td');
                totalLabel.textContent = 'Total base points';
                totalLabel.style.padding = '8px';
                totalLabel.style.borderTop = '2px solid #ddd';
                totalLabel.style.borderBottom = '1px solid #ddd';
                
                const totalValueCell = document.createElement('td');
                totalValueCell.textContent = `${totalPoints} point${totalPoints !== 1 ? 's' : ''}`;
                totalValueCell.style.padding = '8px';
                totalValueCell.style.borderTop = '2px solid #ddd';
                totalValueCell.style.borderBottom = '1px solid #ddd';
                totalValueCell.style.textAlign = 'right';
                
                totalRow.appendChild(totalLabel);
                totalRow.appendChild(totalValueCell);
                tbody.appendChild(totalRow);
                
                // Add multiplier row if applicable
                if (gameState.multiplier && gameState.multiplier > 1) {
                    const multiplierRow = document.createElement('tr');
                    multiplierRow.style.fontWeight = 'bold';
                    
                    const multiplierLabel = document.createElement('td');
                    multiplierLabel.textContent = 'Multiplier';
                    multiplierLabel.style.padding = '8px';
                    multiplierLabel.style.borderBottom = '1px solid #ddd';
                    
                    const multiplierValue = document.createElement('td');
                    multiplierValue.textContent = `${gameState.multiplier}x`;
                    multiplierValue.style.padding = '8px';
                    multiplierValue.style.borderBottom = '1px solid #ddd';
                    multiplierValue.style.textAlign = 'right';
                    
                    multiplierRow.appendChild(multiplierLabel);
                    multiplierRow.appendChild(multiplierValue);
                    tbody.appendChild(multiplierRow);
                }
                
                // Add final score row
                const finalRow = document.createElement('tr');
                finalRow.style.fontWeight = 'bold';
                finalRow.style.backgroundColor = '#f8f9fa';
                
                const finalLabel = document.createElement('td');
                finalLabel.textContent = 'Final points per player';
                finalLabel.style.padding = '8px';
                finalLabel.style.borderBottom = '1px solid #ddd';
                
                const finalValue = document.createElement('td');
                
                // Calculate final points per player
                let finalPoints = 0;
                if (gameState.winner === 'RE') {
                    // Each RE player gets +kontraPlayers points
                    finalPoints = kontraPlayers * (gameState.multiplier || 1);
                    finalValue.textContent = `+${finalPoints} for RE, -${finalPoints} for KONTRA`;
                } else {
                    // Each KONTRA player gets +rePlayers points
                    finalPoints = rePlayers * (gameState.multiplier || 1);
                    finalValue.textContent = `+${finalPoints} for KONTRA, -${finalPoints} for RE`;
                }
                
                finalValue.style.padding = '8px';
                finalValue.style.borderBottom = '1px solid #ddd';
                finalValue.style.textAlign = 'right';
                
                finalRow.appendChild(finalLabel);
                finalRow.appendChild(finalValue);
                tbody.appendChild(finalRow);
                
                table.appendChild(tbody);
                scoreBreakdown.appendChild(table);
                
                // Add the score breakdown to the score calculation container
                scoreCalculationEl.appendChild(scoreBreakdown);
                
                // Add player scores - showing game points instead of trick scores
                const playerScoresHeader = document.createElement('h3');
                playerScoresHeader.textContent = 'Player Game Points';
                scoreBreakdown.appendChild(playerScoresHeader);
                
                const playerScoresList = document.createElement('ul');
                playerScoresList.style.listStyleType = 'none';
                playerScoresList.style.padding = '0';
                
                // Calculate game points based on winner and multiplier
                const gamePoints = gameState.multiplier || 1;
                
                for (let i = 0; i < 4; i++) {
                    const playerScore = document.createElement('li');
                    const playerName = i === 0 ? 'You' : `Player ${i}`;
                    const playerTeam = gameState.otherPlayers && gameState.otherPlayers[i-1] ? 
                                      gameState.otherPlayers[i-1].team : (i === 0 ? gameState.playerTeam : '');
                    
                    // Determine if player is on winning team
                    const isWinningTeam = (gameState.winner === 'RE' && playerTeam === 'RE') || 
                                         (gameState.winner === 'KONTRA' && playerTeam === 'KONTRA');
                    
                    // Calculate points: positive for winners, negative for losers
                    const points = isWinningTeam ? gamePoints : -gamePoints;
                    const pointsDisplay = points > 0 ? `+${points}` : points;
                    
                    playerScore.textContent = `${playerName} (${playerTeam}): ${pointsDisplay} points`;
                    
                    // Add color coding for teams and points
                    if (points > 0) {
                        playerScore.style.color = '#2ecc71'; // Green for positive points
                    } else {
                        playerScore.style.color = '#e74c3c'; // Red for negative points
                    }
                    
                    playerScoresList.appendChild(playerScore);
                }
                
                scoreBreakdown.appendChild(playerScoresList);
                
                // Add trick scores section (original scores)
                if (gameState.playerScores && gameState.playerScores.length === 4) {
                    const trickScoresHeader = document.createElement('h3');
                    trickScoresHeader.textContent = 'Trick Scores';
                    trickScoresHeader.style.marginTop = '15px';
                    scoreBreakdown.appendChild(trickScoresHeader);
                    
                    const trickScoresList = document.createElement('ul');
                    trickScoresList.style.listStyleType = 'none';
                    trickScoresList.style.padding = '0';
                    
                    for (let i = 0; i < 4; i++) {
                        const trickScore = document.createElement('li');
                        const playerName = i === 0 ? 'You' : `Player ${i}`;
                        const playerTeam = gameState.otherPlayers && gameState.otherPlayers[i-1] ? 
                                          gameState.otherPlayers[i-1].team : (i === 0 ? gameState.playerTeam : '');
                        
                        trickScore.textContent = `${playerName} (${playerTeam}): ${gameState.playerScores[i]} trick points`;
                        
                        // Add color coding for teams
                        if (playerTeam === 'RE') {
                            trickScore.style.color = '#2ecc71'; // Green for RE
                        } else if (playerTeam === 'KONTRA') {
                            trickScore.style.color = '#e74c3c'; // Red for KONTRA
                        }
                        
                        trickScoresList.appendChild(trickScore);
                    }
                    
                    scoreBreakdown.appendChild(trickScoresList);
                }
                
                // Add announcements if any were made
                if (gameState.announcements && Object.keys(gameState.announcements).length > 0) {
                    const announcementsHeader = document.createElement('h3');
                    announcementsHeader.textContent = 'Announcements';
                    scoreBreakdown.appendChild(announcementsHeader);
                    
                    const announcementsList = document.createElement('ul');
                    announcementsList.style.listStyleType = 'none';
                    announcementsList.style.padding = '0';
                    
                    if (gameState.announcements.re) {
                        const reAnnouncement = document.createElement('li');
                        reAnnouncement.textContent = 'RE announced';
                        reAnnouncement.style.color = '#2ecc71'; // Green for RE
                        announcementsList.appendChild(reAnnouncement);
                    }
                    
                    if (gameState.announcements.contra) {
                        const contraAnnouncement = document.createElement('li');
                        contraAnnouncement.textContent = 'CONTRA announced';
                        contraAnnouncement.style.color = '#e74c3c'; // Red for KONTRA
                        announcementsList.appendChild(contraAnnouncement);
                    }
                    
                    if (gameState.announcements.no90) {
                        const no90Announcement = document.createElement('li');
                        no90Announcement.textContent = 'No 90 announced';
                        announcementsList.appendChild(no90Announcement);
                    }
                    
                    if (gameState.announcements.no60) {
                        const no60Announcement = document.createElement('li');
                        no60Announcement.textContent = 'No 60 announced';
                        announcementsList.appendChild(no60Announcement);
                    }
                    
                    if (gameState.announcements.no30) {
                        const no30Announcement = document.createElement('li');
                        no30Announcement.textContent = 'No 30 announced';
                        announcementsList.appendChild(no30Announcement);
                    }
                    
                    if (gameState.announcements.black) {
                        const blackAnnouncement = document.createElement('li');
                        blackAnnouncement.textContent = 'Black announced';
                        announcementsList.appendChild(blackAnnouncement);
                    }
                    
                    scoreBreakdown.appendChild(announcementsList);
                }
                
                // Add multiplier information
                if (gameState.multiplier && gameState.multiplier > 1) {
                    const multiplierInfo = document.createElement('p');
                    multiplierInfo.textContent = `Score Multiplier: ${gameState.multiplier}x`;
                    multiplierInfo.style.fontWeight = 'bold';
                    scoreBreakdown.appendChild(multiplierInfo);
                }
                
                // Add the score breakdown to the score calculation container
                scoreCalculationEl.appendChild(scoreBreakdown);
            }
            
            // Set up the play again button
            if (playAgainBtn) {
                playAgainBtn.addEventListener('click', () => {
                    // Hide the game over screen
                    gameOverScreen.classList.add('hidden');
                    
                    // Show the game setup screen
                    if (gameSetupScreen) {
                        gameSetupScreen.classList.remove('hidden');
                    }
                    
                    // Reset the game state
                    gameState = {
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
                        player_team_types: ['', '', '', ''],
                        announcements: {}, // Reset announcements
                        canAnnounceRe: false,
                        canAnnounceContra: false,
                        canAnnounceNo90: false,
                        canAnnounceNo60: false,
                        canAnnounceNo30: false,
                        canAnnounceBlack: false,
                        multiplier: 1
                    };
                    
                    // Start a new game
                    startNewGame();
                });
            }
        }
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
