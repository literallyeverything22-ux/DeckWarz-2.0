import json
import os

def load_json(filepath):
    if not os.path.exists(filepath): return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read().strip()
            return json.loads(data) if data else {}
    except:
        return {}

def main():
    with open("players names.json", "r", encoding="utf-8") as f:
        players_names = json.load(f)

    # Output from DuckDuckGo script (the ones that succeeded before rate limit)
    duck_data = load_json("t20i_players_stats_duck.json")
    
    # Output from Offline script
    offline_data = load_json("t20i_players_stats.json")
    
    final_output = {}
    total_found = 0
    total_requested = sum(len(set(players)) for players in players_names.values())
    
    for country, players in players_names.items():
        final_output[country] = []
        unique_players = list(dict.fromkeys(players))
        
        duck_country_players = duck_data.get(country, [])
        offline_country_players = offline_data.get(country, [])
        
        for player in unique_players:
            found = False
            
            # Check duck data
            for p in duck_country_players:
                if p.get("name") == player:
                    final_output[country].append(p)
                    found = True
                    break
                    
            if not found:
                # Check offline data
                for p in offline_country_players:
                    if p.get("name") == player:
                        final_output[country].append(p)
                        found = True
                        break
                        
            if found:
                total_found += 1
                
    with open("t20i_players_stats_final.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)
        
    print(f"Successfully merged data!")
    print(f"Total players successfully processed with T20I stats: {total_found} / {total_requested}")

if __name__ == "__main__":
    main()
