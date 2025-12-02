import os
import json
import re
from PIL import Image

# Output JSON file
output_file = os.path.join(os.getcwd(), 'art-list.json')

# Extensions we consider image types
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

cwd = os.getcwd()

# Artist folders
folders = [
    d for d in os.listdir(cwd)
    if os.path.isdir(os.path.join(cwd, d)) and not d.startswith('.') and d != '.github'
]


def clean_filename(name: str) -> str:
    base, ext = os.path.splitext(name)

    base = re.sub(r"[^A-Za-z0-9 _\-.]", "", base)
    base = str(base)

    return f"{base}.png"


image_data = []

for folder in folders:
    folder_path = os.path.join(cwd, folder)

    # Low-quality folder
    lowq_path = os.path.join(folder_path, "low-quality")
    os.makedirs(lowq_path, exist_ok=True)

    # Clear previous low-quality files
    for f in os.listdir(lowq_path):
        os.remove(os.path.join(lowq_path, f))

    # All original images
    originals = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and
        os.path.splitext(f)[1].lower() in image_extensions
    ]

    sanitized = []

    for img in originals:
        old_path = os.path.join(folder_path, img)
        old_base, old_ext = os.path.splitext(img)
        old_ext_l = old_ext.lower()

        # Determine what the cleaned name SHOULD be
        cleaned_name = clean_filename(img)
        new_path = os.path.join(folder_path, cleaned_name)

        needs_rename = (cleaned_name != img)
        needs_png_conversion = (old_ext_l != ".png")

        # If the file is already safe AND already PNG → skip
        if not needs_rename and not needs_png_conversion:
            sanitized.append(img)
            print("Skipped " + img)
            continue

        # Otherwise convert + rename
        try:
            with Image.open(old_path) as im:
                im = im.convert("RGBA")
                im.save(new_path, format="PNG", optimize=True)
                print("Converted " + img + " to PNG")
        except Exception as e:
            print(f"Error converting {old_path}: {e}")
            continue

        # Remove old file
        if old_path != new_path:
            try:
                os.remove(old_path)
            except:
                pass

        sanitized.append(cleaned_name)

    for img in sanitized:
        path = os.path.join(folder_path, img)

        try:
            with Image.open(path) as im:
                w, h = im.size

                # Only scale DOWN if both dimensions > 128
                if min(w, h) > 128:
                    scale = 128 / min(w, h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    im_low = im.resize((new_w, new_h), Image.BILINEAR)
                    print(f"Downscaled {img} to {new_w}x{new_h}")
                else:
                    # Do not scale smaller images
                    im_low = im.copy()

                low_path = os.path.join(lowq_path, img)
                im_low.save(low_path, optimize=True)

        except Exception as e:
            print(f"Error generating low-quality for {path}: {e}")

        image_data.append({"artist": folder, "img": img})

with open(output_file, 'w') as f:
    json.dump(image_data, f, indent=2)

print("Script Done!")
