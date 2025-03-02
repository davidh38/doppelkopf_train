document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    const socket = io();
    
    // Store model path
    let MODEL_PATH = 'the server';
    
    // Fetch model info from the server
    fetch('/model_info')
        .then(response => response.json())
        .then(data => {
            MODEL_PATH = data.model_path || 'the server';
            console.log("Using model:", MODEL_PATH);
        })
        .catch(error => console.error('Error fetching model info:', error));
    
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
            
            console.log("Updated hand:", gameState.hand);
            console.log("Current trick:", gameState.currentTrick);
            console.log("Current player:", gameState.currentPlayer);
            console.log("Legal actions:", gameState.legalActions);
        }
        
        // Render the player's hand and current trick
        renderHand();
        renderCurrentTrick();
        
        // Update turn indicator
        updateTurnIndicator();
    });
    
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
                console.log("Model loaded successfully!");
                break;
            case 'model_loading_error':
            case 'model_loading_fallback':
                progressBarFill.style.width = '40%';
                progressMessage.style.color = "#e74c3c"; // Red color for error
                console.log("Error loading model:", data.message);
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
                
                // Show the variant selection screen if we have a game ID
                if (gameState.gameId) {
                    console.log("Game ready, showing variant selection screen");
                    
                    if (gameSetupScreen) {
                        console.log("Hiding game setup screen");
                        gameSetupScreen.classList.add('hidden');
                    }
                    
                    if (variantSelectionScreen) {
                        console.log("Showing variant selection screen");
                        variantSelectionScreen.classList.remove('hidden');
                    }
                    
                    // Render the player's hand in the variant selection screen
                    renderVariantSelectionHand();
                    
                // Log the game state to help debug
                console.log("Game state at game_ready:", gameState);
                console.log("Hand length:", gameState.hand ? gameState.hand.length : 0);
                
                // Force a new game request
                console.log("Making a new game request on game_ready event");
                fetch('/new_game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log("New game response:", data);
                    
                    gameState.gameId = data.game_id;
                    
                    // Join the Socket.IO room for this game
                    socket.emit('join', { game_id: gameState.gameId });
                    console.log("Joining room:", gameState.gameId);
                    
                    // Update game state with the response data
                    if (data.state) {
                        gameState.hand = data.state.hand || [];
                        gameState.currentPlayer = data.state.current_player;
                        gameState.playerTeam = data.state.player_team;
                        gameState.gameVariant = data.state.game_variant;
                        gameState.legalActions = data.state.legal_actions || [];
                        console.log("Player's hand:", gameState.hand);
                        console.log("Current player:", gameState.currentPlayer);
                        console.log("Legal actions:", gameState.legalActions);
                    }
                    
                    // Render the player's hand in the variant selection screen
                    renderVariantSelectionHand();
                    
                    // Show the variant selection screen
                    if (gameSetupScreen) {
                        console.log("Hiding game setup screen");
                        gameSetupScreen.classList.add('hidden');
                    }
                    
                    if (variantSelectionScreen) {
                        console.log("Showing variant selection screen");
                        variantSelectionScreen.classList.remove('hidden');
                    }
                })
                .catch(error => {
                    console.error('Error starting new game:', error);
                });
                }
                break;
        }
        
        // If there's an error, change the color
        if (data.step === 'model_loading_error') {
            progressMessage.style.color = "#e74c3c";
        }
    });
    
    socket.on('trick_completed', function(data) {
        console.log('Trick completed:', data);
        
        // Show a message about who won the trick
        const message = data.is_player ? 
            `You won the trick! (${data.trick_points} points)` : 
            `Player ${data.winner} won the trick (${data.trick_points} points)`;
        
        console.log(message);
    });
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
    const variantSelectionScreen = document.getElementById('variant-selection');
    const gameBoard = document.getElementById('game-board');
    const gameOverScreen = document.getElementById('game-over');
    
    console.log("DOM elements initialized:");
    console.log("gameSetupScreen:", gameSetupScreen);
    console.log("variantSelectionScreen:", variantSelectionScreen);
    console.log("gameBoard:", gameBoard);
    console.log("gameOverScreen:", gameOverScreen);
    
    const newGameBtn = document.getElementById('new-game-btn');
    const normalBtn = document.getElementById('normal-btn');
    const hochzeitBtn = document.getElementById('hochzeit-btn');
    const queenSoloBtn = document.getElementById('queen-solo-btn');
    const jackSoloBtn = document.getElementById('jack-solo-btn');
    const fleshlessBtn = document.getElementById('fleshless-btn');
    const playAgainBtn = document.getElementById('play-again-btn');
    
    const variantSelectionHandEl = document.getElementById('variant-selection-hand');
    
    const playerTeamEl = document.getElementById('player-team');
    const gameVariantEl = document.getElementById('game-variant');
    const reScoreEl = document.getElementById('re-score');
    const kontraScoreEl = document.getElementById('kontra-score');
    const turnIndicatorEl = document.getElementById('turn-indicator');
    
    const otherPlayersEl = document.getElementById('other-players');
    const playerHandEl = document.getElementById('player-hand');
    const currentTrickEl = document.getElementById('current-trick');
    
    // Event listeners
    newGameBtn.addEventListener('click', startNewGame);
    
    // Add event listeners for variant selection buttons
    if (normalBtn) normalBtn.addEventListener('click', () => setGameVariant('normal'));
    if (hochzeitBtn) hochzeitBtn.addEventListener('click', () => setGameVariant('hochzeit'));
    if (queenSoloBtn) queenSoloBtn.addEventListener('click', () => setGameVariant('queen_solo'));
    if (jackSoloBtn) jackSoloBtn.addEventListener('click', () => setGameVariant('jack_solo'));
    if (fleshlessBtn) fleshlessBtn.addEventListener('click', () => setGameVariant('fleshless'));
    
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
        console.log("Creating card element for:", card);
        
        const cardContainer = document.createElement('div');
        cardContainer.className = 'card-container';
        cardContainer.dataset.cardId = card.id;
        
        const cardElement = document.createElement('img');
        cardElement.className = 'card';
        
        // Use the card's suit and rank to determine the image path
        // Use the format without the blue "2" markers
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
        console.log("Card image src:", cardSrc);
        
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
    
    // Game functions
    function startNewGame() {
        console.log("Starting new game...");
        
        // Show progress container and hide the new game button
        const newGameBtn = document.getElementById('new-game-btn');
        const progressContainer = document.getElementById('progress-container');
        const progressBarFill = document.getElementById('progress-bar-fill');
        const progressMessage = document.getElementById('progress-message');
        
        if (newGameBtn) newGameBtn.classList.add('hidden');
        if (progressContainer) progressContainer.classList.remove('hidden');
        
        // Define progress steps
        const progressSteps = [
            { message: "Initializing game...", progress: 10 },
            { message: "Loading AI model...", progress: 30 },
            { message: "Shuffling cards...", progress: 50 },
            { message: "Dealing cards...", progress: 70 },
            { message: "Determining teams...", progress: 90 },
            { message: "Ready to play!", progress: 100 }
        ];
        
        // Function to update progress
        let currentStep = 0;
        function updateProgress() {
            if (currentStep < progressSteps.length) {
                const step = progressSteps[currentStep];
                progressMessage.textContent = step.message;
                progressBarFill.style.width = step.progress + '%';
                currentStep++;
                
                // If not the last step, schedule the next update
                if (currentStep < progressSteps.length) {
                    setTimeout(updateProgress, 500);
                } else {
                    // Last step - make the API call
                    makeNewGameRequest();
                }
            }
        }
        
        // Start the progress updates
        updateProgress();
        
        // Function to make the actual API request
        function makeNewGameRequest() {
            // Set a timeout for the API call
            const apiTimeout = setTimeout(() => {
                // If the API call takes too long, show a detailed message about what's happening
                progressMessage.textContent = "Game initialization is taking longer than expected. The server is currently:";
                progressMessage.style.color = "#e67e22";
                
                // Create a detailed explanation element
                const detailsElement = document.createElement('div');
                detailsElement.className = 'initialization-details';
                detailsElement.innerHTML = `
                    <ul>
                        <li>Creating a new game instance and shuffling cards</li>
                        <li>Loading the trained AI model from ${MODEL_PATH}</li>
                        <li>Dealing cards to all players and determining teams</li>
                        <li>Having AI players select their game variants</li>
                        <li>Preparing the initial game state</li>
                    </ul>
                    <p>This may take a few moments, especially if the AI model is large.</p>
                `;
                progressContainer.appendChild(detailsElement);
            }, 3000); // 3 seconds timeout
            
            // Add a retry button to the progress container
            const retryButton = document.createElement('button');
            retryButton.className = 'btn hidden';
            retryButton.textContent = 'Retry';
            retryButton.id = 'retry-button';
            retryButton.addEventListener('click', () => {
                // Hide the retry button
                retryButton.classList.add('hidden');
                // Reset the progress bar
                progressBarFill.style.width = '0%';
                // Start the progress updates again
                currentStep = 0;
                updateProgress();
            });
            progressContainer.appendChild(retryButton);
            
            fetch('/new_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                clearTimeout(apiTimeout);
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
                console.log("Joining room:", gameState.gameId);
                
                // Update game state with the response data
                if (data.state) {
                    gameState.hand = data.state.hand || [];
                    gameState.currentPlayer = data.state.current_player;
                    gameState.playerTeam = data.state.player_team;
                    gameState.gameVariant = data.state.game_variant;
                    gameState.legalActions = data.state.legal_actions || [];
                    console.log("Player's hand:", gameState.hand);
                    console.log("Current player:", gameState.currentPlayer);
                    console.log("Legal actions:", gameState.legalActions);
                }
                
                // Render the player's hand in the variant selection screen
                renderVariantSelectionHand();
                
                // Show the variant selection screen
                console.log("Showing variant selection screen");
                
                if (gameSetupScreen) {
                    console.log("Hiding game setup screen");
                    gameSetupScreen.classList.add('hidden');
                }
                
                if (variantSelectionScreen) {
                    console.log("Showing variant selection screen");
                    variantSelectionScreen.classList.remove('hidden');
                }
                
                // Update turn indicator
                updateTurnIndicator();
            })
            .catch(error => {
                clearTimeout(apiTimeout);
                console.error('Error starting new game:', error);
                
                // Show error message
                progressMessage.textContent = "Error starting game. Please try again.";
                progressMessage.style.color = "#e74c3c";
                
                // Show the retry button
                retryButton.classList.remove('hidden');
                
                // Show the new game button again
                if (newGameBtn) newGameBtn.classList.remove('hidden');
            });
        }
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
        .then(response => response.json())
        .then(data => {
            console.log("Set variant response:", data);
            
            // Update game state with the response data
            if (data.state) {
                gameState.hand = data.state.hand || [];
                gameState.gameVariant = data.state.game_variant;
                gameState.legalActions = data.state.legal_actions || [];
                console.log("Updated hand:", gameState.hand);
                console.log("Game variant:", gameState.gameVariant);
                console.log("Legal actions:", gameState.legalActions);
            }
            
            // Update current player
            if (data.state.current_player !== undefined) {
                gameState.currentPlayer = data.state.current_player;
            }
            
            // Check if the variant selection phase is over
            const variantSelectionPhase = data.variant_selection_phase !== undefined ? 
                data.variant_selection_phase : true;
            
            if (!variantSelectionPhase) {
                // Variant selection phase is over, show game board
                console.log("Variant selection phase is over, showing game board");
                console.log("variantSelectionScreen classes before hiding:", variantSelectionScreen ? variantSelectionScreen.className : "null");
                console.log("gameBoard classes before showing:", gameBoard ? gameBoard.className : "null");
                
                if (variantSelectionScreen) {
                    variantSelectionScreen.classList.add('hidden');
                    console.log("variantSelectionScreen classes after hiding:", variantSelectionScreen.className);
                }
                
                if (gameBoard) {
                    gameBoard.classList.remove('hidden');
                    gameBoard.style.display = "grid"; // Force grid display for game board
                    console.log("gameBoard classes after showing:", gameBoard.className);
                    console.log("Set gameBoard display style to grid");
                }
            } else {
                // Variant selection phase is still active
                console.log("Variant selection phase is still active, waiting for other players");
                
                // Update the variant selection screen to show the current player
                const variantSelectionStatusEl = document.getElementById('variant-selection-status');
                if (variantSelectionStatusEl) {
                    if (gameState.currentPlayer === 0) {
                        variantSelectionStatusEl.textContent = "Please select a game variant";
                    } else {
                        variantSelectionStatusEl.textContent = `Waiting for Player ${gameState.currentPlayer} to select a variant...`;
                    }
                }
            }
            
            // Render the player's hand
            renderHand();
            
            // Update turn indicator
            updateTurnIndicator();
        })
        .catch(error => console.error('Error setting game variant:', error));
    }
    
    function renderVariantSelectionHand() {
        console.log("Rendering variant selection hand...");
        
        if (!variantSelectionHandEl) {
            console.error("Variant selection hand element not found");
            return;
        }
        
        variantSelectionHandEl.innerHTML = '';
        
        // Sort the cards: trumps first, then clubs, spades, hearts
        const sortedHand = sortCards(gameState.hand);
        
        // Render the sorted hand
        sortedHand.forEach(card => {
            const cardElement = createCardElement(card, false); // Cards are not playable in variant selection
            variantSelectionHandEl.appendChild(cardElement);
        });
    }
    
    function renderHand() {
        console.log("Rendering hand...");
        console.log("Current player:", gameState.currentPlayer);
        console.log("Legal actions:", gameState.legalActions);
        
        if (!playerHandEl) {
            console.error("Player hand element not found");
            return;
        }
        
        playerHandEl.innerHTML = '';
        
        // Sort the cards: trumps first, then clubs, spades, hearts
        const sortedHand = sortCards(gameState.hand);
        
        // Debug: Log all legal action IDs
        const legalActionIds = gameState.legalActions.map(card => card.id);
        console.log("Legal action IDs:", legalActionIds);
        
        // Render the sorted hand
        sortedHand.forEach(card => {
            // Check if the card is in the legal actions
            const isPlayable = gameState.currentPlayer === 0 && 
                               gameState.legalActions.some(legalCard => legalCard.id === card.id);
            
            console.log(`Card ${card.id} playable: ${isPlayable}`);
            
            // Only make cards playable if they are legal moves
            const cardElement = createCardElement(card, isPlayable);
            playerHandEl.appendChild(cardElement);
        });
    }
    
    function renderCurrentTrick() {
        console.log("Rendering current trick...");
        console.log("Current trick:", gameState.currentTrick);
        
        // Get the hardcoded trick element
        const hardcodedTrickEl = document.getElementById('hardcoded-trick');
        if (!hardcodedTrickEl) {
            console.error("Hardcoded trick element not found");
            return;
        }
        
        // Clear the trick element
        hardcodedTrickEl.innerHTML = '';
        
        if (!gameState.currentTrick || gameState.currentTrick.length === 0) {
            console.log("No current trick to render");
            return;
        }
        
        console.log("Rendering current trick with " + gameState.currentTrick.length + " cards");
        
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
            playerLabel.textContent = playerIdx === 0 ? 'You' : `Player ${playerIdx}`;
            
            // Add the player label and card to the container
            cardContainer.appendChild(playerLabel);
            cardContainer.appendChild(cardElement);
            
            // Add the container to the trick display
            hardcodedTrickEl.appendChild(cardContainer);
        }
        
        // Make sure the trick is visible
        hardcodedTrickEl.style.display = "flex";
    }
    
    function playCard(cardId) {
        console.log('Playing card:', cardId);
        
        // Find the card in the hand
        const card = gameState.hand.find(c => c.id === cardId);
        if (!card) {
            console.error("Card not found in hand:", cardId);
            return;
        }
        
        console.log("Found card in hand:", card);
        
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
                console.log("Updated hand:", gameState.hand);
                console.log("Current trick:", gameState.currentTrick);
                console.log("Current player:", gameState.currentPlayer);
                console.log("Legal actions:", gameState.legalActions);
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
});
