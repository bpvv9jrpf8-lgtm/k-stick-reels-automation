import json
import os

STORY_FILE = "latest_story.json"
OUTPUT_FILE = "scene_plan.json"

BACKGROUND_FILES = {
    "bedroom": "assets/backgrounds/bedroom.png",
    "office": "assets/backgrounds/office.png",
    "classroom": "assets/backgrounds/classroom.png",
    "kitchen": "assets/backgrounds/kitchen.png",
    "street": "assets/backgrounds/street.png",
}

EXPRESSION_FILES = {
    "happy": "assets/transparent/k_stick_happy_transparent.png",
    "sad": "assets/transparent/k_stick_sad_transparent.png",
    "angry": "assets/transparent/k_stick_angry_transparent.png",
    "shocked": "assets/transparent/k_stick_shocked_transparent.png",
    "sleepy": "assets/transparent/k_stick_sleepy_transparent.png",
}

POSE_FILES = {
    "standing": "assets/poses/k_stick_standing.png",
    "sitting": "assets/poses/k_stick_sitting.png",
    "sleeping": "assets/poses/k_stick_sleeping.png",
    "walking": "assets/poses/k_stick_walking.png",
    "running": "assets/poses/k_stick_running.png",
    "pointing": "assets/poses/k_stick_pointing.png",
    "phone": "assets/poses/k_stick_phone.png",
    "working": "assets/poses/k_stick_working.png",
    "hiding": "assets/poses/k_stick_hiding.png",
    "falling": "assets/poses/k_stick_falling.png",
    "confused": "assets/poses/k_stick_confused.png",
    "celebrating": "assets/poses/k_stick_celebrating.png",
}

PROP_FILES = {
    "apple": "assets/props/apple.png",
    "phone": "assets/props/phone.png",
    "laptop": "assets/props/laptop.png",
    "chair": "assets/props/chair.png",
    "pillow": "assets/props/pillow.png",
    "alarm_clock": "assets/props/alarm_clock.png",
    "shopping_bag": "assets/props/shopping_bag.png",
    "burger": "assets/props/burger.png",
    "book": "assets/props/book.png",
    "stool": "assets/props/stool.png",
    "scanner": "assets/props/scanner.png",
    "kiosk": "assets/props/kiosk.png",
}

DURATIONS = [3.25, 3.25, 3.25, 5.25]


def require_file(path, label):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Missing {label}: {path}")
    return path


def main():
    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story = json.load(f)

    background_name = story.get("background", "street")
    background_asset = require_file(
        BACKGROUND_FILES.get(background_name),
        f"background '{background_name}'",
    )

    scenes = story.get("scenes", [])
    if len(scenes) != 4:
        raise ValueError("latest_story.json must contain exactly 4 scenes")

    plan = {
        "topic": story.get("topic", ""),
        "hook_text": " ".join(story.get("hook_text", "WAIT FOR IT").split()[:4]),
        "reaction_text": " ".join(story.get("reaction_text", "WHAT?!").split()[:4]),
        "reaction_start": 11.0,
        "background": background_name,
        "background_asset": background_asset,
        "video_title": story.get("video_title", ""),
        "facebook_caption": story.get("facebook_caption", ""),
        "youtube_description": story.get("youtube_description", ""),
        "hashtags": story.get("hashtags", []),
        "scenes": [],
    }

    for index, scene in enumerate(scenes):
        pose = scene.get("pose", "standing")
        expression = scene.get("expression", "happy")
        prop = scene.get("prop", "none")

        pose_path = POSE_FILES.get(pose)
        expression_path = EXPRESSION_FILES.get(expression)

        # Prefer an action pose when it exists. If a pose file is missing, fall back
        # to the expression asset instead of crashing the reel build.
        if pose_path and os.path.exists(pose_path):
            character_asset = pose_path
            asset_type = "pose"
        else:
            character_asset = require_file(
                expression_path,
                f"expression '{expression}'",
            )
            asset_type = "expression"

        prop_asset = None
        if prop != "none":
            candidate = PROP_FILES.get(prop)
            if candidate and os.path.exists(candidate):
                prop_asset = candidate
            else:
                print(f"Warning: prop asset '{prop}' missing; scene will render without it")
                prop = "none"

        plan["scenes"].append({
            "scene_number": index + 1,
            "duration_seconds": DURATIONS[index],
            "story_text": scene.get("action", ""),
            "short_caption": " ".join(scene.get("caption", "").split()[:5]),
            "background_asset": background_asset,
            "character_asset": character_asset,
            "asset_type": asset_type,
            "pose": pose,
            "expression": expression,
            "prop": prop,
            "prop_asset": prop_asset,
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(json.dumps(plan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
