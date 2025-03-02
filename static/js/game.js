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
    
    // Add event listener for the Show Last Trick button
    const showLastTrickBtn = document.getElementById('show-last-trick-btn');
    if (showLastTrickBtn) {
        showLastTrickBtn.addEventListener('click', showLastTrick);
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
                    
                    // Render the player's hand
                    renderHand();
                    
                    // Update turn indicator
                    updateTurnIndicator();
                }
                break;
        }
    });
    
    socket.on('trick_completed', function(data) {
        console.log('Trick completed:', data);
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
        const reBtn = document.getElementById('re-btn');
        const contraBtn = document.getElementById('contra-btn');
        const gameReBtn = document.getElementById('game-re-btn');
        const gameContraBtn = document.getElementById('game-contra-btn');
        
        // Get the announcement areas
        const announcementOptions = document.querySelector('.announcement-options');
        const gameAnnouncementArea = document.getElementById('game-announcement-area');
        
        // Update the Re button visibility
        if (reBtn) {
            reBtn.disabled = !gameState.canAnnounceRe;
            reBtn.style.opacity = gameState.canAnnounceRe ? '1' : '0.5';
        }
        
        if (gameReBtn) {
            gameReBtn.disabled = !gameState.canAnnounceRe;
            gameReBtn.style.opacity = gameState.canAnnounceRe ? '1' : '0.5';
        }
        
        // Update the Contra button visibility
        if (contraBtn) {
            contraBtn.disabled = !gameState.canAnnounceContra;
            contraBtn.style.opacity = gameState.canAnnounceContra ? '1' : '0.5';
        }
        
        if (gameContraBtn) {
            gameContraBtn.disabled = !gameState.canAnnounceContra;
            gameContraBtn.style.opacity = gameState.canAnnounceContra ? '1' : '0.5';
        }
        
        // Show/hide the announcement areas based on whether announcements are allowed
        if (announcementOptions) {
            announcementOptions.style.display = (gameState.canAnnounceRe || gameState.canAnnounceContra) ? 'block' : 'none';
        }
        
        if (gameAnnouncementArea) {
            gameAnnouncementArea.classList.toggle('hidden', !(gameState.canAnnounceRe || gameState.canAnnounceContra));
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
        
        // Update multiplier displays
        const multiplierEl = document.getElementById('multiplier');
        const gameMultiplierEl = document.getElementById('game-announcement-multiplier');
        
        if (multiplierEl) {
            multiplierEl.textContent = `${gameState.multiplier || 1}x`;
        }
        
        if (gameMultiplierEl) {
            gameMultiplierEl.textContent = `${gameState.multiplier || 1}x`;
        }
    }
    
    // Function to make an announcement (Re or Contra)
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
                
                // Update announcements
                if (!gameState.announcements) {
                    gameState.announcements = {};
                }
                
                if (announcement === 're') {
                    gameState.announcements.re = true;
                } else if (announcement === 'contra') {
                    gameState.announcements.contra = true;
                }
                
                // Update multiplier
                gameState.multiplier = data.multiplier || gameState.multiplier;
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
        
        if (!gameState.currentTrick || gameState.currentTrick.length === 0) {
            return;
        }
        
        // Create a container for each card with player information
        for (let i = 0; i < gameState.currentTrick.length; i++) {
            const card = gameState.currentTrick[i];
            
            // Create a container for the card and player label
            const cardContainer = document.createElement('div');
            cardContainer.className = 'trick-card-container';
            
            // Create the card element
            const cardElement = createCardElement(card, false); // Cards in the trick are not playable
            
            // Calculate which player played this card
            const startingPlayer = (gameState.currentPlayer - gameState.currentTrick.length) % 4;
            const playerIdx = (startingPlayer + i) % 4;
            
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
            
            // Add the player label and card to the container
            cardContainer.appendChild(playerLabel);
            cardContainer.appendChild(cardElement);
            
            // Add the container to the trick display
            hardcodedTrickEl.appendChild(cardContainer);
        }
        
        // Make sure the trick is visible
        hardcodedTrickEl.style.display = "flex";
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
    
    // Fetch model info from the server
    fetch('/model_info')
        .then(response => response.json())
        .then(data => {
            MODEL_PATH = data.model_path || 'the server';
            console.log("Using model:", MODEL_PATH);
        })
        .catch(error => console.error('Error fetching model info:', error));
});
