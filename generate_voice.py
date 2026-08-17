import json
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

STORY_FILE = "latest_story.json"
OUTPUT_DIR = Path("audio")
OUTPUT_FILE = OUTPUT_DIR / "voiceover.mp3"

def main():
    if not os.path.exists(STORY_FILE):
        raise FileNotFoundError("latest_story.json not found")

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story = json.load(f)

    # Keep narration short enough for ~15 seconds
    narration = " ".join([
        story.get("scene_1", ""),
        story.get("scene_2", ""),
        story.get("scene_3", ""),
        story.get("twist_ending", "")
    ]).strip()

    # Safety cap so the voiceover does not become too long
    words = narration.split()
    if len(words) > 42:
        narration = " ".join(words[:42])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating voiceover:")
    print(narration)

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="marin",
        input=narration,
        instructions=(
            "Speak like a funny, energetic short-form cartoon narrator. "
            "Fast but clear. Playful timing. Slight surprise before the ending. "
            "Do not sound robotic."
        ),
        response_format="mp3"
    ) as response:
        response.stream_to_file(OUTPUT_FILE)

    print(f"Voiceover saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
