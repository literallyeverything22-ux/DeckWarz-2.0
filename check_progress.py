import json
from pathlib import Path

MASTER_JSON_PATH = Path("data/t20i_players_stats_merged.json")

if not MASTER_JSON_PATH.exists():
    print("Master JSON not found.")
else:
    with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    total_players = 0
    generated_images = 0
    country_progress = {}
    
    for country, players in data.items():
        country_total = len(players)
        total_players += country_total
        country_generated = sum(1 for p in players if 'image_url' in p and p['image_url'])
        generated_images += country_generated
        
        if country_total > 0:
            country_progress[country] = f"{country_generated}/{country_total} ({(country_generated/country_total)*100:.1f}%)"
            
    print(f"\n--- AI Image Generation Progress ---")
    print(f"Total Players: {total_players}")
    print(f"Generated Portraits: {generated_images}")
    print(f"Progress: {(generated_images/total_players)*100:.1f}%\n")
    
    print("Breakdown by Country:")
    for country, prog in country_progress.items():
        if not prog.startswith("0/"):
            print(f"  - {country}: {prog}")
