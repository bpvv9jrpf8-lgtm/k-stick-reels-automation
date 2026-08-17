from PIL import Image
import os

INPUT_FILES = [
    "assets/character/k_stick_base.png",
    "assets/expressions/k_stick_happy.png",
    "assets/expressions/k_stick_sad.png",
    "assets/expressions/k_stick_angry.png",
    "assets/expressions/k_stick_shocked.png",
    "assets/expressions/k_stick_sleepy.png",
]

OUTPUT_DIR = "assets/transparent"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def remove_light_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]

            # Remove nearly-white / very light neutral background
            if r > 235 and g > 235 and b > 235:
                pixels[x, y] = (255, 255, 255, 0)

    # Crop transparent padding
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    img.save(output_path)


for input_path in INPUT_FILES:
    name = os.path.basename(input_path)

    output_path = os.path.join(
        OUTPUT_DIR,
        name.replace(".png", "_transparent.png")
    )

    remove_light_background(input_path, output_path)
    print(f"Saved: {output_path}")
