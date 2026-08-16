import os
import sys
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

if len(sys.argv) < 2:
    raise ValueError("Please provide an expression name, e.g. happy, sad, angry")

expression = sys.argv[1].strip().lower()

EXPRESSION_MAP = {
    "happy": {
        "face": "happy expression with a cheerful smile",
        "pose": "standing with slightly raised arms"
    },
    "sad": {
        "face": "sad expression with teary eyes and a downturned mouth",
        "pose": "standing with slouched shoulders and lowered arms"
    },
    "angry": {
        "face": "angry expression with narrowed eyes and a frustrated mouth",
        "pose": "standing with clenched fists"
    },
    "shocked": {
        "face": "shocked expression with wide eyes and open mouth",
        "pose": "standing with both arms slightly raised in surprise"
    },
    "sleepy": {
        "face": "sleepy expression with half-closed eyes and a tired mouth",
        "pose": "standing lazily with drooping arms"
    }
}

if expression not in EXPRESSION_MAP:
    raise ValueError(f"Unsupported expression: {expression}")

face_desc = EXPRESSION_MAP[expression]["face"]
pose_desc = EXPRESSION_MAP[expression]["pose"]

prompt = f"""
Create the same original K-Stick character with a {expression} expression.

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

Expression details:
- {face_desc}

Pose details:
- {pose_desc}

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
    prompt=prompt,
    size="1024x1536"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

os.makedirs("assets/expressions", exist_ok=True)

output_path = f"assets/expressions/k_stick_{expression}.png"

with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"{expression} expression saved to: {output_path}")
