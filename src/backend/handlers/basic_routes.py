#!/usr/bin/env python3
"""
Basic route handlers for the Doppelkopf web application.
These include the main page and model information.
"""

from flask import render_template, jsonify
from src.backend.config import MODEL_PATH

def index():
    """Render the main game page."""
    return render_template('index.html')

def model_info():
    """Get information about the model being used."""
    return jsonify({
        'model_path': MODEL_PATH
    })
