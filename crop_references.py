from PIL import Image
import os

# Create references directory
os.makedirs('references', exist_ok=True)

# Define source images and their symbols with approximate crop regions
# Format: (image_path, [(symbol_name, left, top, right, bottom), ...])

sources = [
    # Image 4: Straightness, Flatness, Roundness, Cylindricity, Line profile, Surface profile, Angularity
    ('/Users/zhouka/.cursor/projects/Users-zhouka-Documents-AI-project-Small-Font/assets/Screenshot_2026-05-29_at_9.58.41_am-add01cb8-c52c-40b2-8acb-93b8c4c21930.png', [
        ('straightness', 30, 10, 180, 70),
        ('flatness', 30, 90, 180, 170),
        ('roundness', 30, 200, 180, 280),
        ('cylindricity', 30, 310, 180, 400),
        ('lineProfile', 30, 430, 180, 520),
        ('surfaceProfile', 30, 550, 180, 640),
        ('angularity', 30, 680, 180, 770),
    ]),
    
    # Image 5: Perpendicularity, Parallelism, Position, Concentricity, Coaxiality, Symmetry, Circular runout
    ('/Users/zhouka/.cursor/projects/Users-zhouka-Documents-AI-project-Small-Font/assets/Screenshot_2026-05-29_at_9.58.46_am-95209d38-1a47-4a88-ac5d-3bacb903a1bb.png', [
        ('perpendicularity', 50, 10, 200, 110),
        ('parallelism', 50, 130, 200, 220),
        ('position', 50, 240, 200, 340),
        ('concentricity', 50, 360, 200, 450),
        ('coaxiality', 50, 480, 200, 570),
        ('symmetry', 50, 600, 200, 680),
        ('circularRunout', 50, 710, 200, 810),
    ]),
    
    # Image 2: Total runout
    ('/Users/zhouka/.cursor/projects/Users-zhouka-Documents-AI-project-Small-Font/assets/Screenshot_2026-05-29_at_9.58.49_am-f7cf4cbf-dd09-4b90-b3bc-02357840d5d9.png', [
        ('totalRunout', 40, 10, 200, 90),
    ]),
    
    # Image 3: Diameter, Plus/Minus, Degree, Square, Taper, Slope, Counterbore, Countersink
    ('/Users/zhouka/.cursor/projects/Users-zhouka-Documents-AI-project-Small-Font/assets/Screenshot_2026-05-29_at_9.58.54_am-ec65a09b-cccf-4c90-8200-6929812a5c1c.png', [
        ('diameter', 30, 10, 180, 110),
        ('plusMinus', 30, 130, 180, 210),
        ('degree', 30, 240, 180, 310),
        ('square', 30, 340, 180, 430),
        ('taper', 30, 460, 180, 550),
        ('slope', 30, 580, 180, 670),
        ('counterbore', 30, 700, 180, 780),
        ('countersink', 30, 820, 180, 910),
    ]),
    
    # Image 1: Depth, Centerline, Circular Projection, Section, Between, Integral
    ('/Users/zhouka/.cursor/projects/Users-zhouka-Documents-AI-project-Small-Font/assets/Screenshot_2026-05-29_at_9.59.00_am-b7ed8677-a6bb-4447-8aaa-93e47e57b619.png', [
        ('depth', 30, 10, 180, 100),
        ('centerline', 30, 120, 180, 220),
        ('circularProjection', 30, 250, 180, 350),
        ('section', 30, 380, 180, 490),
        ('between', 30, 520, 180, 600),
        ('integral', 30, 640, 180, 750),
    ]),
]

for img_path, symbols in sources:
    print(f"Processing {img_path}")
    try:
        img = Image.open(img_path)
        for name, left, top, right, bottom in symbols:
            # Crop the symbol
            cropped = img.crop((left, top, right, bottom))
            # Save
            output_path = f'references/{name}.png'
            cropped.save(output_path)
            print(f"  Saved {name}.png")
    except Exception as e:
        print(f"  Error: {e}")

print("Done!")
