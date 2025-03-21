document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    const socket = io();
    
    // Store model path
    let MODEL_PATH = 'the server';
    
    // Game state
    let gameState = {
        game_id: null,
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
    if (hochzeitBtn) {
        hochzeitBtn.addEventListener('click', () => {
            // Only allow hochzeit if the player has two Queens of Clubs
            if (gameState.hasHochzeit) {
                setGameVariant('hochzeit');
            } else {
                console.log("Cannot select Hochzeit: Player does not have two Queens of Clubs");
                // Provide visual feedback to the user
                hochzeitBtn.classList.add('btn-error');
                setTimeout(() => {
                    hochzeitBtn.classList.remove('btn-error');
                }, 1000);
                // Optionally show a message to the user
                alert("You can only select Hochzeit (Marriage) if you have two Queens of Clubs");
            }
        });
    }
    if (queenSoloBtn) queenSoloBtn.addEventListener('click', () => setGameVariant('queen_solo'));
    if (jackSoloBtn) jackSoloBtn.addEventListener('click', () => setGameVariant('jack_solo'));
    if (fleshlessBtn) fleshlessBtn.addEventListener('click', () => setGameVariant('fleshless'));
    
    // Add event listener for King Solo button
    const kingSoloBtn = document.getElementById('king-solo-btn');
    if (kingSoloBtn) kingSoloBtn.addEventListener('click', () => setGameVariant('king_solo'));
    
    // Helper function to add announcement button event listeners
    function addAnnouncementButtonListener(buttonId, announcementType) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', () => makeAnnouncement(announcementType));
        }
    }
});
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
                if (gameState.game_id) {
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
            // Just clear the diamond_ace_captured flag without showing popups
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
        } else if (gameState.gameVariant === 'KING_SOLO') {
            // In King Solo, only Kings are trump
            return card.rank === 'KING';
        } else if (gameState.gameVariant === 'TRUMP_SOLO') {
            // In Trump Solo, all normal trumps are trump
            return card.suit === 'DIAMONDS' || card.rank === 'JACK' || card.rank === 'QUEEN';
        } else {
            // Normal game
            return card.suit === 'DIAMONDS' || card.rank === 'JACK' || card.rank === 'QUEEN' || 
                   (card.suit === 'HEARTS' && card.rank === 'TEN');
        }
    }
