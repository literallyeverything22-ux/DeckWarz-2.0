import requests
import io
from PIL import Image

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.content

print("Testing HuggingFace FLUX.1 API...")
try:
    image_bytes = query({
        "inputs": "A hyper-realistic cinematic portrait of an Australian cricket player, wearing yellow and green, intense lighting, dark stadium background, perfect details",
    })

    # The inference endpoint returns pure bytes.
    image = Image.open(io.BytesIO(image_bytes))
    image.save("test_hf_flux.jpg")
    print("Success! Image generated and saved as test_hf_flux.jpg")
except Exception as e:
    print(f"Error occurred: {e}")
    # Sometimes it returns a JSON error message if rate limited or warming up
    if isinstance(image_bytes, bytes):
        print(image_bytes.decode('utf-8', errors='ignore'))
