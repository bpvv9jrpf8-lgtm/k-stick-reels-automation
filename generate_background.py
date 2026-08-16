import os
import sys
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

if len(sys.argv) < 2:
    raise ValueError("Please provide a background name, e.g. bedroom, office, classroom")

bg_name = sys.argv[1].strip().lower()

BACKGROUND_MAP = {
    "bedroom": "A simple clean cartoon bedroom with a bed, pillow, side table, and soft indoor lighting.",
    "office": "A simple clean cartoon office with a desk, chair, laptop, and soft indoor lighting.",
    "classroom": "A simple clean cartoon classroom with desks, a board, and simple school-room details.",
    "kitchen": "A simple clean cartoon kitchen with a fridge, counter, and neat household details.",
    "street": "A simple clean cartoon street scene with sidewalk, road, and a few simple urban background details."
}

if bg_name not in BACKGROUND_MAP:
    raise ValueError(f"Unsupported background: {bg_name}")

scene_description = BACKGROUND_MAP[bg_name]

prompt = f"""
Create a reusable background for a viral short-form 2D cartoon stickman comedy series.

Background type: {bg_name}

Scene requirements:
- {scene_description}
- no characters
- no text
- no watermark
- no logos
- clean empty central space for placing a stickman character later
- family-friendly
- simple composition
- visually clear for social media reels
- polished modern 2D cartoon style
- crisp outlines
- flat clean shading
- bright but not overly detailed
- should match the same visual universe as a simple stickman comedy brand

Composition:
- vertical 9:16 framing
- keep the middle area open for character placement
- balanced layout
- suitable for repeated use in multiple short videos
"""

result = client.images.generate(
    model="gpt-image-2",
    prompt=prompt,
    size="1024x1536"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

os.makedirs("assets/backgrounds", exist_ok=True)

output_path = f"assets/backgrounds/{bg_name}.png"

with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"Background saved to: {output_path}")
