#!/usr/bin/env python3
"""
Generate 26 pixel-perfect 16x16 icons with two random letters each.
Pill/stadium shape with half-circle ends and maximized letter size.
"""

import random
from PIL import Image, ImageDraw

# 4x8 pixel font for two-letter pill icons
PIXEL_FONT = {
    'A': [(1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (1, 4), (2, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'B': [(0, 0), (1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (1, 4), (2, 4), (0, 5), (3, 5), (0, 6), (3, 6), (0, 7), (1, 7), (2, 7)],
    'C': [(1, 0), (2, 0), (3, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 7), (2, 7), (3, 7)],
    'D': [(0, 0), (1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (0, 7), (1, 7), (2, 7)],
    'E': [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (0, 5), (0, 6), (0, 7), (1, 7), (2, 7), (3, 7)],
    'F': [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (0, 5), (0, 6), (0, 7)],
    'G': [(1, 0), (2, 0), (3, 0), (0, 1), (0, 2), (0, 3), (0, 4), (2, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (1, 7), (2, 7), (3, 7)],
    'H': [(0, 0), (3, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (1, 4), (2, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'I': [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6), (0, 7), (1, 7), (2, 7)],
    'J': [(0, 0), (1, 0), (2, 0), (3, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (0, 6), (2, 6), (1, 7)],
    'K': [(0, 0), (3, 0), (0, 1), (2, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4), (2, 4), (0, 5), (2, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'L': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 7), (2, 7), (3, 7)],
    'M': [(0, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3), (0, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'N': [(0, 0), (3, 0), (0, 1), (1, 1), (3, 1), (0, 2), (1, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3), (0, 4), (2, 4), (3, 4), (0, 5), (2, 5), (3, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'O': [(1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (1, 7), (2, 7)],
    'P': [(0, 0), (1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (1, 4), (2, 4), (0, 5), (0, 6), (0, 7)],
    'Q': [(1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (3, 4), (0, 5), (2, 5), (3, 5), (0, 6), (3, 6), (1, 7), (2, 7), (3, 7)],
    'R': [(0, 0), (1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (1, 4), (2, 4), (0, 5), (2, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'S': [(1, 0), (2, 0), (3, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 5), (3, 6), (0, 7), (1, 7), (2, 7)],
    'T': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7)],
    'U': [(0, 0), (3, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (3, 4), (0, 5), (3, 5), (0, 6), (3, 6), (1, 7), (2, 7)],
    'V': [(0, 0), (3, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (3, 4), (1, 5), (2, 5), (1, 6), (2, 6), (1, 7), (2, 7)],
    'W': [(0, 0), (3, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (3, 3), (0, 4), (3, 4), (0, 5), (1, 5), (2, 5), (3, 5), (0, 6), (1, 6), (2, 6), (3, 6), (0, 7), (3, 7)],
    'X': [(0, 0), (3, 0), (0, 1), (3, 1), (1, 2), (2, 2), (1, 3), (2, 3), (1, 4), (2, 4), (1, 5), (2, 5), (0, 6), (3, 6), (0, 7), (3, 7)],
    'Y': [(0, 0), (4, 0), (0, 1), (4, 1), (1, 2), (3, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7)],
    'Z': [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 2), (2, 3), (1, 4), (2, 4), (1, 5), (0, 6), (0, 7), (1, 7), (2, 7), (3, 7)],
}


def draw_pill_shape(draw, color):
    """Draw a pill/stadium shape in 16x16 (13px tall pill, starting at y=1)."""
    # Pill is 13px tall, starting at y=1 (1px top margin, 2px bottom margin)
    pixels = [
        (2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),
        (1,2),(14,2),
        (0,3),(15,3),
        (0,4),(15,4),
        (0,5),(15,5),
        (0,6),(15,6),
        (0,7),(15,7),
        (0,8),(15,8),
        (0,9),(15,9),
        (0,10),(15,10),
        (0,11),(15,11),
        (1,12),(14,12),
        (2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),(12,13),(13,13)
    ]
    
    for x, y in pixels:
        draw.point((x, y), fill=color)


def draw_letter(draw, letter, offset_x, offset_y, color):
    """Draw a single letter at the specified offset."""
    if letter not in PIXEL_FONT:
        return
    for px, py in PIXEL_FONT[letter]:
        x = offset_x + px
        y = offset_y + py
        draw.point((x, y), fill=color)


def create_icon(letter1, letter2, output_path):
    """Create a 16x16 icon with two letters inside a centered pill shape."""
    # Create image with transparent background - always 16x16
    img = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    black = (0, 0, 0, 255)
    
    # Draw pill shape border (13px tall, starting at y=1)
    draw_pill_shape(draw, black)
    
    # Calculate letter positions for 5x8 font
    # Two letters: 4+2+4 default, or 5+1+N when T or Y is present
    # Letter height: 8 pixels
    # Pill is 13px tall starting at y=1, top margin 2px within pill
    
    letter_height = 8
    start_y = 1 + 2  # = 3

    def slot_width(letter):
        return 5 if letter in ('T', 'Y') else 4

    width1 = slot_width(letter1)
    width2 = slot_width(letter2)
    spacing = 1 if letter1 in ('T', 'Y') or letter2 in ('T', 'Y') else 2
    total_width = width1 + spacing + width2
    start_x = (16 - total_width) // 2

    draw_letter(draw, letter1, start_x, start_y, black)
    draw_letter(draw, letter2, start_x + width1 + spacing, start_y, black)
    
    # Save as PNG
    img.save(output_path, 'PNG')
    return img


def generate_all_icons(output_dir='icons'):
    """Generate 26 icons with random letter pairs."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    # Set seed for reproducibility
    random.seed(42)
    
    icons_info = []
    
    for i in range(26):
        # Pick two random letters
        letter1 = random.choice(alphabet)
        letter2 = random.choice(alphabet)
        
        # Create filename based on index
        filename = f'icon_{i+1:02d}_{letter1}{letter2}.png'
        filepath = os.path.join(output_dir, filename)
        
        create_icon(letter1, letter2, filepath)
        icons_info.append((filename, letter1, letter2))
        print(f'Created: {filename}')
    
    return icons_info


def create_preview_grid(icons_dir='icons', output_path='preview_grid.png'):
    """Create a preview grid showing all icons at 8x scale for review."""
    import os
    
    # Load all icons
    icon_files = sorted([f for f in os.listdir(icons_dir) if f.endswith('.png')])
    
    # Icon dimensions - always 16x16
    icon_size = 16
    
    # Create grid: 13 icons per row (2 rows for 26 icons)
    cols = 13
    rows = 2
    scale = 8  # Scale factor for preview
    padding = 4
    
    grid_width = cols * (icon_size * scale + padding) + padding
    grid_height = rows * (icon_size * scale + padding) + padding
    
    grid = Image.new('RGBA', (grid_width, grid_height), (240, 240, 240, 255))
    
    for i, icon_file in enumerate(icon_files):
        row = i // cols
        col = i % cols
        
        icon = Image.open(os.path.join(icons_dir, icon_file))
        # Scale up using nearest neighbor for crisp pixels
        scaled = icon.resize((icon_size * scale, icon_size * scale), Image.NEAREST)
        
        x = padding + col * (icon_size * scale + padding)
        y = padding + row * (icon_size * scale + padding)
        
        grid.paste(scaled, (x, y), scaled)
    
    grid.save(output_path, 'PNG')
    print(f'Preview grid saved: {output_path}')


if __name__ == '__main__':
    print('Generating 26 pixel-perfect icons...')
    print('=' * 40)
    
    icons_info = generate_all_icons()
    
    print('=' * 40)
    print(f'Generated {len(icons_info)} icons in ./icons/')
    
    # Create preview grid
    create_preview_grid()
    
    print('\nIcon details:')
    for filename, l1, l2 in icons_info:
        print(f'  {filename}: "{l1}{l2}"')
