import os
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

CHARACTER_PROMPT = """
Create a clean, original, reusable cartoon stickman character for a short-form comedy brand.

Character name: K-Stick.

Character design:
- simple black stickman body
- perfectly round white face
- large expressive black eyes
- tiny simple mouth
- signature bright red baseball cap
- no logos
- no copyrighted character resemblance
- friendly, slightly confused personality
- highly consistent simple proportions
- clean thick outlines
- minimal details
- easy to animate
- family-friendly
- full body visible
- standing in a neutral relaxed pose
- facing slightly toward camera

Visual style:
- polished modern 2D cartoon
- simple viral social-media animation aesthetic
- crisp outlines
- flat clean shading
- professional character-sheet quality
- no text
- no watermark

Background:
plain light neutral background.

Vertical composition suitable for 9:16 video production.
"""

result = client.images.generate(
    model="gpt-image-2",
    prompt=CHARACTER_PROMPT,
    size="1024x1536"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

os.makedirs("assets/character", exist_ok=True)

output_path = "assets/character/k_stick_base.png"

with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"K-Stick base character saved to: {output_path}")
