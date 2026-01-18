import os
import shutil
from pathlib import Path

def fix_image_problems():
    print("🔧 Fixing Image Problems...")
    
    # 1. Create directory if it doesn't exist
    image_dir = Path('static/images')
    image_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created/Verified directory: {image_dir}")
    
    # 2. Check what files exist
    print("\n📁 Current files in static/images/:")
    existing_files = list(image_dir.glob('*'))
    
    if not existing_files:
        print("  No files found! Let's create placeholder images...")
        create_placeholder_images()
    else:
        for file in existing_files:
            print(f"  - {file.name}")
        
        # 3. Fix naming issues
        print("\n🔤 Fixing filename issues...")
        fixed_count = 0
        for file in existing_files:
            name_lower = file.name.lower()
            
            # Fix common naming mistakes
            new_name = None
            
            if 'sampl' in name_lower and 'sample' not in name_lower:
                # Fix sampl2.jpg → sample2.jpg
                num = ''.join(filter(str.isdigit, file.name))
                if num:
                    new_name = f'sample{num}.jpg'
            
            elif name_lower.startswith('img'):
                num = ''.join(filter(str.isdigit, file.name))
                if num:
                    new_name = f'sample{num}.jpg'
            
            elif name_lower.startswith('property'):
                num = ''.join(filter(str.isdigit, file.name))
                if num:
                    new_name = f'sample{num}.jpg'
            
            if new_name:
                new_path = image_dir / new_name
                if not new_path.exists():
                    file.rename(new_path)
                    print(f"  ✅ Renamed: {file.name} → {new_name}")
                    fixed_count += 1
                else:
                    print(f"  ⚠️  {new_name} already exists, keeping both")
        
        # 4. Create missing files
        create_missing_files()
    
    print("\n🎉 Done! Now test your application.")

def create_placeholder_images():
    """Create simple placeholder images if PIL is not installed"""
    import base64
    
    # A simple red placeholder image (1x1 pixel, scaled with HTML)
    placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    for i in range(1, 21):
        filename = f'static/images/sample{i}.jpg'
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(placeholder))
        print(f"  ✅ Created placeholder: sample{i}.jpg")
    
    # Also create a simple HTML test file
    create_test_html()

def create_missing_files():
    """Create any missing sample1.jpg through sample20.jpg"""
    missing = []
    for i in range(1, 21):
        if not Path(f'static/images/sample{i}.jpg').exists():
            missing.append(i)
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} image files: {missing}")
        print("Creating simple text-based placeholders...")
        
        try:
            from PIL import Image, ImageDraw
            print("Using PIL to create nicer placeholders...")
            create_pil_images(missing)
        except ImportError:
            print("PIL not installed, creating basic placeholders...")
            create_basic_placeholders(missing)
    else:
        print("✅ All sample1.jpg to sample20.jpg exist!")

def create_pil_images(missing_indices):
    """Create images using PIL"""
    from PIL import Image, ImageDraw
    
    for i in missing_indices:
        img = Image.new('RGB', (400, 300), color=(30, 41, 59))
        draw = ImageDraw.Draw(img)
        draw.text((150, 130), f'Sample {i}', fill=(255, 255, 255))
        draw.text((140, 160), 'Property Image', fill=(200, 200, 200))
        img.save(f'static/images/sample{i}.jpg')
        print(f"  ✅ Created: sample{i}.jpg")

def create_basic_placeholders(missing_indices):
    """Create basic placeholder files"""
    for i in missing_indices:
        with open(f'static/images/sample{i}.jpg', 'w') as f:
            f.write(f"This is a placeholder for sample{i}.jpg")
        print(f"  ✅ Created: sample{i}.jpg")

def create_test_html():
    """Create a test HTML file to check images"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>Image Test</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .image-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }
        .image-item { border: 1px solid #ccc; padding: 10px; text-align: center; }
        img { max-width: 150px; max-height: 100px; border: 1px solid #eee; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Image Test Page</h1>
    <div class="image-grid" id="image-grid">
        <!-- Images will be loaded here -->
    </div>
    
    <script>
        function loadImages() {
            const grid = document.getElementById('image-grid');
            for (let i = 1; i <= 20; i++) {
                const div = document.createElement('div');
                div.className = 'image-item';
                
                const img = document.createElement('img');
                img.src = `../static/images/sample${i}.jpg`;
                img.alt = `sample${i}.jpg`;
                img.onload = function() {
                    div.innerHTML += `<div class="success">✓ sample${i}.jpg</div>`;
                };
                img.onerror = function() {
                    div.innerHTML += `<div class="error">✗ sample${i}.jpg</div>`;
                };
                
                div.appendChild(img);
                grid.appendChild(div);
            }
        }
        
        loadImages();
    </script>
</body>
</html>'''
    
    with open('image_test.html', 'w') as f:
        f.write(html)
    print("\n📄 Created image_test.html - open this file in your browser to test images")

if __name__ == '__main__':
    fix_image_problems()