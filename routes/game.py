from flask import Blueprint, render_template, request, jsonify
from flask_socketio import join_room, leave_room, emit
import json
import time
from pathlib import Path

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def index():
    return render_template('deck_selection.html')

@game_bp.route('/game')
def game():
    return render_template('game.html')

@game_bp.route('/api/generation-progress')
def generation_progress():
    MASTER_JSON_PATH = Path("data/t20i_players_stats_merged.json")
    if not MASTER_JSON_PATH.exists():
        return jsonify({"progress": 0, "total": 0, "generated": 0})
        
    try:
        with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        total_players = 0
        generated_images = 0
        
        for country, players in data.items():
            total_players += len(players)
            generated_images += sum(1 for p in players if 'image_url' in p and p['image_url'])
            
        progress = (generated_images / total_players * 100) if total_players > 0 else 0
        return jsonify({
            "progress": round(progress, 1),
            "total": total_players,
            "generated": generated_images
        })
    except Exception as e:
        return jsonify({"progress": 0, "total": 0, "generated": 0, "error": str(e)})

def register_socket_events(socketio, game_manager):
    @socketio.on('disconnect')
    def on_disconnect():
        room_id, player_name = game_manager.remove_player(request.sid)
        if room_id and player_name:
            emit('message', {'msg': f'{player_name} has disconnected (refreshing).'}, to=room_id)
            
    @socketio.on('join')
    def on_join(data):
        username = data.get('username')
        room_id = data.get('room')
        nations = data.get('nations', [])
        
        game_manager.create_room(room_id)
        if nations:
            game_manager.set_nations(room_id, nations)
            
        success, msg = game_manager.join_room(room_id, request.sid, username)
        if success:
            join_room(room_id)
            room = game_manager.rooms[room_id]
            emit('message', {'msg': f'{username} has entered the room.'}, to=room_id)
            
            # If game started, notify players
            if room['state'] == 'drafting':
                emit('game_started', {'msg': 'Drafting phase begun! Check your cards.'}, to=room_id)
                # Send drafting state to all players in room
                for pid, player in room['players'].items():
                    # Send only the countries of the cards in hand so they can decide
                    hand_countries = [c['country'] for c in player['hand']]
                    
                    # Gather opponent countries
                    opp_countries = []
                    for opid, oplayer in room['players'].items():
                        if opid != pid:
                            opp_countries = [c['country'] for c in oplayer['hand']]
                            break
                    # Pass the synchronized remaining time down
                    elapsed = time.time() - room.get('draft_start_time', time.time())
                    timer_remaining = max(0, 60 - int(elapsed))
                            
                    emit('draft_state', {
                        'hand_countries': hand_countries,
                        'opp_countries': opp_countries,
                        'timer_remaining': timer_remaining
                    }, to=pid)
            elif room['state'] == 'playing':
                emit('game_started', {'msg': 'Game is starting!'}, to=room_id)
                # Send initial state to all players in room
                for pid, player in room['players'].items():
                    p_hand = len(player['hand'])
                    p_top_card = player['hand'][0] if p_hand > 0 else None
                    hand_countries = [c['country'] for c in player['hand']]
                    
                    # Opponent info
                    opp_hand_size = 0
                    for opid, oplayer in room['players'].items():
                        if opid != pid:
                            opp_hand_size = len(oplayer['hand'])
                            break
                            
                    emit('update_state', {
                        'hand_size': p_hand, 
                        'opp_hand_size': opp_hand_size,
                        'top_card': p_top_card, 
                        'hand_countries': hand_countries,
                        'turn': room['current_turn'] == pid
                    }, to=pid)
        else:
            emit('error', {'msg': msg})

    @socketio.on('make_move')
    def on_move(data):
        room_id = data.get('room')
        stat_category = data.get('category')
        stat_name = data.get('stat')
        
        success, msg = game_manager.make_move(room_id, request.sid, stat_category, stat_name)
        
        if not success:
            emit('error', {'msg': msg})
            return
            
        room = game_manager.rooms[room_id]
        emit('message', {'msg': msg}, to=room_id)
        
        # Update state for all players
        for pid, player in room['players'].items():
            p_hand = len(player['hand'])
            p_top_card = player['hand'][0] if p_hand > 0 else None
            hand_countries = [c['country'] for c in player['hand']]
            
            # Opponent info
            opp_hand_size = 0
            for opid, oplayer in room['players'].items():
                if opid != pid:
                    opp_hand_size = len(oplayer['hand'])
                    break
                    
            emit('update_state', {
                'hand_size': p_hand, 
                'opp_hand_size': opp_hand_size,
                'top_card': p_top_card, 
                'hand_countries': hand_countries,
                'turn': room['current_turn'] == pid
            }, to=pid)
            
        if room['state'] == 'finished':
            emit('game_over', {'msg': msg}, to=room_id)

    @socketio.on('redraw_hand')
    def on_redraw(data):
        room_id = data.get('room')
        success, msg = game_manager.redraw_hand(room_id, request.sid)
        if success:
            room = game_manager.rooms[room_id]
            player = room['players'][request.sid]
            hand_countries = [c['country'] for c in player['hand']]
            
            # Opponent countries
            opp_countries = []
            for opid, oplayer in room['players'].items():
                if opid != request.sid:
                    opp_countries = [c['country'] for c in oplayer['hand']]
                    break
                    
            # Pass the synchronized remaining time down
            elapsed = time.time() - room.get('draft_start_time', time.time())
            timer_remaining = max(0, 60 - int(elapsed))
                    
            emit('draft_state', {
                'hand_countries': hand_countries,
                'opp_countries': opp_countries,
                'timer_remaining': timer_remaining
            }, to=request.sid)
        else:
            emit('error', {'msg': msg}, to=request.sid)

    @socketio.on('accept_hand')
    def on_accept(data):
        room_id = data.get('room')
        success, msg = game_manager.accept_hand(room_id, request.sid)
        if success:
            room = game_manager.rooms[room_id]
            if room['state'] == 'playing':
                emit('message', {'msg': 'Both players accepted! Battle begins!'}, to=room_id)
                # Send full state to start playing
                for pid, player in room['players'].items():
                    p_hand = len(player['hand'])
                    p_top_card = player['hand'][0] if p_hand > 0 else None
                    hand_countries = [c['country'] for c in player['hand']]
                    
                    # Opponent info
                    opp_hand_size = 0
                    for opid, oplayer in room['players'].items():
                        if opid != pid:
                            opp_hand_size = len(oplayer['hand'])
                            break
                            
                    emit('update_state', {
                        'hand_size': p_hand, 
                        'opp_hand_size': opp_hand_size,
                        'top_card': p_top_card, 
                        'hand_countries': hand_countries,
                        'turn': room['current_turn'] == pid
                    }, to=pid)
            else:
                emit('message', {'msg': f'{room["players"][request.sid]["name"]} accepted their hand. Waiting for opponent...'}, to=room_id)
        else:
            emit('error', {'msg': msg}, to=request.sid)
