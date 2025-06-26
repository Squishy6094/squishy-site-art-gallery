import os
import json

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(os.getcwd(), 'art-list.json')

# Supported image extensions
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
# Get all folders in the current working directory, excluding .github and hidden folders
cwd = os.getcwd()
folders = [
    d for d in os.listdir(cwd)
    if os.path.isdir(os.path.join(cwd, d)) and not d.startswith('.') and d != '.github'
]
# Build a list of dicts with "artist" and "img" keys
image_data = []
for folder in folders:
    folder_path = os.path.join(cwd, folder)
    images = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and
        os.path.splitext(f)[1].lower() in image_extensions
    ]
    for img in images:
        image_data.append({"artist": folder, "img": img})

# Write the list to art-list.json
with open(output_file, 'w') as f:
    json.dump(image_data, f, indent=2)
