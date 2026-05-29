#!/usr/bin/env python3
"""
Generate 26 pixel-perfect 16x16 icons with two random letters each.
Pill/stadium shape with half-circle ends and maximized letter size.
"""

import random
from PIL import Image, ImageDraw

# Larger 4x7 pixel font for maximum legibility
# Each letter is a list of (x, y) coordinates for black pixels
# Optimized for pill-shaped container at 16x16
PIXEL_FONT = {
    'A': [
        (1, 0), (2, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (1, 3), (2, 3), (3, 3),      # middle bar
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'B': [
        (0, 0), (1, 0), (2, 0),              # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (1, 3), (2, 3),              # middle bar
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (1, 6), (2, 6),              # bottom
    ],
    'C': [
        (1, 0), (2, 0), (3, 0),              # top
        (0, 1),                              # row 1
        (0, 2),                              # row 2
        (0, 3),                              # middle
        (0, 4),                              # row 4
        (0, 5),                              # row 5
        (1, 6), (2, 6), (3, 6),              # bottom
    ],
    'D': [
        (0, 0), (1, 0), (2, 0),              # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (3, 3),                      # middle
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (1, 6), (2, 6),              # bottom
    ],
    'E': [
        (0, 0), (1, 0), (2, 0), (3, 0),      # top
        (0, 1),                              # row 1
        (0, 2),                              # row 2
        (0, 3), (1, 3), (2, 3),              # middle bar
        (0, 4),                              # row 4
        (0, 5),                              # row 5
        (0, 6), (1, 6), (2, 6), (3, 6),      # bottom
    ],
    'F': [
        (0, 0), (1, 0), (2, 0), (3, 0),      # top
        (0, 1),                              # row 1
        (0, 2),                              # row 2
        (0, 3), (1, 3), (2, 3),              # middle bar
        (0, 4),                              # row 4
        (0, 5),                              # row 5
        (0, 6),                              # bottom
    ],
    'G': [
        (1, 0), (2, 0), (3, 0),              # top
        (0, 1),                              # row 1
        (0, 2),                              # row 2
        (0, 3), (2, 3), (3, 3),              # middle with bar
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (1, 6), (2, 6), (3, 6),              # bottom
    ],
    'H': [
        (0, 0), (3, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (1, 3), (2, 3), (3, 3),      # middle bar
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'I': [
        (0, 0), (1, 0), (2, 0),              # top bar
        (1, 1),                              # center
        (1, 2),                              # center
        (1, 3),                              # center
        (1, 4),                              # center
        (1, 5),                              # center
        (0, 6), (1, 6), (2, 6),              # bottom bar
    ],
    'J': [
        (0, 0), (1, 0), (2, 0), (3, 0),      # top bar
        (2, 1),                              # right
        (2, 2),                              # right
        (2, 3),                              # right
        (2, 4),                              # right
        (0, 5), (2, 5),                      # row 5
        (1, 6),                              # bottom
    ],
    'K': [
        (0, 0), (3, 0),                      # top
        (0, 1), (2, 1),                      # row 1
        (0, 2), (1, 2),                      # row 2
        (0, 3), (1, 3),                      # middle
        (0, 4), (2, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'L': [
        (0, 0),                              # top
        (0, 1),                              # row 1
        (0, 2),                              # row 2
        (0, 3),                              # middle
        (0, 4),                              # row 4
        (0, 5),                              # row 5
        (0, 6), (1, 6), (2, 6), (3, 6),      # bottom
    ],
    'M': [
        (0, 0), (3, 0),                      # top corners
        (0, 1), (1, 1), (2, 1), (3, 1),      # row 1
        (0, 2), (1, 2), (2, 2), (3, 2),      # row 2
        (0, 3), (3, 3),                      # middle
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'N': [
        (0, 0), (3, 0),                      # top
        (0, 1), (1, 1), (3, 1),              # row 1
        (0, 2), (1, 2), (3, 2),              # row 2
        (0, 3), (2, 3), (3, 3),              # middle
        (0, 4), (2, 4), (3, 4),              # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'O': [
        (1, 0), (2, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (3, 3),                      # middle
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (1, 6), (2, 6),                      # bottom
    ],
    'P': [
        (0, 0), (1, 0), (2, 0),              # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (1, 3), (2, 3),              # middle bar
        (0, 4),                              # row 4
        (0, 5),                              # row 5
        (0, 6),                              # bottom
    ],
    'Q': [
        (1, 0), (2, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (3, 3),                      # middle
        (0, 4), (2, 4), (3, 4),              # row 4
        (0, 5), (3, 5),                      # row 5
        (1, 6), (2, 6), (3, 6),              # bottom with tail
    ],
    'R': [
        (0, 0), (1, 0), (2, 0),              # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (1, 3), (2, 3),              # middle bar
        (0, 4), (2, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'S': [
        (1, 0), (2, 0), (3, 0),              # top
        (0, 1),                              # row 1
        (0, 2),                              # row 2
        (1, 3), (2, 3),                      # middle
        (3, 4),                              # row 4
        (3, 5),                              # row 5
        (0, 6), (1, 6), (2, 6),              # bottom
    ],
    'T': [
        (0, 0), (1, 0), (2, 0), (3, 0),      # top bar
        (1, 1), (2, 1),                      # center
        (1, 2), (2, 2),                      # center
        (1, 3), (2, 3),                      # center
        (1, 4), (2, 4),                      # center
        (1, 5), (2, 5),                      # center
        (1, 6), (2, 6),                      # bottom
    ],
    'U': [
        (0, 0), (3, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (3, 3),                      # middle
        (0, 4), (3, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (1, 6), (2, 6),                      # bottom
    ],
    'V': [
        (0, 0), (3, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (3, 3),                      # middle
        (1, 4), (2, 4),                      # row 4
        (1, 5), (2, 5),                      # row 5
        (1, 6), (2, 6),                      # bottom
    ],
    'W': [
        (0, 0), (3, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (0, 2), (3, 2),                      # row 2
        (0, 3), (3, 3),                      # middle
        (0, 4), (1, 4), (2, 4), (3, 4),      # row 4
        (0, 5), (1, 5), (2, 5), (3, 5),      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'X': [
        (0, 0), (3, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (1, 2), (2, 2),                      # row 2
        (1, 3), (2, 3),                      # middle
        (1, 4), (2, 4),                      # row 4
        (0, 5), (3, 5),                      # row 5
        (0, 6), (3, 6),                      # bottom
    ],
    'Y': [
        (0, 0), (3, 0),                      # top
        (0, 1), (3, 1),                      # row 1
        (1, 2), (2, 2),                      # row 2
        (1, 3), (2, 3),                      # center
        (1, 4), (2, 4),                      # center
        (1, 5), (2, 5),                      # center
        (1, 6), (2, 6),                      # bottom
    ],
    'Z': [
        (0, 0), (1, 0), (2, 0), (3, 0),      # top
        (3, 1),                              # row 1
        (2, 2),                              # row 2
        (1, 3), (2, 3),                      # middle
        (1, 4),                              # row 4
        (0, 5),                              # row 5
        (0, 6), (1, 6), (2, 6), (3, 6),      # bottom
    ],
}


def draw_pill_shape(draw, color):
    """Draw a pill/stadium shape centered in 16x16 (12px tall pill, offset by 2px)."""
    # Pill is 12px tall, centered vertically in 16x16 (2px offset top/bottom)
    pixels = [
        (3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),
        (2,3),(13,3),
        (1,4),(14,4),
        (0,5),(15,5),
        (0,6),(15,6),
        (0,7),(15,7),
        (0,8),(15,8),
        (0,9),(15,9),
        (0,10),(15,10),
        (1,11),(14,11),
        (2,12),(13,12),
        (3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),(12,13)
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
    
    # Draw pill shape border (centered in 16x16)
    draw_pill_shape(draw, black)
    
    # Calculate letter positions for 4x7 font
    # Two letters: 4 + 1 + 4 = 9 pixels wide
    # Letter height: 7 pixels
    # Pill is 12px tall, centered at y offset 2
    
    letter_width = 4
    letter_height = 7
    spacing = 1
    total_width = letter_width * 2 + spacing  # 9 pixels
    
    # Center horizontally in 16px
    start_x = (16 - total_width) // 2   # = 3
    # Center vertically within the pill area (12px starting at y=2)
    start_y = 2 + (12 - letter_height) // 2  # = 2 + 2 = 4
    
    # Draw first letter
    draw_letter(draw, letter1, start_x, start_y, black)
    
    # Draw second letter
    draw_letter(draw, letter2, start_x + letter_width + spacing, start_y, black)
    
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
