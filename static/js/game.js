document.addEventListener('DOMContentLoaded', function() {
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
        winner: null
    };
    
    // Polling interval for trick updates (in milliseconds)
    const POLLING_INTERVAL = 2000; // 2 seconds
    let pollingTimer = null;
    
    // DOM elements
    const gameSetupScreen = document.getElementById('game-setup');
    const variantSelectionScreen = document.getElementById('variant-selection');
    const gameBoard = document.getElementById('game-board');
    const gameOverScreen = document.getElementById('game-over');
    
    const newGameBtn = document.getElementById('new-game-btn');
    const normalBtn = document.getElementById('normal-btn');
    const hochzeitBtn = document.getElementById('hochzeit-btn');
    const queenSoloBtn = document.getElementById('queen-solo-btn');
    const jackSoloBtn = document.getElementById('jack-solo-btn');
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
    const lastTrickContainerEl = document.querySelector('.last-trick-container');
    const lastTrickEl = document.getElementById('last-trick');
    const trickWinnerEl = document.getElementById('trick-winner');
    
    const finalReScoreEl = document.getElementById('final-re-score');
    const finalKontraScoreEl = document.getElementById('final-kontra-score');
    const gameResultEl = document.getElementById('game-result');
    
    // Socket.io setup
    const socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('game_update', function(data) {
        updateGameState(data);
        renderGameState();
        
        // Also fetch the current trick data when the game state is updated via socket.io
        fetchCurrentTrickData();
    });
    
    socket.on('trick_completed', function(data) {
        const winner = data.winner;
        const isPlayer = data.is_player;
        const trickPoints = data.trick_points;
        
        // Show the completed trick
        showCompletedTrick(winner, isPlayer, trickPoints);
    });
    
    // Debug elements
    const debugTrickEl = document.getElementById('debug-trick');
    const debugBtn = document.getElementById('debug-btn');
    
    // Event listeners
    newGameBtn.addEventListener('click', startNewGame);
    normalBtn.addEventListener('click', () => setGameVariant('normal'));
    hochzeitBtn.addEventListener('click', () => setGameVariant('hochzeit'));
    queenSoloBtn.addEventListener('click', () => setGameVariant('queen_solo'));
    jackSoloBtn.addEventListener('click', () => setGameVariant('jack_solo'));
    playAgainBtn.addEventListener('click', resetGame);
    
    // Debug button event listener
    debugBtn.addEventListener('click', function() {
        // Fetch current trick data directly from the server
        fetch(`/get_current_trick?game_id=${gameState.gameId}`)
            .then(response => response.json())
            .then(data => {
                // Show raw trick data
                debugTrickEl.innerHTML = `
                    <p><strong>Current Trick:</strong> ${JSON.stringify(data.current_trick, null, 2)}</p>
                    <p><strong>Trick Players:</strong> ${JSON.stringify(data.trick_players, null, 2)}</p>
                    <p><strong>Current Player:</strong> ${data.current_player}</p>
                    <p><strong>Starting Player:</strong> ${data.starting_player}</p>
                `;
                
                // Update the game state with the new data
                gameState.currentTrick = data.current_trick;
                gameState.trick_players = data.trick_players;
                
                // Try to manually render the trick
                renderDebugTrick();
                
                // Also try to render the trick normally
                renderCurrentTrick();
            })
            .catch(error => {
                console.error('Error fetching current trick data:', error);
                debugTrickEl.innerHTML = `<p>Error fetching current trick data: ${error.message}</p>`;
            });
    });
    
    function renderDebugTrick() {
        // Clear the current trick area
        currentTrickEl.innerHTML = '';
        
        if (!gameState.currentTrick || gameState.currentTrick.length === 0) {
            currentTrickEl.innerHTML = '<p>No cards in current trick</p>';
            return;
        }
        
        // Create a simple table to display the cards
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginTop = '10px';
        
        // Create header row
        const headerRow = document.createElement('tr');
        const headers = ['Player', 'Card'];
        
        headers.forEach(headerText => {
            const header = document.createElement('th');
            header.textContent = headerText;
            header.style.border = '1px solid #ddd';
            header.style.padding = '8px';
            header.style.backgroundColor = '#f2f2f2';
            headerRow.appendChild(header);
        });
        
        table.appendChild(headerRow);
        
        // Add a row for each card in the trick
        gameState.currentTrick.forEach((card, index) => {
            const row = document.createElement('tr');
            
            // Player cell
            const playerCell = document.createElement('td');
            playerCell.style.border = '1px solid #ddd';
            playerCell.style.padding = '8px';
            
            let playerName = "Unknown";
            if (gameState.trick_players && gameState.trick_players[index]) {
                playerName = gameState.trick_players[index].name;
            } else if (index === 0) {
                playerName = "You";
            } else {
                playerName = `Player ${index}`;
            }
            
            playerCell.textContent = playerName;
            row.appendChild(playerCell);
            
            // Card cell
            const cardCell = document.createElement('td');
            cardCell.style.border = '1px solid #ddd';
            cardCell.style.padding = '8px';
            cardCell.textContent = `${card.rank} of ${card.suit}`;
            row.appendChild(cardCell);
            
            table.appendChild(row);
        });
        
        currentTrickEl.appendChild(table);
    }
    
    // Game functions
    function startNewGame() {
        fetch('/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            gameState.gameId = data.game_id;
            updateGameState(data.state);
            
            // Check if player has both Queens of Clubs for Hochzeit
            if (data.has_hochzeit) {
                hochzeitBtn.disabled = false;
            }
            
            // Render the player's hand in the variant selection screen
            renderVariantSelectionHand();
            
            // Show variant selection screen
            gameSetupScreen.classList.add('hidden');
            variantSelectionScreen.classList.remove('hidden');
        })
        .catch(error => console.error('Error starting new game:', error));
    }
    
    function renderVariantSelectionHand() {
        variantSelectionHandEl.innerHTML = '';
        
        // Sort the cards: trumps first, then clubs, spades, hearts
        // Note: We don't know the game variant yet, so we'll sort without considering trumps
        const sortedHand = [...gameState.hand].sort((a, b) => {
            // Sort by suit: Clubs, Spades, Hearts, Diamonds
            const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
            if (a.suit !== b.suit) {
                return suitOrder[a.suit] - suitOrder[b.suit];
            }
            
            // If same suit, sort by rank: Ace, 10, King, Queen, Jack, 9
            const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
            return rankOrder[a.rank] - rankOrder[b.rank];
        });
        
        // Render the sorted hand
        sortedHand.forEach(card => {
            const cardElement = createCardElement(card, false); // Cards are not playable in variant selection
            variantSelectionHandEl.appendChild(cardElement);
        });
    }
    
    function setGameVariant(variant) {
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
            updateGameState(data.state);
            renderGameState();
            
            // Show game board
            variantSelectionScreen.classList.add('hidden');
            gameBoard.classList.remove('hidden');
            
            // Start polling for trick updates
            startPolling();
        })
        .catch(error => console.error('Error setting game variant:', error));
    }
    
    // Start polling for trick updates
    function startPolling() {
        // Clear any existing timer
        if (pollingTimer) {
            clearInterval(pollingTimer);
        }
        
        // Set up a new timer to fetch trick data periodically
        pollingTimer = setInterval(() => {
            if (gameState.gameId) {
                fetchCurrentTrickData();
            }
        }, POLLING_INTERVAL);
        
        console.log("Started polling for trick updates");
    }
    
    // Stop polling
    function stopPolling() {
        if (pollingTimer) {
            clearInterval(pollingTimer);
            pollingTimer = null;
            console.log("Stopped polling for trick updates");
        }
    }
    
    function playCard(cardId) {
        console.log('Playing card:', cardId);
        
        // Find the card in the player's hand
        const playedCard = gameState.hand.find(card => card.id === cardId);
        if (!playedCard) {
            console.error('Card not found in hand:', cardId);
            return;
        }
        
        // Immediately remove the card from the hand in the UI
        const cardElement = document.querySelector(`[data-card-id="${cardId}"]`);
        if (cardElement) {
            cardElement.remove();
        }
        
        // Immediately update the game state to reflect the played card
        // Remove the card from the hand
        gameState.hand = gameState.hand.filter(card => card.id !== cardId);
        
        // Add the card to the current trick
        if (!gameState.currentTrick) {
            gameState.currentTrick = [];
        }
        
        // Add the card to the current trick with player info
        gameState.currentTrick.push(playedCard);
        
        // Update trick players if needed
        if (!gameState.trick_players) {
            gameState.trick_players = [];
        }
        
        // Add player info for the current player (you)
        gameState.trick_players.push({
            name: "You",
            idx: 0,
            is_current: false
        });
        
        // Immediately render the updated trick
        renderCurrentTrick();
        
        // Now make the server request
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
            updateGameState(data.state);
            renderGameState();
            
            // Automatically fetch the current trick data after playing a card
            fetchCurrentTrickData();
            
            // Check if a trick was completed
            if (data.trick_completed) {
                // Calculate points for the trick (this is a temporary solution until the server sends the points)
                const trickPoints = gameState.currentTrick.reduce((sum, card) => {
                    let points = 0;
                    if (card.rank === 'ACE') points = 11;
                    else if (card.rank === 'TEN') points = 10;
                    else if (card.rank === 'KING') points = 4;
                    else if (card.rank === 'QUEEN') points = 3;
                    else if (card.rank === 'JACK') points = 2;
                    return sum + points;
                }, 0);
                
                showCompletedTrick(data.trick_winner, data.is_player_winner, trickPoints);
            }
            
            // Check if game is over
            if (gameState.gameOver) {
                showGameOver();
            }
        })
        .catch(error => console.error('Error playing card:', error));
    }
    
    // Function to fetch current trick data from the server
    function fetchCurrentTrickData() {
        if (!gameState.gameId) return;
        
        fetch(`/get_current_trick?game_id=${gameState.gameId}`)
            .then(response => response.json())
            .then(data => {
                // Update the game state with the new data
                gameState.currentTrick = data.current_trick;
                gameState.trick_players = data.trick_players;
                
                // Render the current trick
                renderCurrentTrick();
            })
            .catch(error => {
                console.error('Error fetching current trick data:', error);
            });
    }
    
    function updateGameState(state) {
        if (!state) return;
        
        gameState.currentPlayer = state.current_player;
        gameState.playerTeam = state.player_team;
        gameState.gameVariant = state.game_variant;
        gameState.hand = state.hand || [];
        gameState.currentTrick = state.current_trick || [];
        gameState.trick_players = state.trick_players || [];
        gameState.legalActions = state.legal_actions || [];
        gameState.scores = state.scores || [0, 0];
        gameState.gameOver = state.game_over || false;
        gameState.winner = state.winner;
        gameState.otherPlayers = state.other_players || [];
        gameState.player_score = state.player_score || 0;
        gameState.last_trick_points = state.last_trick_points || 0;
        
        if (state.last_trick) {
            gameState.lastTrick = state.last_trick;
            gameState.trickWinner = state.trick_winner;
        }
        
        console.log("Updated game state:", gameState);
    }
    
    function renderGameState() {
        // Update game info
        playerTeamEl.textContent = gameState.playerTeam;
        gameVariantEl.textContent = gameState.gameVariant;
        reScoreEl.textContent = gameState.scores[0];
        kontraScoreEl.textContent = gameState.scores[1];
        
        // Update player score if available
        const playerScoreEl = document.getElementById('player-score');
        if (playerScoreEl && gameState.player_score !== undefined) {
            playerScoreEl.textContent = gameState.player_score;
        }
        
        // Update turn indicator
        if (gameState.currentPlayer === 0) {
            turnIndicatorEl.textContent = 'Your turn';
        } else {
            turnIndicatorEl.textContent = `Player ${gameState.currentPlayer}'s turn`;
        }
        
        // Render other players
        renderOtherPlayers();
        
        // Render player's hand
        renderHand();
        
        // Render current trick
        renderCurrentTrick();
        
        // Check if game is over
        if (gameState.gameOver) {
            showGameOver();
        }
    }
    
    function renderOtherPlayers() {
        otherPlayersEl.innerHTML = '';
        
        if (!gameState.otherPlayers || gameState.otherPlayers.length === 0) {
            return;
        }
        
        gameState.otherPlayers.forEach(player => {
            const playerBox = document.createElement('div');
            playerBox.className = 'player-box';
            
            // Add data attribute for CSS positioning
            playerBox.dataset.playerId = player.id;
            
            // Highlight current player
            if (player.is_current) {
                playerBox.classList.add('current-turn');
            }
            
            // Player info
            const playerInfo = document.createElement('div');
            playerInfo.className = 'player-info-text';
            playerInfo.innerHTML = `Player ${player.id}<br>Team: <span class="player-team">${player.team}</span><br>Cards: ${player.card_count}<br>Score: <span class="player-score">${player.score}</span>`;
            
            // Player cards (shown as backs)
            const playerCards = document.createElement('div');
            playerCards.className = 'player-cards';
            
            // Create card backs
            for (let i = 0; i < player.card_count; i++) {
                const cardBack = document.createElement('img');
                cardBack.className = 'card-back';
                cardBack.src = '/static/images/cards/back.png';
                cardBack.alt = 'Card back';
                playerCards.appendChild(cardBack);
            }
            
            playerBox.appendChild(playerInfo);
            playerBox.appendChild(playerCards);
            otherPlayersEl.appendChild(playerBox);
        });
    }
    
    function renderHand() {
        playerHandEl.innerHTML = '';
        
        // Sort the cards: trumps first, then clubs, spades, hearts
        const sortedHand = [...gameState.hand].sort((a, b) => {
            // First check if cards are trump
            const aIsTrump = isTrumpCard(a);
            const bIsTrump = isTrumpCard(b);
            
            if (aIsTrump && !bIsTrump) return -1;
            if (!aIsTrump && bIsTrump) return 1;
            
            // If both are trump or both are not trump, sort by suit
            if (aIsTrump && bIsTrump) {
                // Special case for Ten of Hearts - it's the highest trump
                const aIsTenOfHearts = a.rank === 'TEN' && a.suit === 'HEARTS';
                const bIsTenOfHearts = b.rank === 'TEN' && b.suit === 'HEARTS';
                
                // Ten of Hearts comes first (highest trump)
                if (aIsTenOfHearts && !bIsTenOfHearts) return -1;
                if (!aIsTenOfHearts && bIsTenOfHearts) return 1;
                
                // Then Queens
                if (a.rank === 'QUEEN' && b.rank !== 'QUEEN') return -1;
                if (a.rank !== 'QUEEN' && b.rank === 'QUEEN') return 1;
                
                // Then Jacks
                if (a.rank === 'JACK' && b.rank !== 'JACK') return -1;
                if (a.rank !== 'JACK' && b.rank === 'JACK') return 1;
                
                // If same rank, sort by suit: Clubs, Spades, Hearts, Diamonds
                if (a.rank === b.rank) {
                    const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
                    return suitOrder[a.suit] - suitOrder[b.suit];
                }
                
                // For diamond cards, sort by rank: Ace, 10, King
                if (a.suit === 'DIAMONDS' && b.suit === 'DIAMONDS') {
                    const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
                    return rankOrder[a.rank] - rankOrder[b.rank];
                }
                
                // Default sorting for other trump cards
                const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
                return rankOrder[a.rank] - rankOrder[b.rank];
            }
            
            // For non-trump cards, sort by suit: Clubs, Spades, Hearts
            const suitOrder = { 'CLUBS': 0, 'SPADES': 1, 'HEARTS': 2, 'DIAMONDS': 3 };
            if (a.suit !== b.suit) {
                return suitOrder[a.suit] - suitOrder[b.suit];
            }
            
            // If same suit, sort by rank: Ace, 10, King, Queen, Jack, 9
            const rankOrder = { 'ACE': 0, 'TEN': 1, 'KING': 2, 'QUEEN': 3, 'JACK': 4, 'NINE': 5 };
            return rankOrder[a.rank] - rankOrder[b.rank];
        });
        
        // Render the sorted hand
        sortedHand.forEach(card => {
            const isLegal = gameState.legalActions.some(action => 
                action.id === card.id
            );
            
            const cardElement = createCardElement(card, isLegal);
            
            if (isLegal && gameState.currentPlayer === 0) {
                cardElement.addEventListener('click', function() {
                    console.log('Playing card:', card.id);
                    playCard(card.id);
                });
            }
            
            playerHandEl.appendChild(cardElement);
        });
    }
    
    // Get the hardcoded trick element
    const hardcodedTrickEl = document.getElementById('hardcoded-trick');
    
    function renderCurrentTrick() {
        // Clear the hardcoded trick area
        hardcodedTrickEl.innerHTML = '';
        
        console.log("Current trick data:", gameState.currentTrick);
        console.log("Trick players:", gameState.trick_players);
        
        if (!gameState.currentTrick || gameState.currentTrick.length === 0) {
            console.log("No current trick data to render");
            hardcodedTrickEl.innerHTML = '<p>No cards in current trick</p>';
            return;
        }
        
        // ULTRA SIMPLE APPROACH - just render the cards directly with minimal styling
        for (let i = 0; i < gameState.currentTrick.length; i++) {
            const card = gameState.currentTrick[i];
            
            // Create a container for the card and player
            const container = document.createElement('div');
            container.style.textAlign = 'center';
            
            // Create player label
            const playerLabel = document.createElement('div');
            
            // Get player name
            let playerName = "Unknown";
            if (gameState.trick_players && gameState.trick_players[i]) {
                playerName = gameState.trick_players[i].name;
            } else if (i === 0) {
                playerName = "You";
            } else {
                playerName = `Player ${i}`;
            }
            
            playerLabel.textContent = playerName;
            playerLabel.style.fontWeight = 'bold';
            playerLabel.style.marginBottom = '5px';
            
            // Map card to filename
            let cardRank;
            switch(card.rank) {
                case 'ACE': cardRank = 'A'; break;
                case 'KING': cardRank = 'K'; break;
                case 'QUEEN': cardRank = 'Q'; break;
                case 'JACK': cardRank = 'J'; break;
                case 'TEN': cardRank = '0'; break;
                case 'NINE': cardRank = '9'; break;
                default: cardRank = card.rank;
            }
            
            let cardSuit;
            switch(card.suit) {
                case 'SPADES': cardSuit = 'S'; break;
                case 'HEARTS': cardSuit = 'H'; break;
                case 'DIAMONDS': cardSuit = 'D'; break;
                case 'CLUBS': cardSuit = 'C'; break;
                default: cardSuit = card.suit.charAt(0);
            }
            
            // Create card image
            const cardImg = document.createElement('img');
            cardImg.src = `/static/images/cards/${cardRank}${cardSuit}.png`;
            cardImg.alt = `${card.rank} of ${card.suit}`;
            cardImg.style.width = '120px';
            cardImg.style.height = '170px';
            cardImg.style.border = '2px solid #ddd';
            cardImg.style.borderRadius = '10px';
            
            // Add elements to container
            container.appendChild(playerLabel);
            container.appendChild(cardImg);
            
            // Add container to trick area
            hardcodedTrickEl.appendChild(container);
        }
    }
    
    function createCardElement(card, isPlayable) {
        const cardElement = document.createElement('div');
        cardElement.className = `card ${card.suit.toLowerCase()}`;
        
        if (!isPlayable) {
            cardElement.classList.add('disabled');
        }
        
        // Check if card is trump based on game variant
        const isTrump = isTrumpCard(card);
        if (isTrump) {
            cardElement.classList.add('trump');
        }
        
        // Map Doppelkopf card to standard card deck
        let cardRank;
        switch(card.rank) {
            case 'ACE': cardRank = 'A'; break;
            case 'KING': cardRank = 'K'; break;
            case 'QUEEN': cardRank = 'Q'; break;
            case 'JACK': cardRank = 'J'; break;
            case 'TEN': cardRank = '0'; break; // Note: 10 is represented as 0 in the filenames
            case 'NINE': cardRank = '9'; break;
            default: cardRank = card.rank;
        }
        
        let cardSuit;
        switch(card.suit) {
            case 'SPADES': cardSuit = 'S'; break;
            case 'HEARTS': cardSuit = 'H'; break;
            case 'DIAMONDS': cardSuit = 'D'; break;
            case 'CLUBS': cardSuit = 'C'; break;
            default: cardSuit = card.suit.charAt(0);
        }
        
        // Create the card image
        const cardImg = document.createElement('img');
        cardImg.className = 'card-image';
        cardImg.src = `/static/images/cards/${cardRank}${cardSuit}.png`;
        cardImg.alt = `${card.rank.toLowerCase()} of ${card.suit.toLowerCase()}`;
        
        cardElement.appendChild(cardImg);
        
        // Add a small indicator for second copy
        if (card.is_second) {
            const secondIndicator = document.createElement('div');
            secondIndicator.className = 'second-indicator';
            secondIndicator.textContent = '2';
            cardElement.appendChild(secondIndicator);
        }
        
        // Store the card ID as a data attribute for easier access
        cardElement.dataset.cardId = card.id;
        
        // Add a tooltip with card info
        const tooltip = document.createElement('div');
        tooltip.className = 'card-tooltip';
        tooltip.textContent = `${card.rank.charAt(0) + card.rank.slice(1).toLowerCase()} of ${card.suit.charAt(0) + card.suit.slice(1).toLowerCase()}${card.is_second ? ' (2)' : ''}`;
        cardElement.appendChild(tooltip);
        
        return cardElement;
    }
    
    function isTrumpCard(card) {
        const variant = gameState.gameVariant;
        
        if (variant === 'NORMAL' || variant === 'HOCHZEIT') {
            // Queens, Jacks, Diamonds, and Ten of Hearts are trump
            return card.rank === 'QUEEN' || 
                   card.rank === 'JACK' || 
                   card.suit === 'DIAMONDS' ||
                   (card.rank === 'TEN' && card.suit === 'HEARTS');
        } else if (variant === 'QUEEN_SOLO') {
            // Only Queens are trump
            return card.rank === 'QUEEN';
        } else if (variant === 'JACK_SOLO') {
            // Only Jacks are trump
            return card.rank === 'JACK';
        }
        
        return false;
    }
    
    function showCompletedTrick(winner, isPlayer, trickPoints) {
        console.log("Trick completed! Winner:", winner, "Is player:", isPlayer, "Points:", trickPoints);
        
        // ULTRA SIMPLE APPROACH: Just add a winner message to the current trick
        // The server will handle the delay and clearing the trick
        
        // Add a winner message to the current trick display
        const winnerMessage = document.createElement('div');
        winnerMessage.style.textAlign = 'center';
        winnerMessage.style.fontWeight = 'bold';
        winnerMessage.style.fontSize = '24px';
        winnerMessage.style.color = 'red';
        winnerMessage.style.marginTop = '20px';
        winnerMessage.style.padding = '10px';
        winnerMessage.style.backgroundColor = '#f8f9fa';
        winnerMessage.style.border = '2px solid red';
        winnerMessage.style.borderRadius = '5px';
        winnerMessage.textContent = isPlayer ? 
            `You won this trick! (${trickPoints} points)` : 
            `Player ${winner} won this trick (${trickPoints} points)`;
        
        // Add the winner message to the current trick display
        hardcodedTrickEl.appendChild(winnerMessage);
        
        // The server will handle the delay and clearing the trick
        // We don't need to do anything else here
    }
    
    function showGameOver() {
        // Stop polling for trick updates
        stopPolling();
        
        // Update final scores
        finalReScoreEl.textContent = gameState.scores[0];
        finalKontraScoreEl.textContent = gameState.scores[1];
        
        // Show game result
        const playerWon = (gameState.playerTeam === gameState.winner);
        gameResultEl.textContent = playerWon ? 
            'Congratulations! Your team won!' : 
            'Sorry, your team lost.';
        gameResultEl.style.color = playerWon ? '#27ae60' : '#e74c3c';
        
        // Show game over screen
        gameBoard.classList.add('hidden');
        gameOverScreen.classList.remove('hidden');
    }
    
    function resetGame() {
        // Stop polling if it's still active
        stopPolling();
        
        // Reset game state
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
            winner: null
        };
        
        // Reset UI
        hochzeitBtn.disabled = true;
        lastTrickContainerEl.classList.add('hidden');
        
        // Show setup screen
        gameOverScreen.classList.add('hidden');
        gameSetupScreen.classList.remove('hidden');
    }
});
