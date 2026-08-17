import os
import sys
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

BASE_CHARACTER = "assets/character/k_stick_base.png"

POSES = {
    "standing": """
Standing naturally, facing the viewer, relaxed arms,
both feet visible, friendly neutral expression.
""",

    "sitting": """
Clearly sitting on the floor with knees bent,
body visibly lower than standing height,
hands resting naturally, slightly confused expression.
""",

    "sleeping": """
Lying down asleep on his side,
eyes closed, relaxed body,
peaceful sleeping expression.
""",

    "walking": """
Walking forward naturally,
one leg ahead of the other,
arms swinging,
casual happy expression.
""",

    "running": """
Running quickly,
one leg extended forward,
other leg behind,
arms moving dynamically,
slightly determined expression.
""",

    "pointing": """
Standing and clearly pointing to the right with one hand,
other arm relaxed,
curious expression.
""",

    "phone": """
Standing while holding and looking at a smartphone,
slightly curious expression.
""",

    "working": """
Sitting at a simple desk using a laptop,
focused expression.
Only include the small desk and laptop needed for the pose.
""",

    "hiding": """
Crouching slightly and trying to hide,
looking nervous and cautious.
""",

    "falling": """
Losing balance and falling backward,
arms spread,
wide shocked eyes,
dynamic comedy pose.
""",

    "confused": """
Standing with shoulders raised and both hands open,
clearly confused,
eyebrows and mouth showing uncertainty.
""",

    "celebrating": """
Jumping slightly with both arms raised,
very happy excited expression,
celebration pose.
"""
}


def main():
    if len(sys.argv) < 2:
        raise ValueError(
            "Provide pose name. Example: python generate_pose.py sitting"
        )

    pose_name = sys.argv[1].strip().lower()

    if pose_name not in POSES:
        raise ValueError(
            f"Unsupported pose: {pose_name}. "
            f"Available: {', '.join(POSES.keys())}"
        )

    if not os.path.exists(BASE_CHARACTER):
        raise FileNotFoundError(
            f"Base character not found: {BASE_CHARACTER}"
        )

    pose_instruction = POSES[pose_name]

    prompt = f"""
Use the supplied K-Stick reference image as the definitive character reference.

Create THE SAME K-Stick character.
Do not redesign him.

Identity MUST remain consistent:
- same perfectly round white head
- same black stick body proportions
- same large black expressive eyes
- same small mouth style
- same bright red baseball cap
- same cap shape
- same black line thickness
- same simple polished 2D cartoon style
- same overall proportions
- no clothing changes
- no new accessories unless specifically required by the pose
- no text
- no watermark
- only one K-Stick character

POSE:
{pose_instruction}

IMPORTANT:
Change only what is necessary to create the requested pose.
Preserve K-Stick's identity as closely as possible.

BACKGROUND:
Use a completely plain bright magenta background (#FF00FF).
No shadows, furniture, scenery, texture, gradients, or objects in the
background unless the requested pose explicitly needs a small prop.

Full body must remain visible.
Center the character.
Vertical portrait composition.
"""

    with open(BASE_CHARACTER, "rb") as base_image:
        result = client.images.edit(
            model="gpt-image-2",
            image=base_image,
            prompt=prompt,
            size="1024x1536",
            quality="medium",
            input_fidelity="high",
            output_format="png"
        )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    os.makedirs("assets/poses_raw", exist_ok=True)

    output_path = f"assets/poses_raw/k_stick_{pose_name}.png"

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Pose created: {output_path}")


if __name__ == "__main__":
    main()
