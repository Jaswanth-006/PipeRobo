import json
import os
import cv2
import shutil
import yaml

# --- CONFIGURATION ---
INPUT_FILE = 'info.labels'
CLASSES = ['crack', 'corrosion'] # We ignore "Normal" so those images act as background (good for AI!)

# Create YOLO directory structure
dirs = ['datasets/images/train', 'datasets/images/val', 'datasets/labels/train', 'datasets/labels/val']
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Load JSON data
with open(INPUT_FILE, 'r') as f:
    data = json.load(f)

print(f"Found {len(data['files'])} images. Converting...")

for item in data['files']:
    # Get image info
    original_path = item['path'] # e.g., "training/image.jpg"
    filename = os.path.basename(original_path)
    subset = 'train' if 'training' in original_path else 'val'
    
    # Check if image exists
    if not os.path.exists(original_path):
        print(f"Skipping missing file: {original_path}")
        continue

    # Load image to get dimensions
    img = cv2.imread(original_path)
    if img is None: continue
    height, width, _ = img.shape

    # Prepare YOLO labels
    yolo_lines = []
    for box in item['boundingBoxes']:
        label = box['label']
        if label not in CLASSES:
            continue # Skip "Normal" or other labels
        
        class_id = CLASSES.index(label)
        
        # Convert to YOLO format (Normalized Center_X, Center_Y, Width, Height)
        # Edge Impulse gives: x, y, w, h (Top-Left)
        x_center = (box['x'] + (box['width'] / 2)) / width
        y_center = (box['y'] + (box['height'] / 2)) / height
        w_norm = box['width'] / width
        h_norm = box['height'] / height
        
        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

    # Save Image to new folder
    shutil.copy(original_path, f"datasets/images/{subset}/{filename}")

    # Save Label Text File
    txt_filename = os.path.splitext(filename)[0] + ".txt"
    with open(f"datasets/labels/{subset}/{txt_filename}", "w") as f:
        f.write("\n".join(yolo_lines))

print("Conversion Complete!")

# Create data.yaml automatically
yaml_content = f"""
path: {os.path.abspath('datasets')} 
train: images/train
val: images/val

nc: {len(CLASSES)}
names: {CLASSES}
"""

with open("data.yaml", "w") as f:
    f.write(yaml_content)

print("Created data.yaml. You are ready to train!")