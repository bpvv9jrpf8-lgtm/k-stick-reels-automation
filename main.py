import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def main():
    print("K-Stick structured story generation started.")

    response = client.responses.create(
        model="gpt-5.6-luna",
        input="""
Create ONE original 15-second funny stickman reel concept.

Main character:
- Name: K-Stick
- Simple black stickman body
- Round white face
- Big expressive eyes
- Signature red cap
- Family-friendly personality

Rules:
- Must be simple enough for low-cost automation
- Use mostly reusable backgrounds and props
- Include a fast setup, problem, twist, and funny ending
- No copyrighted characters
- No politics
- No unsafe content
- No complicated crowd scenes

Return ONLY valid JSON in this exact structure:

{
  "topic": "",
  "hook_text": "",
  "background": "",
  "main_expression": "",
  "main_pose": "",
  "prop": "",
  "scene_1": "",
  "scene_2": "",
  "scene_3": "",
  "twist_ending": "",
  "video_title": "",
  "facebook_caption": "",
  "youtube_description": "",
  "hashtags": ["", "", "", ""],
  "image_prompt": "",
  "motion_prompt": ""
}
"""
    )

    raw = response.output_text.strip()

    # Remove accidental markdown fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        story = json.loads(raw)
    except json.JSONDecodeError:
        print("ERROR: Model did not return valid JSON.")
        print(raw)
        raise

    print("\n=== K-STICK STORY ===")
    print(json.dumps(story, indent=2, ensure_ascii=False))

    # Save the latest story for later automation steps
    with open("latest_story.json", "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2, ensure_ascii=False)

    print("\nSaved as latest_story.json")


if __name__ == "__main__":
    main()
