import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

STORY_FILE = "latest_story.json"

AUDIO_DIR = Path("audio")
NARRATOR_FILE = AUDIO_DIR / "narrator.mp3"
REACTION_FILE = AUDIO_DIR / "reaction.mp3"


def generate_speech(text, output_file, voice, instructions, speed=1.0):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions=instructions,
        response_format="mp3",
        speed=speed
    ) as response:
        response.stream_to_file(output_file)


def main():
    if not os.path.exists(STORY_FILE):
        raise FileNotFoundError("latest_story.json not found")

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story = json.load(f)

    narration = story.get("narration", "").strip()

    if not narration:
        narration = " ".join([
            story.get("scene_1", ""),
            story.get("scene_2", ""),
            story.get("scene_3", ""),
            story.get("twist_ending", "")
        ])

    # Keep narration short
    narration_words = narration.split()

    if len(narration_words) > 38:
        narration = " ".join(narration_words[:38])

    reaction = story.get(
        "reaction_text",
        "What?!"
    ).strip()

    AUDIO_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    generate_speech(
        narration,
        NARRATOR_FILE,
        voice="marin",
        instructions=(
            "Speak like an energetic funny short-form cartoon narrator. "
            "Natural, playful, fast but very clear. "
            "Build anticipation and emphasize the final joke."
        ),
        speed=1.08
    )

    generate_speech(
        reaction,
        REACTION_FILE,
        voice="cedar",
        instructions=(
            "Speak as a funny innocent cartoon character. "
            "Very short, expressive, surprised, playful."
        ),
        speed=1.05
    )

    print(f"Narrator: {NARRATOR_FILE}")
    print(f"Reaction: {REACTION_FILE}")
    print(f"Reaction text: {reaction}")


if __name__ == "__main__":
    main()
