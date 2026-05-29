# Pixel Icon Generator

A web-based tool for generating pixel-perfect letter icons at small sizes (16×16 and 16×12 pixels).

## Features

- **Three variants:**
  - 1 letter in a circle (16×16px)
  - 2 letters in a pill shape (16×12px)
  - 3 letters in a pill shape (16×12px)

- **Theme support:**
  - Light theme (black icons)
  - Dark theme (white icons)

- **Export:** Downloads both light and dark transparent PNGs

## Usage

1. Open `index.html` in a web browser
2. Select the number of letters (1, 2, or 3)
3. Type your letters (A-Z)
4. Preview updates instantly
5. Click "Export" to download both light and dark versions

## Files

- `index.html` - Main web application
- `generate_icons.py` - Python script for batch generation
- `icons/` - Pre-generated sample icons

## Technical Details

- Hand-crafted pixel fonts optimized for each size
- No anti-aliasing for crisp rendering
- Transparent PNG export
