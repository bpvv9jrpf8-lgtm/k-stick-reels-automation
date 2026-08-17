from PIL import Image
import os
import glob

INPUT_DIR = "assets/poses_raw"
OUTPUT_DIR = "assets/poses"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def remove_magenta_background(input_path, output_path):
    image = Image.open(input_path).convert("RGBA")

    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]

            # Detect strong magenta / pink background.
            # Keeps white face and red cap safe.
            if r > 180 and b > 150 and g < 120:
                pixels[x, y] = (255, 255, 255, 0)

    bbox = image.getbbox()

    if bbox:
        image = image.crop(bbox)

    image.save(output_path, "PNG")


files = glob.glob(os.path.join(INPUT_DIR, "*.png"))

if not files:
    raise FileNotFoundError(
        "No raw pose files found in assets/poses_raw"
    )

for input_path in files:
    filename = os.path.basename(input_path)

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    remove_magenta_background(
        input_path,
        output_path
    )

    print(f"Transparent pose saved: {output_path}")
