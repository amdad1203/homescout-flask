from PIL import Image, ImageDraw, ImageFont
import os

# Create directory
os.makedirs('static/images', exist_ok=True)

# Bangladeshi cities for property labels
cities = ['Dhaka', 'Chattogram', 'Cumilla', 'Rajshahi', 'Sylhet', 
          'Khulna', 'Barishal', 'Rangpur', 'Mymensingh', "Cox's Bazar"]

# Property types
types = ['Apartment', 'House', 'Villa', 'Condo', 'Penthouse']

print("🎨 Creating property images...")

for i in range(1, 21):
    # Different background colors for variety
    colors = [
        (30, 64, 175),    # Blue
        (16, 185, 129),   # Green
        (139, 92, 246),   # Purple
        (239, 68, 68),    # Red
        (245, 158, 11),   # Yellow
        (59, 130, 246),   # Light Blue
        (217, 70, 239),   # Pink
        (34, 197, 94),    # Emerald
        (249, 115, 22),   # Orange
        (6, 182, 212),    # Cyan
    ]
    
    color = colors[(i-1) % len(colors)]
    city = cities[(i-1) % len(cities)]
    prop_type = types[(i-1) % len(types)]
    
    # Create image
    img = Image.new('RGB', (400, 300), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add property info
    try:
        # Try to use a nicer font if available
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Title
    draw.text((120, 100), f'Property {i}', fill=(255, 255, 255), font=font)
    
    # City
    draw.text((150, 140), city, fill=(220, 220, 220), 
              font=ImageFont.load_default().font_variant(size=16))
    
    # Type
    draw.text((160, 170), prop_type, fill=(200, 200, 200),
              font=ImageFont.load_default().font_variant(size=14))
    
    # Save
    filename = f'static/images/sample{i}.jpg'
    img.save(filename)
    print(f"✅ Created {filename}")

print("\n🎉 Successfully created 20 property images!")
print("📍 They're saved in: static/images/")
print("🏠 Images feature Bangladeshi cities: Dhaka, Chattogram, Cumilla, etc.")