#!/usr/bin/env python3
"""
Flask web application for Doppelkopf card game.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask
from flask_socketio import SocketIO

from config import args, TEMPLATE_FOLDER, STATIC_FOLDER
from routes import register_routes
from socket_handlers import register_socket_handlers

# Configure Flask to find templates and static files in the frontend directory
app = Flask(__name__, 
            template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER)
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key
socketio = SocketIO(app)

# Register Socket.IO event handlers
register_socket_handlers(socketio)

# Register HTTP route handlers
register_routes(app, socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=args.port)
