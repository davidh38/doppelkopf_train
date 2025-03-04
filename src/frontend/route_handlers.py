"""
Route handlers module for the Doppelkopf game frontend.

This module defines route handler interfaces that can be used by both the frontend and backend components.
It serves as a bridge between the two, allowing for consistent handling of routes.
"""

from flask import jsonify

class RouteHandlers:
    """
    Class containing route handler interfaces that can be used by both frontend and backend.
    
    These methods define the interface for route handlers, but the actual implementation
    should be in the backend. The backend can import and use these interfaces to ensure
    consistent handling of routes.
    """
    
    @staticmethod
    def handle_model_info(model_path):
        """
        Handle the model info route.
        
        Args:
            model_path: Path to the AI model
            
        Returns:
            JSON response with model information
        """
        return jsonify({
            'model_path': model_path
        })
    
    @staticmethod
    def handle_hochzeit_check(hand):
        """
        Check if a player has both Queens of Clubs (hochzeit/marriage).
        
        This is a utility function that can be called by the backend to check
        if a player has both Queens of Clubs, which allows them to play the
        hochzeit (marriage) game variant.
        
        Args:
            hand: The player's hand of cards
            
        Returns:
            Boolean indicating if the player has both Queens of Clubs
        """
        # The actual implementation should be in the backend
        # This is just an interface definition
        pass
