import os
import json
import time
import requests
import io
from PIL import Image
from pathlib import Path

# List of fallback URLs to try when one gets rate-limited
API_URLS = [
    "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
    "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3.5-large-turbo",
    "https://router.huggingface.co/hf-inference/models/CompVis/stable-diffusion-v1-4"
]

current_api_index = 0
headers = {"Authorization": "Bearer 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"}

MASTER_JSON_PATH = Path("data/t20i_players_stats_merged.json")
OUTPUT_DIR = Path("static/images/players")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def query_hf(payload, url):
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.content

def generate_player_image(player_name, country):
    """Generates a hyper-realistic placeholder portrait for a player."""
    prompt = (
        f"A hyper-realistic dramatic portrait of professional cricket player {player_name} from {country}, "
        f"wearing an official {country} national cricket team jersey. Cinematic lighting, focused expression, "
        f"stadium background blurred, photorealistic, 8k resolution, highly detailed."
    )
    
    sanitized_name = "".join([c if c.isalnum() else "_" for c in player_name]).lower()
    filename = f"{sanitized_name}.jpg"
    filepath = OUTPUT_DIR / filename
    
    # Skip if already generated
    if filepath.exists():
        print(f"Skipping {player_name} (Image already exists)")
        return str(filepath.as_posix())

    print(f"Generating image for {player_name} ({country})...")
    
    global current_api_index
    max_retries = 3 * len(API_URLS) # Total attempts across all models
    
    for attempt in range(max_retries):
        current_url = API_URLS[current_api_index]
        model_name = current_url.split('/')[-1]
        
        try:
            image_bytes = query_hf({"inputs": prompt}, current_url)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize image to save space and fit card dimensions (e.g. 300x400)
            image = image.resize((300, 400), Image.Resampling.LANCZOS)
            
            image.save(filepath, format="JPEG", quality=85)
            print(f"[{model_name}] Success! Saved to {filepath}")
            # Be mindful of free-tier rate limits
            time.sleep(2) 
            return str(filepath.as_posix())
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited, seamlessly fall back to the next model in the list
                current_api_index = (current_api_index + 1) % len(API_URLS)
                next_model = API_URLS[current_api_index].split('/')[-1]
                print(f"[{model_name}] Rate limited! Swapping to fallback model -> [{next_model}]")
                time.sleep(2)
            elif e.response.status_code == 503:
                # Model is loading
                print(f"[{model_name}] Model is warming up, waiting 15s...")
                time.sleep(15)
            else:
                print(f"[{model_name}] HTTP Error for {player_name}: {e}")
                time.sleep(5)
        except Exception as e:
            print(f"[{model_name}] Generation failed for {player_name}: {str(e)}")
            time.sleep(5)
            
    print(f"Failed to generate image for {player_name} after {max_retries} attempts.")
    return None

def process_all_decks():
    print(f"Loading master file: {MASTER_JSON_PATH}")
    if not MASTER_JSON_PATH.exists():
        print("Master JSON not found.")
        return
        
    with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    updated = False
    
    # data is a dict of {country_name: [list of player dicts]}
    for country, players in data.items():
        print(f"\nProcessing Team: {country}")
        for player in players:
            # Look for Player Name
            name_keys = [k for k in player.keys() if "name" in k.lower()]
            if name_keys:
                player_name = str(player[name_keys[0]])
                
                # Check if we've already successfully bound an image URL for this player
                if 'image_url' in player and player['image_url']:
                    continue
                    
                img_path = generate_player_image(player_name, country)
                if img_path:
                    # Convert to web path relative to document root
                    player['image_url'] = "/" + img_path
                    updated = True
                    
                    # Save updated JSON back to disk incrementally so we don't lose progress
                    with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"Updated {MASTER_JSON_PATH.name} with new image URL for {player_name}.")

if __name__ == "__main__":
    process_all_decks()
