// Test script to simulate a Doppelkopf game and verify team display and score calculation
// This script simulates the game logic without using the GUI

// Mock game state
let gameState = {
    gameId: "test-game-123",
    currentPlayer: 0,
    playerTeam: "RE",
    gameVariant: "NORMAL",
    hand: [],
    currentTrick: [],
    legalActions: [],
    scores: [120, 120], // Example scores for RE and CONTRA
    gameOver: false,
    winner: null,
    revealed_team: false,
    revealed_teams: [false, false, false, false],
    player_team_type: '',
    player_team_types: ['', '', '', ''],
    otherPlayers: [
        { id: 1, team: "CONTRA", card_count: 10, score: 0, revealed_team: false },
        { id: 2, team: "RE", card_count: 10, score: 0, revealed_team: false },
        { id: 3, team: "CONTRA", card_count: 10, score: 0, revealed_team: false }
    ]
};

// Mock cards
const mockCards = {
    queenOfClubs: { id: "QC1", rank: "QUEEN", suit: "CLUBS", is_second: false },
    aceOfSpades: { id: "AS1", rank: "ACE", suit: "SPADES", is_second: false },
    tenOfHearts: { id: "10H1", rank: "TEN", suit: "HEARTS", is_second: false },
    jackOfDiamonds: { id: "JD1", rank: "JACK", suit: "DIAMONDS", is_second: false }
};

// Test functions
function testTeamReveal() {
    console.log("=== Testing Team Reveal Logic ===");
    
    // Initial state - no teams revealed
    console.log("Initial state:");
    console.log("Player revealed team:", gameState.revealed_team);
    console.log("Player team type:", gameState.player_team_type);
    console.log("Other players revealed teams:", gameState.revealed_teams);
    console.log("Other players team types:", gameState.player_team_types);
    
    // Simulate player playing Queen of Clubs
    console.log("\nPlayer plays Queen of Clubs:");
    
    // This simulates the logic in playCard function
    gameState.revealed_team = true;
    gameState.player_team_type = 're';
    
    // Count how many "re" players we've identified
    let reCount = 1; // We just identified ourselves
    
    if (gameState.player_team_types) {
        for (let i = 0; i < gameState.player_team_types.length; i++) {
            if (gameState.player_team_types[i] === 're') {
                reCount++;
            }
        }
    }
    
    console.log("After player plays Queen of Clubs:");
    console.log("Player revealed team:", gameState.revealed_team);
    console.log("Player team type:", gameState.player_team_type);
    console.log("Other players revealed teams:", gameState.revealed_teams);
    console.log("Other players team types:", gameState.player_team_types);
    
    // Simulate AI player 2 playing Queen of Clubs
    console.log("\nAI Player 2 plays Queen of Clubs:");
    
    // This simulates the logic in renderCurrentTrick function
    const playerIdx = 2;
    
    // Initialize the revealed_teams array if it doesn't exist
    if (!gameState.revealed_teams) {
        gameState.revealed_teams = [false, false, false, false];
        gameState.player_team_types = ['', '', '', ''];
    }
    
    gameState.revealed_teams[playerIdx] = true;
    gameState.player_team_types[playerIdx] = 're';
    
    // Count how many "re" players we've identified
    reCount = 0;
    if (gameState.player_team_type === 're') {
        reCount++;
    }
    
    if (gameState.player_team_types) {
        for (let i = 0; i < gameState.player_team_types.length; i++) {
            if (gameState.player_team_types[i] === 're') {
                reCount++;
            }
        }
    }
    
    // If we've identified both "re" players, mark the others as "contra"
    if (reCount === 2) {
        // For the human player
        if (gameState.player_team_type !== 're') {
            gameState.revealed_team = true;
            gameState.player_team_type = 'contra';
        }
        
        // For AI players
        if (gameState.player_team_types) {
            for (let i = 0; i < gameState.player_team_types.length; i++) {
                if (gameState.player_team_types[i] !== 're') {
                    gameState.revealed_teams[i] = true;
                    gameState.player_team_types[i] = 'contra';
                }
            }
        }
    }
    
    console.log("After AI player 2 plays Queen of Clubs:");
    console.log("Player revealed team:", gameState.revealed_team);
    console.log("Player team type:", gameState.player_team_type);
    console.log("Other players revealed teams:", gameState.revealed_teams);
    console.log("Other players team types:", gameState.player_team_types);
    
    // Verify that all teams are now revealed
    const allTeamsRevealed = gameState.revealed_team && 
                            gameState.revealed_teams.every(revealed => revealed);
    
    console.log("\nAll teams revealed:", allTeamsRevealed);
    
    // Verify that we have 2 re players and 2 contra players
    // Note: We need to be careful about double-counting the player
    let rePlayerCount = 0;
    let contraPlayerCount = 0;
    
    // Count the human player
    if (gameState.player_team_type === 're') {
        rePlayerCount++;
    } else if (gameState.player_team_type === 'contra') {
        contraPlayerCount++;
    }
    
    // Count the AI players (only the first 3 since we have 4 players total)
    for (let i = 1; i <= 3; i++) {
        if (gameState.player_team_types[i] === 're') {
            rePlayerCount++;
        } else if (gameState.player_team_types[i] === 'contra') {
            contraPlayerCount++;
        }
    }
    
    console.log("Re player count:", rePlayerCount);
    console.log("Contra player count:", contraPlayerCount);
    
    return rePlayerCount === 2 && contraPlayerCount === 2;
}

function testScoreCalculation() {
    console.log("\n=== Testing Score Calculation Logic ===");
    
    // Set up game over state
    gameState.gameOver = true;
    gameState.winner = "RE"; // RE team wins
    
    // Calculate the points for each player based on the winner
    const winningTeam = gameState.winner;
    const pointsPerPlayer = 2; // +2 for winners, -2 for losers
    
    // Calculate scores for each player
    const playerScores = [];
    
    // For player 0 (human player)
    const playerTeam = gameState.playerTeam;
    const playerPoints = playerTeam === winningTeam ? pointsPerPlayer : -pointsPerPlayer;
    playerScores.push({ id: 0, team: playerTeam, points: playerPoints });
    
    // For AI players
    for (let i = 0; i < gameState.otherPlayers.length; i++) {
        const player = gameState.otherPlayers[i];
        const points = player.team === winningTeam ? pointsPerPlayer : -pointsPerPlayer;
        playerScores.push({ id: player.id, team: player.team, points: points });
    }
    
    // Log the results
    console.log("Game over, winning team:", winningTeam);
    console.log("Player scores:");
    playerScores.forEach(player => {
        console.log(`Player ${player.id} (${player.team}): ${player.points} points`);
    });
    
    // Verify that we have 2 players with +2 points and 2 players with -2 points
    const winnersCount = playerScores.filter(player => player.points === pointsPerPlayer).length;
    const losersCount = playerScores.filter(player => player.points === -pointsPerPlayer).length;
    
    console.log("\nPlayers with +2 points:", winnersCount);
    console.log("Players with -2 points:", losersCount);
    
    return winnersCount === 2 && losersCount === 2;
}

// Run the tests
console.log("Starting Doppelkopf game logic tests...\n");

const teamRevealSuccess = testTeamReveal();
const scoreCalculationSuccess = testScoreCalculation();

console.log("\n=== Test Results ===");
console.log("Team reveal logic:", teamRevealSuccess ? "PASSED" : "FAILED");
console.log("Score calculation logic:", scoreCalculationSuccess ? "PASSED" : "FAILED");
console.log("All tests:", (teamRevealSuccess && scoreCalculationSuccess) ? "PASSED" : "FAILED");
