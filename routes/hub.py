from flask import Blueprint, jsonify, render_template
import scraper

hub_bp = Blueprint('hub', __name__)

@hub_bp.route('/hub')
def index():
    return render_template('index.html')

@hub_bp.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    player_data = scraper.get_player_profile(player_name)
    if "error" in player_data:
        return jsonify(player_data), 404
    return jsonify(player_data)

@hub_bp.route('/schedule')
def schedule():
    matches = scraper.get_schedule()
    if isinstance(matches, dict) and "error" in matches:
        return jsonify(matches), 500
    return jsonify(matches)

@hub_bp.route('/live')
def live_matches():
    live_data = scraper.get_live_matches()
    if isinstance(live_data, dict) and "error" in live_data:
        return jsonify(live_data), 500
    return jsonify(live_data)
