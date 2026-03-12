import json
import urllib.request
import urllib.error
import urllib.parse
import random
import time
from pathlib import Path
from PIL import Image
import io

server_address = "127.0.0.1:8188"
OUTPUT_DIR = Path("static/images/players")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MASTER_JSON_PATH = Path("data/t20i_players_stats_merged.json")

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.URLError as e:
        print(f"Error connecting to ComfyUI at {server_address}. Is it running and listening on port 8188?")
        return None

def get_history(prompt_id):
    req = urllib.request.Request(f"http://{server_address}/history/{prompt_id}")
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.URLError:
        return {}

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    req = urllib.request.Request(f"http://{server_address}/view?{url_values}")
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except urllib.error.URLError:
        return None

def generate_player_image_local(player_name, country):
    prompt_text = (
        f"A hyper-realistic dramatic portrait of professional cricket player {player_name} from {country}, "
        f"wearing an official {country} national cricket team jersey. Cinematic lighting, focused expression, "
        f"stadium background blurred, photorealistic, 8k resolution, highly detailed."
    )

    sanitized_name = "".join([c if c.isalnum() else "_" for c in player_name]).lower()
    filename = f"{sanitized_name}.jpg"
    filepath = OUTPUT_DIR / filename

    if filepath.exists():
        print(f"Skipping {player_name} (Image already exists)")
        return str(filepath.as_posix())

    print(f"Generating image locally for {player_name} ({country})...")

    # Define the ComfyUI API JSON workflow
    workflow = {
        "3": {
            "inputs": {
                "seed": random.randint(1, 100000000000000),
                "steps": 20,
                "cfg": 1.0, # Flux typically uses 1.0 CFG
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "flux1-dev-fp8.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 768,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": prompt_text,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "text, watermark, ugly, low quality, deformed",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": sanitized_name,
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

    res = queue_prompt(workflow)
    if not res:
        return None

    prompt_id = res['prompt_id']
    print(f"[{prompt_id}] Queued to Local ComfyUI API! Waiting for generation...")

    # Poll history until it's done
    last_print = time.time()
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            # Done!
            out = history[prompt_id]['outputs']
            
            # Find the node that saved the image (node 9 in our workflow)
            for node_id in out:
                node_output = out[node_id]
                if 'images' in node_output:
                    # Get the first image
                    image_info = node_output['images'][0]
                    img_filename = image_info['filename']
                    img_subfolder = image_info['subfolder']
                    img_type = image_info['type']
                    
                    # Download the image from the ComfyUI server into memory
                    image_data = get_image(img_filename, img_subfolder, img_type)
                    if image_data:
                        img = Image.open(io.BytesIO(image_data)).convert("RGB")
                        # Resize to fit card dimensions (300x400)
                        img = img.resize((300, 400), Image.Resampling.LANCZOS)
                        img.save(filepath, format="JPEG", quality=85)
                        
                        print(f"Success! Saved to {filepath}")
                        return str(filepath.as_posix())
            break
            
        # Give UX feedback if it's taking a while
        if time.time() - last_print > 10:
            print("Still generating...")
            last_print = time.time()
            
        time.sleep(1.5)
        
    print(f"Failed to fetch image for {player_name}")
    return None

def process_all_decks():
    print(f"Loading master file: {MASTER_JSON_PATH}")
    if not MASTER_JSON_PATH.exists():
        print("Master JSON not found.")
        return
        
    with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for country, players in data.items():
        print(f"\nProcessing Team: {country}")
        for player in players:
            name_keys = [k for k in player.keys() if "name" in k.lower()]
            if name_keys:
                player_name = str(player[name_keys[0]])
                
                # Skip if already generated
                if 'image_url' in player and player['image_url']:
                    continue
                    
                img_path = generate_player_image_local(player_name, country)
                if img_path:
                    # Convert to web path relative to document root
                    player['image_url'] = "/" + img_path
                    
                    # Save updated JSON back to disk incrementally
                    with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"Updated {MASTER_JSON_PATH.name} with new image URL for {player_name}.")

if __name__ == "__main__":
    process_all_decks()
