import os
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT = """
Create the same original K-Stick character in a happy expression.

K-Stick design must stay consistent:
- simple black stickman body
- perfectly round white face
- large expressive black eyes
- tiny simple mouth
- signature bright red baseball cap
- clean thick outlines
- flat clean shading
- family-friendly
- full body visible

Pose:
- standing
- happy expression
- small cheerful smile
- slightly raised arms

Style:
- polished modern 2D cartoon
- simple viral social-media animation aesthetic
- crisp outlines
- no text
- no watermark

Background:
plain light neutral background.

Vertical composition suitable for 9:16 video production.
"""

result = client.images.generate(
    model="gpt-image-2",
    prompt=PROMPT,
    size="1024x1536"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

os.makedirs("assets/expressions", exist_ok=True)

output_path = "assets/expressions/k_stick_happy.png"

with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"Happy expression saved to: {output_path}")
