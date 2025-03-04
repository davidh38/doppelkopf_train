"""
Frontend routes module for the Doppelkopf game.

This module defines routes that handle frontend-related logic but are implemented
in the backend. These routes can be imported and used by the main backend app.
"""

from flask import Blueprint, render_template, jsonify, request, session
from flask_socketio import emit, join_room
from src.frontend.routes import Routes
from src.frontend.route_handlers import RouteHandlers

# Create a Blueprint for frontend routes
frontend_routes = Blueprint('frontend_routes', __name__)

@frontend_routes.route(Routes.INDEX)
def index():
    """Render the main game page."""
    return render_template('index.html')

# Variable to store the model path
_model_path = 'models/final_model.pt'

@frontend_routes.route(Routes.MODEL_INFO, methods=['GET'])
def model_info():
    """Get information about the model being used."""
    # Use the route handler from the frontend module
    return RouteHandlers.handle_model_info(_model_path)

def register_frontend_routes(app, socketio, model_path):
    """
    Register frontend routes with the Flask app.
    
    Args:
        app: The Flask application instance
        socketio: The SocketIO instance
        model_path: Path to the AI model
    """
    # Update the model path
    global _model_path
    _model_path = model_path
    
    # Register the blueprint with the app
    app.register_blueprint(frontend_routes)
    
    # Register socket.io event handlers
    @socketio.on(Routes.SOCKET_JOIN)
    def on_join(data):
        """Join a game room."""
        game_id = data.get('game_id')
        if game_id:
            print(f"Client joined game room: {game_id}")
            join_room(game_id)
    
    # Function to emit progress updates to clients
    def emit_progress_update(step, message, room=None):
        """
        Emit a progress update to clients.
        
        Args:
            step: The current step in the process
            message: A message describing the current step
            room: Optional room to emit to (if None, emits to all clients)
        """
        socketio.emit(Routes.SOCKET_PROGRESS_UPDATE, {
            'step': step,
            'message': message
        }, room=room)
    
    # Return the emit_progress_update function so it can be used by the main app
    return emit_progress_update
