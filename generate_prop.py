import os
import sys
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROPS = {
    "apple": "one simple shiny red apple, isolated",
    "phone": "one simple modern smartphone, isolated",
    "laptop": "one simple open laptop, isolated",
    "chair": "one simple wooden chair, isolated",
    "pillow": "one simple soft pillow, isolated",
    "alarm_clock": "one simple cartoon alarm clock, isolated",
    "shopping_bag": "one simple grocery shopping bag, isolated",
    "burger": "one simple cartoon burger, isolated",
    "book": "one simple closed book, isolated",
    "stool": "one simple tiny stool, isolated",
    "scanner": "one simple self-checkout barcode scanner, isolated",
    "kiosk": "one simple self-checkout kiosk screen, isolated"
}

if len(sys.argv) < 2:
    raise ValueError("Provide prop name")

prop_name = sys.argv[1].strip().lower()

if prop_name not in PROPS:
    raise ValueError(
        f"Unsupported prop: {prop_name}. "
        f"Available: {', '.join(PROPS.keys())}"
    )

prompt = f"""
Create a reusable prop asset for the K-Stick cartoon comedy series.

Object:
{PROPS[prop_name]}

Style:
- polished modern 2D cartoon
- thick clean outlines
- simple flat shading
- bright but not over-detailed
- family-friendly
- same visual universe as a simple viral stickman cartoon
- no character
- no text
- no watermark
- object centered
- full object visible

Background:
solid bright magenta #FF00FF
"""

result = client.images.generate(
    model="gpt-image-2",
    prompt=prompt,
    size="1024x1024",
    quality="medium"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

os.makedirs("assets/props_raw", exist_ok=True)

output_path = f"assets/props_raw/{prop_name}.png"

with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"Saved prop: {output_path}")
