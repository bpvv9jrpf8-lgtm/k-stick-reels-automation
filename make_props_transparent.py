from PIL import Image
import os
import glob

INPUT_DIR = "assets/props_raw"
OUTPUT_DIR = "assets/props"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def remove_magenta(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]

            if r > 180 and b > 150 and g < 120:
                pixels[x, y] = (255, 255, 255, 0)

    bbox = img.getbbox()

    if bbox:
        img = img.crop(bbox)

    img.save(output_path, "PNG")


files = glob.glob(os.path.join(INPUT_DIR, "*.png"))

if not files:
    raise FileNotFoundError("No prop files found")

for input_path in files:
    filename = os.path.basename(input_path)
    output_path = os.path.join(OUTPUT_DIR, filename)

    remove_magenta(input_path, output_path)

    print(f"Transparent prop saved: {output_path}")
