from flask import Flask
from flask_socketio import SocketIO
from game_logic import GameManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-cricket-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize GameManager with the merged dataset
data_path = os.path.join("data", "t20i_players_stats_merged.json")
game_manager = GameManager(data_path)

# Import and register Blueprints
from routes.hub import hub_bp
from routes.game import game_bp, register_socket_events

app.register_blueprint(hub_bp)
app.register_blueprint(game_bp)

# Register Socket.IO events for the game
register_socket_events(socketio, game_manager)

if __name__ =="__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
