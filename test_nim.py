import os
import requests
import base64

# The user mentioned using NIMs recently. Let's see if there is an ENV set up for it.
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")

# Need the `pip install requests`
invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/sdxl-turbo"

headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Accept": "application/json",
}

payload = {
    "text_prompts": [
        {
            "text": "A majestic portrait of an Australian cricket player, realistic, cinematic lighting",
            "weight": 1
        }
    ],
    "cfg_scale": 5,
    "seed": 0,
    "steps": 4
}

print("Testing NVIDIA API Connection...")
try:
    response = requests.post(invoke_url, headers=headers, json=payload)
    response.raise_for_status()
    
    response_body = response.json()
    # Save the output image
    image_data = base64.b64decode(response_body['artifacts'][0]['base64'])
    with open("test_nvidia_image.png", "wb") as f:
        f.write(image_data)
        
    print("Success! Image generated and saved as test_nvidia_image.png")
    
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response:
        print(f"Details: {e.response.text}")
