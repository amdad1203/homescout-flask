import os
from pathlib import Path

# Path to your images folder
image_dir = Path('static/images')

# Check if folder exists
if not image_dir.exists():
    print(f"❌ Folder not found: {image_dir}")
    print("Creating images folder...")
    image_dir.mkdir(parents=True, exist_ok=True)

# List all files in the folder
print("📁 Files in static/images/:")
files = list(image_dir.glob('*'))
for file in files:
    print(f"  - {file.name}")

# Check for required files
required_files = [f'sample{i}.jpg' for i in range(1, 21)]
print("\n🔍 Checking for required files (sample1.jpg to sample20.jpg):")

missing_files = []
for req in required_files:
    if (image_dir / req).exists():
        print(f"  ✓ {req}")
    else:
        print(f"  ✗ {req} - MISSING")
        missing_files.append(req)

if missing_files:
    print(f"\n❌ Missing {len(missing_files)} files!")
    print("\n💡 Solutions:")
    print("1. Download images and rename them to sample1.jpg, sample2.jpg, etc.")
    print("2. Or create placeholder images with Python:")
    
    create_script = '''
from PIL import Image, ImageDraw
import os

os.makedirs('static/images', exist_ok=True)

for i in range(1, 21):
    img = Image.new('RGB', (400, 300), color=(30, 41, 59))
    d = ImageDraw.Draw(img)
    d.text((150, 130), f'Sample {i}', fill=(255, 255, 255))
    d.text((140, 160), 'Property Image', fill=(200, 200, 200))
    img.save(f'static/images/sample{i}.jpg')
    print(f"Created sample{i}.jpg")

print("✅ Created 20 placeholder images!")
    '''
    
    print("\nRun this script to create placeholder images:")
    print(create_script)
else:
    print("\n✅ All required image files found!")

# Check for common naming mistakes
print("\n🔤 Checking for common naming mistakes:")
common_errors = {
    'sampl': 'sample',
    'Sample': 'sample',
    'SAMPLE': 'sample',
    'img': 'sample',
    'property': 'sample'
}

for file in files:
    name_lower = file.name.lower()
    for wrong, correct in common_errors.items():
        if wrong in name_lower and correct not in name_lower:
            print(f"  ⚠️  Suspicious filename: {file.name}")
            print(f"     Might need renaming to {correct}X.jpg format")