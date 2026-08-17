import json
import os

STORY_FILE = "latest_story.json"
OUTPUT_FILE = "scene_plan.json"

EXPRESSION_FILES = {
    "happy": "assets/transparent/k_stick_happy_transparent.png",
    "sad": "assets/transparent/k_stick_sad_transparent.png",
    "angry": "assets/transparent/k_stick_angry_transparent.png",
    "shocked": "assets/transparent/k_stick_shocked_transparent.png",
    "sleepy": "assets/transparent/k_stick_sleepy_transparent.png",
}


BACKGROUND_FILES = {
    "bedroom": "assets/backgrounds/bedroom.png",
    "office": "assets/backgrounds/office.png",
    "classroom": "assets/backgrounds/classroom.png",
    "kitchen": "assets/backgrounds/kitchen.png",
    "street": "assets/backgrounds/street.png",
}


def choose_expression(text):
    text = text.lower()

    if any(word in text for word in ["shock", "surprise", "scared", "wide eyes"]):
        return "shocked"

    if any(word in text for word in ["angry", "mad", "frustrated"]):
        return "angry"

    if any(word in text for word in ["sad", "cry", "upset"]):
        return "sad"

    if any(word in text for word in ["sleep", "tired", "bed"]):
        return "sleepy"

    return "happy"


def choose_background(story):
    bg = story.get("background", "").lower()

    for key in BACKGROUND_FILES:
        if key in bg:
            return key

    combined = " ".join([
        story.get("scene_1", ""),
        story.get("scene_2", ""),
        story.get("scene_3", ""),
        story.get("twist_ending", "")
    ]).lower()

    if any(word in combined for word in ["bed", "sleep", "alarm", "pillow"]):
        return "bedroom"

    if any(word in combined for word in ["office", "desk", "work", "laptop"]):
        return "office"

    if any(word in combined for word in ["school", "exam", "teacher", "class"]):
        return "classroom"

    if any(word in combined for word in ["food", "fridge", "burger", "kitchen"]):
        return "kitchen"

    return "street"


def main():
    if not os.path.exists(STORY_FILE):
        raise FileNotFoundError("latest_story.json not found")

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story = json.load(f)

    background = choose_background(story)

    scene_texts = [
        story.get("scene_1", ""),
        story.get("scene_2", ""),
        story.get("scene_3", ""),
        story.get("twist_ending", "")
    ]

    scene_plan = {
        "topic": story.get("topic", ""),
        "hook_text": story.get("hook_text", ""),
        "background": BACKGROUND_FILES[background],
        "scenes": []
    }

    for index, text in enumerate(scene_texts, start=1):
        expression = choose_expression(text)

        scene_plan["scenes"].append({
            "scene_number": index,
            "duration_seconds": 3 if index < 4 else 4,
            "story_text": text,
            "character_asset": EXPRESSION_FILES[expression],
            "background_asset": BACKGROUND_FILES[background],
            "expression": expression
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scene_plan, f, indent=2, ensure_ascii=False)

    print("=== SCENE PLAN ===")
    print(json.dumps(scene_plan, indent=2, ensure_ascii=False))
    print("\nSaved as scene_plan.json")


if __name__ == "__main__":
    main()
