from google import genai
import os
from PIL import Image
from io import BytesIO

# The user provided their API key directly
os.environ["GEMINI_API_KEY"] = "AIzaSyD3B7GmdC53GERTZk4zlooYKqv7dTu2Du0"

client = genai.Client()

print("Testing Google Imagen 3 API...")
try:
    result = client.models.generate_images(
        model='imagen-4.0-fast-generate-001',
        prompt='A hyper-realistic cinematic portrait of an Australian cricket player, wearing yellow and green, intense lighting, dark stadium background, perfect details',
        config=genai.types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="3:4",
            output_mime_type="image/jpeg",
        )
    )

    if result.generated_images:
        for i, generated_image in enumerate(result.generated_images):
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            filename = f"test_imagen_aus_{i}.jpg"
            image.save(filename)
            print(f"Success! Image generated and saved as {filename}")
    else:
        print("No images were returned.")

except Exception as e:
    print(f"Error occurred: {e}")
