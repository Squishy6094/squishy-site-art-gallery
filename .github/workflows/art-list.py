import os
import json
from PIL import Image

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(os.getcwd(), 'art-list.json')

# Supported image extensions
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

cwd = os.getcwd()

# Get all folders in repo root except hidden and .github
folders = [
    d for d in os.listdir(cwd)
    if os.path.isdir(os.path.join(cwd, d))
    and not d.startswith('.')
    and d != '.github'
]

image_data = []

for folder in folders:
    folder_path = os.path.join(cwd, folder)

    # Path for low-quality directory
    lowq_path = os.path.join(folder_path, "low-quality")
    os.makedirs(lowq_path, exist_ok=True)

    # Clear the low-quality folder
    for f in os.listdir(lowq_path):
        os.remove(os.path.join(lowq_path, f))

    # Scan for image files
    images = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and
        os.path.splitext(f)[1].lower() in image_extensions
    ]

    for img in images:
        full_img_path = os.path.join(folder_path, img)
        image_data.append({"artist": folder, "img": img})

        # Generate low-quality version
        try:
            with Image.open(full_img_path) as im:
                w, h = im.size

                # Only resize if either dimension > 64
                if max(w, h) > 64:
                    # scale so the largest dimension becomes 64
                    scale = 64 / max(w, h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)

                    im_low = im.resize((new_w, new_h), Image.BILINEAR)
                else:
                    # Already small; just copy original
                    im_low = im.copy()

                # Save to low-quality directory
                low_path = os.path.join(lowq_path, img)
                im_low.save(low_path, optimize=True)

        except Exception as e:
            print(f"Error processing {full_img_path}: {e}")

# Write art-list.json
with open(output_file, 'w') as f:
    json.dump(image_data, f, indent=2)

print("Art list + low-quality images generated.")
