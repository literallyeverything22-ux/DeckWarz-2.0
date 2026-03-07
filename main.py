from flask import Flask, jsonify, render_template
import scraper

app = Flask(__name__)

@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    player_data = scraper.get_player_profile(player_name)
    
    # If standard error is returned
    if "error" in player_data:
        return jsonify(player_data), 404
        
    return jsonify(player_data)

@app.route('/schedule')
def schedule():
    matches = scraper.get_schedule()
    
    if isinstance(matches, dict) and "error" in matches:
        return jsonify(matches), 500
        
    return jsonify(matches)


@app.route('/live')
def live_matches():
    live_data = scraper.get_live_matches()
    
    if isinstance(live_data, dict) and "error" in live_data:
        return jsonify(live_data), 500
        
    return jsonify(live_data)

@app.route('/')
def website():
    return render_template('index.html')

if __name__ =="__main__":
    app.run(debug=True)
