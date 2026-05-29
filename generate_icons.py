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


def draw_pill_shape(draw, width, height, color):
    """Draw a pill/stadium shape with half circles on each side (1px outline)."""
    # For 16x12, half circle radius = height/2 = 6 pixels
    # Pill shape: semicircle left, straight top/bottom, semicircle right
    
    # Draw pixel-perfect semicircles for 12px height (radius ~5-6)
    # Left arc pixels (for 12px height pill)
    left_arc = [
        (3, 0), (4, 0), (5, 0),  # top
        (2, 1), (1, 2), (0, 3), (0, 4), (0, 5),  # left side going down
        (0, 6), (0, 7), (0, 8), (1, 9), (2, 10),  # continue down
        (3, 11), (4, 11), (5, 11),  # bottom
    ]
    
    # Right arc pixels
    right_arc = [
        (10, 0), (11, 0), (12, 0),  # top
        (13, 1), (14, 2), (15, 3), (15, 4), (15, 5),  # right side going down
        (15, 6), (15, 7), (15, 8), (14, 9), (13, 10),  # continue
        (10, 11), (11, 11), (12, 11),  # bottom
    ]
    
    # Top and bottom connecting lines
    top_line = [(x, 0) for x in range(6, 10)]
    bottom_line = [(x, 11) for x in range(6, 10)]
    
    for x, y in left_arc + right_arc + top_line + bottom_line:
        if 0 <= x < width and 0 <= y < height:
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
    """Create a 16x12 icon with two letters inside a pill shape."""
    # Create image with transparent background
    img = Image.new('RGBA', (16, 12), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    black = (0, 0, 0, 255)
    
    # Draw pill shape border
    draw_pill_shape(draw, 16, 12, black)
    
    # Calculate letter positions for 4x7 font
    # Two letters: 4 + 1 + 4 = 9 pixels wide
    # Letter height: 7 pixels
    # Canvas: 16x12
    
    letter_width = 4
    letter_height = 7
    spacing = 1
    total_width = letter_width * 2 + spacing  # 9 pixels
    
    # Center horizontally in 16px: (16 - 9) / 2 = 3.5, use 3
    # Center vertically in 12px: (12 - 7) / 2 = 2.5, use 2
    start_x = (16 - total_width) // 2   # = 3
    start_y = (12 - letter_height) // 2  # = 2
    
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
    
    # Icon dimensions
    icon_width = 16
    icon_height = 12
    
    # Create grid: 13 icons per row (2 rows for 26 icons)
    cols = 13
    rows = 2
    scale = 8  # Scale factor for preview
    padding = 4
    
    grid_width = cols * (icon_width * scale + padding) + padding
    grid_height = rows * (icon_height * scale + padding) + padding
    
    grid = Image.new('RGBA', (grid_width, grid_height), (240, 240, 240, 255))
    
    for i, icon_file in enumerate(icon_files):
        row = i // cols
        col = i % cols
        
        icon = Image.open(os.path.join(icons_dir, icon_file))
        # Scale up using nearest neighbor for crisp pixels
        scaled = icon.resize((icon_width * scale, icon_height * scale), Image.NEAREST)
        
        x = padding + col * (icon_width * scale + padding)
        y = padding + row * (icon_height * scale + padding)
        
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
