import random
import json
import os
import time

class GameManager:
    def __init__(self, data_path):
        self.rooms = {}
        self.cards = self.load_cards(data_path)

    def load_cards(self, data_path):
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
            cards = []
            for country, players in data.items():
                for player in players:
                    player['country'] = country
                    cards.append(player)
            return cards
        except Exception as e:
            print(f"Error loading cards: {e}")
            return []

    def create_room(self, room_id):
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                'players': {},
                'current_turn': None,
                'state': 'waiting', # waiting, drafting, playing, finished
                'deck': [],
                'selected_nations': set()
            }
        return self.rooms[room_id]

    def set_nations(self, room_id, nations):
        if room_id in self.rooms and not self.rooms[room_id]['selected_nations']:
            self.rooms[room_id]['selected_nations'] = set(nations)
            # Filter the deck based on selected nations
            filtered_cards = [card for card in self.cards if card.get('country') in self.rooms[room_id]['selected_nations']]
            # Fallback if no nations matched effectively (shouldn't happen with correct names)
            if not filtered_cards:
                filtered_cards = self.cards
            self.rooms[room_id]['deck'] = random.sample(filtered_cards, min(len(filtered_cards), 60))

    def join_room(self, room_id, player_id, player_name):
        room = self.rooms.get(room_id)
        if not room:
            room = self.create_room(room_id)
        
        if len(room['players']) >= 2:
            return False, "Room is full"
            
        room['players'][player_id] = {
            'name': player_name,
            'hand': [],
            'score': 0
        }
        
        if len(room['players']) == 2:
            self.start_game(room_id)
            
        return True, "Joined successfully"

    def remove_player(self, player_id):
        # Find which room the player was in and remove them
        for room_id, room in self.rooms.items():
            if player_id in room['players']:
                name = room['players'][player_id]['name']
                del room['players'][player_id]
                # If room is now empty, delete it completely so it resets
                if len(room['players']) == 0:
                    del self.rooms[room_id]
                else:
                    room['state'] = 'waiting' # Reset to waiting if someone leaves
                return room_id, name
        return None, None

    def start_game(self, room_id):
        room = self.rooms[room_id]
        room['state'] = 'drafting'
        room['draft_start_time'] = time.time()
        
        # Distribute 11 cards exact if possible
        pids = list(room['players'].keys())
        cards_per_player = min(11, len(room['deck']) // 2)
        
        room['players'][pids[0]]['hand'] = room['deck'][:cards_per_player]
        room['players'][pids[1]]['hand'] = room['deck'][cards_per_player:cards_per_player*2]
        
        # Remove dealt cards from main deck so they can be replenished later
        room['deck'] = room['deck'][cards_per_player*2:]
        
        room['players'][pids[0]]['accepted_hand'] = False
        room['players'][pids[1]]['accepted_hand'] = False
        room['current_turn'] = pids[0]

    def redraw_hand(self, room_id, player_id):
        room = self.rooms.get(room_id)
        if not room or room['state'] != 'drafting':
            return False, "Not in drafting phase"
            
        player = room['players'].get(player_id)
        if not player or player.get('accepted_hand'):
            return False, "Hand already accepted"
            
        # Return cards to deck and shuffle
        room['deck'].extend(player['hand'])
        random.shuffle(room['deck'])
        
        # Draw new 11
        cards_amount = min(11, len(room['deck']))
        player['hand'] = room['deck'][:cards_amount]
        room['deck'] = room['deck'][cards_amount:]
        return True, "Hand redrawn"

    def accept_hand(self, room_id, player_id):
        room = self.rooms.get(room_id)
        if not room or room['state'] != 'drafting':
            return False, "Not in drafting phase"
            
        player = room['players'].get(player_id)
        if not player:
            return False, "Player not found"
            
        player['accepted_hand'] = True
        
        # Check if both accepted
        all_accepted = all(p.get('accepted_hand') for p in room['players'].values())
        if all_accepted:
            room['state'] = 'playing'
            return True, "Both accepted, starting game"
            
        return True, "Hand accepted, waiting for opponent"

    def make_move(self, room_id, player_id, stat_category, stat_name):
        room = self.rooms.get(room_id)
        if not room or room['state'] != 'playing':
            return False, "Game is not active"
            
        if room['current_turn'] != player_id:
            return False, "Not your turn"
            
        pids = list(room['players'].keys())
        opponent_id = pids[1] if pids[0] == player_id else pids[0]
        
        p1_card = room['players'][player_id]['hand'][0]
        p2_card = room['players'][opponent_id]['hand'][0]
        
        p1_val = self.extract_stat(p1_card, stat_category, stat_name)
        p2_val = self.extract_stat(p2_card, stat_category, stat_name)
        
        winner_id = None
        # Logic for 'highest wins' or 'lowest wins'. Assume all stats here are 'highest wins' except Economy
        if stat_name in ['Economy / Eco. Rate']:
            if p1_val < p2_val:
                winner_id = player_id
            elif p2_val < p1_val:
                winner_id = opponent_id
        else:
            if p1_val > p2_val:
                winner_id = player_id
            elif p2_val > p1_val:
                winner_id = opponent_id
                
        # If tie, let's give cards back (bottom of deck) or discard?
        # Standard rules: winner takes both cards
        if winner_id == player_id:
            room['players'][player_id]['hand'].append(room['players'][opponent_id]['hand'].pop(0))
            room['players'][player_id]['hand'].append(room['players'][player_id]['hand'].pop(0))
            room['current_turn'] = player_id
            result_msg = f"{room['players'][player_id]['name']} won the round!"
        elif winner_id == opponent_id:
            room['players'][opponent_id]['hand'].append(room['players'][player_id]['hand'].pop(0))
            room['players'][opponent_id]['hand'].append(room['players'][opponent_id]['hand'].pop(0))
            room['current_turn'] = opponent_id
            result_msg = f"{room['players'][opponent_id]['name']} won the round!"
        else:
            # Tie - burn cards by moving them to the bottom of the deck
            room['players'][player_id]['hand'].append(room['players'][player_id]['hand'].pop(0))
            room['players'][opponent_id]['hand'].append(room['players'][opponent_id]['hand'].pop(0))
            result_msg = "Round tied! Cards moved to bottom."
            
        # Check game over
        if len(room['players'][player_id]['hand']) == 0:
            room['state'] = 'finished'
            return True, f"Game Over! {room['players'][opponent_id]['name']} wins the game!"
        elif len(room['players'][opponent_id]['hand']) == 0:
            room['state'] = 'finished'
            return True, f"Game Over! {room['players'][player_id]['name']} wins the game!"
            
        return True, result_msg
        
    def extract_stat(self, card, category, stat_name):
        try:
            val = card['stats'].get(category, {}).get(stat_name, 0)
            if val is None:
                return 0
            # Some stats are strings like "3/17", clean them if necessary. But mostly we compare numbers for Top Trumps.
            # Best Bowling is string. We should avoid it or parse it. For now, float conversion.
            if isinstance(val, str):
                if "/" in val:
                    parts = val.split('/')
                    return float(parts[0]) # just use wickets part for best bowling if chosen
            return float(val)
        except:
            return 0
