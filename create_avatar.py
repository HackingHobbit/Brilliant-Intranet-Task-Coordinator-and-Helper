#!/usr/bin/env python3
"""
Create a simple placeholder avatar image for the Local AI Avatar project
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_avatar_placeholder():
    """Create a simple placeholder avatar image"""
    
    # Create assets directory if it doesn't exist
    os.makedirs('assets', exist_ok=True)
    
    # Create a 400x400 image with blue background
    width, height = 400, 400
    image = Image.new('RGB', (width, height), color='#00bfff')
    draw = ImageDraw.Draw(image)
    
    # Add a gradient effect
    for y in range(height):
        # Create a subtle gradient from top to bottom
        factor = y / height
        r = int(0 * (1 - factor) + 0 * factor)
        g = int(191 * (1 - factor) + 100 * factor)
        b = int(255 * (1 - factor) + 200 * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add a circular mask for a more avatar-like appearance
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([20, 20, width-20, height-20], fill=255)
    
    # Create a circular background
    circle_bg = Image.new('RGB', (width, height), (0, 0, 0))
    circle_bg.paste(image, (0, 0), mask)
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
    except:
        try:
            # Fallback to default font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        except:
            # Use default font
            font = ImageFont.load_default()
    
    # Add "AI" text
    text = "AI"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 20
    
    # Draw text with white color and shadow
    draw.text((x+2, y+2), text, fill='#000000', font=font)  # Shadow
    draw.text((x, y), text, fill='#ffffff', font=font)  # Main text
    
    # Add "Avatar" text below
    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            small_font = ImageFont.load_default()
    
    text2 = "Avatar"
    bbox2 = draw.textbbox((0, 0), text2, font=small_font)
    text2_width = bbox2[2] - bbox2[0]
    text2_height = bbox2[3] - bbox2[1]
    
    x2 = (width - text2_width) // 2
    y2 = y + text_height + 10
    
    # Draw second text with shadow
    draw.text((x2+1, y2+1), text2, fill='#000000', font=small_font)  # Shadow
    draw.text((x2, y2), text2, fill='#ffffff', font=small_font)  # Main text
    
    # Add a subtle glow effect
    glow_radius = 20
    for i in range(glow_radius):
        alpha = int(255 * (1 - i / glow_radius))
        glow_color = (0, 191, 255)
        draw.ellipse([20-i, 20-i, width-20+i, height-20+i], 
                    outline=glow_color, width=1)
    
    # Save the image
    output_path = 'assets/avatar.jpg'
    image.save(output_path, 'JPEG', quality=95)
    
    print(f"✅ Created placeholder avatar: {output_path}")
    print("   You can replace this with your own image later")
    
    return output_path

if __name__ == "__main__":
    create_avatar_placeholder() 