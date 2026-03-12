from google import genai
import os

os.environ["GEMINI_API_KEY"] = "AIzaSyD3B7GmdC53GERTZk4zlooYKqv7dTu2Du0"

client = genai.Client()

print("Listing available models...")
for model in client.models.list():
    if "imagen" in model.name:
        print(f"Model ID: {model.name}")
