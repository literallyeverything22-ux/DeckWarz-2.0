import json

def cleanup_missing_players():
    with open('t20i_players_stats.json', 'r', encoding='utf-8') as f:
        stats = json.load(f)
    with open('players names.json', 'r', encoding='utf-8') as f:
        players = json.load(f)
        
    players_to_remove = set()
    cleaned_stats = {}
    
    # Identify which players are completely blank or missing
    for country, p_list in players.items():
        stats_list = stats.get(country, [])
        stats_map = {s['name']: s for s in stats_list}
        
        for p in p_list:
            if p not in stats_map:
                players_to_remove.add((country, p))
            elif stats_map[p].get('profile_url', '') == 'debutant_or_not_found':
                players_to_remove.add((country, p))
                
    print(f"Total players identified for removal: {len(players_to_remove)}")
    for c, p in players_to_remove:
        print(f"- {p} ({c})")
        
    # Clean up stats JSON
    for country in stats.keys():
        cleaned_stats[country] = []
        for p in stats[country]:
            if (country, p['name']) not in players_to_remove:
                cleaned_stats[country].append(p)
                
    # Clean up players names JSON
    cleaned_names = {}
    for country, p_list in players.items():
        cleaned_names[country] = [p for p in p_list if (country, p) not in players_to_remove]
        
    with open('t20i_players_stats.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_stats, f, indent=4)
        
    with open('players names.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_names, f, indent=4)
        
    print("Cleanup complete.")
    
if __name__ == "__main__":
    cleanup_missing_players()
