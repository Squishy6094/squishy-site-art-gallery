import os
import json
import re
import unicodedata
from PIL import Image

# Get directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(os.getcwd(), 'art-list.json')

# Supported image extensions
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

cwd = os.getcwd()

folders = [
    d for d in os.listdir(cwd)
    if os.path.isdir(os.path.join(cwd, d)) and not d.startswith('.') and d != '.github'
]

def clean_filename(name: str) -> str:
    # Remove extension first
    base, ext = os.path.splitext(name)

    base = unicodedata.normalize("NFKD", base)
    base = "".join(c for c in base if not unicodedata.combining(c))

    # Keep only safe characters A-Z a-z 0-9 _ -
    base = re.sub(r"[^A-Za-z0-9_\-]", "", base)

    return base + ".png"  # new enforced extension


image_data = []

for folder in folders:
    folder_path = os.path.join(cwd, folder)

    # Create / Wipe low-quality folder
    lowq_path = os.path.join(folder_path, "low-quality")
    os.makedirs(lowq_path, exist_ok=True)
    for f in os.listdir(lowq_path):
        os.remove(os.path.join(lowq_path, f))

    # Scan images
    originals = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and
        os.path.splitext(f)[1].lower() in image_extensions
    ]

    sanitized_images = []

    for img in originals:
        old_path = os.path.join(folder_path, img)

        new_name = clean_filename(img)
        new_path = os.path.join(folder_path, new_name)

        # Avoid name conflict (rare but safe)
        if new_path.lower() != old_path.lower() and os.path.exists(new_path):
            base, ext = os.path.splitext(new_name)
            new_name = base + "_1" + ext
            new_path = os.path.join(folder_path, new_name)

        try:
            with Image.open(old_path) as im:
                im = im.convert("RGBA")  # keep transparency
                im.save(new_path, format="PNG", optimize=True)

        except Exception as e:
            print(f"Error converting {old_path}: {e}")
            continue

        # Delete old file if filename changed or wasn't PNG
        if old_path != new_path:
            try:
                os.remove(old_path)
            except:
                pass

        sanitized_images.append(new_name)

    # Compress
    for img in sanitized_images:
        full_img_path = os.path.join(folder_path, img)

        try:
            with Image.open(full_img_path) as im:
                w, h = im.size

                # Only scale DOWN if smallest dimension > 128
                if min(w, h) > 128:
                    scale = 128 / min(w, h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)

                    im_low = im.resize((new_w, new_h), Image.BILINEAR)
                else:
                    im_low = im.copy()

                low_path = os.path.join(lowq_path, img)
                im_low.save(low_path, optimize=True)

        except Exception as e:
            print(f"Error generating low-quality for {full_img_path}: {e}")

        # Add to manifest
        image_data.append({
            "artist": folder,
            "img": img
        })

# Write
with open(output_file, 'w') as f:
    json.dump(image_data, f, indent=2)

print("✔ All images sanitized, converted to PNG, low-quality generated, and JSON updated.")
