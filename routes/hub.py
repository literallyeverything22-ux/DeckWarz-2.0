from flask import Blueprint, redirect, url_for

hub_bp = Blueprint('hub', __name__)

# The root "/" is handled by routes/game.py (deck selection page)
# This blueprint is kept for future API hub endpoints
