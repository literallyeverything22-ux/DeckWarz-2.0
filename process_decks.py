import os
from PIL import Image
import shutil

src_dir = 'assets/Deck box images'
dest_dir = 'static/images/decks'
os.makedirs(dest_dir, exist_ok=True)

for file in os.listdir(src_dir):
    if file.endswith('.png'):
        img_path = os.path.join(src_dir, file)
        try:
            img = Image.open(img_path)
            w, h = img.size
            print(f"Processing {file} (size: {w}x{h})...")
            
            # Split the image into left and right halves
            left_half = img.crop((0, 0, w//2, h))
            right_half = img.crop((w//2, 0, w, h))
            
            # Format the name (e.g. 'India (1).png' -> 'india')
            base_name = file.split(' (')[0].lower().replace(' ', '_')
            
            left_half.save(os.path.join(dest_dir, f"{base_name}_start.png"))
            right_half.save(os.path.join(dest_dir, f"{base_name}_end.png"))
        except Exception as e:
            print(f"Failed to process {file}: {e}")

print("Done processing deck boxes into start and end frames.")
