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


def has(text, *terms):
    text = text.lower()
    return any(term in text for term in terms)


def choose_pose(text):
    if has(text, "fall", "falls", "fell", "slip", "trip"):
        return "falling"

    if has(text, "run", "runs", "running", "rush"):
        return "running"

    if has(text, "walk", "walks", "walking"):
        return "walking"

    if has(text, "sit", "sits", "sitting", "sat"):
        return "sitting"

    if has(text, "sleep", "sleeps", "sleeping", "lies down", "lying"):
        return "sleeping"

    if has(text, "point", "points", "pointing"):
        return "pointing"

    if has(text, "phone", "smartphone", "texting"):
        return "phone"

    if has(text, "laptop", "typing", "working at"):
        return "working"

    if has(text, "hide", "hides", "hiding", "crouch"):
        return "hiding"

    if has(text, "celebrate", "celebrates", "victory", "wins"):
        return "celebrating"

    if has(text, "confused", "shrug"):
        return "confused"

    return None


def choose_expression(text):
    if has(text, "shock", "surprise", "panic", "scared"):
        return "shocked"

    if has(text, "angry", "mad", "furious", "annoyed"):
        return "angry"

    if has(text, "sad", "cry", "upset", "tears"):
        return "sad"

    if has(text, "sleepy", "tired", "yawn"):
        return "sleepy"

    return "happy"


def choose_character(text):
    pose = choose_pose(text)

    if pose and os.path.exists(POSE_FILES.get(pose, "")):
        return POSE_FILES[pose], pose, None

    expression = choose_expression(text)

    return (
        EXPRESSION_FILES[expression],
        "standing",
        expression
    )


def choose_prop(text):
    rules = [
        ("apple", ["apple"]),
        ("phone", ["phone", "smartphone"]),
        ("laptop", ["laptop", "computer"]),
        ("chair", ["chair"]),
        ("pillow", ["pillow"]),
        ("alarm_clock", ["alarm", "clock"]),
        ("shopping_bag", ["bagging", "shopping bag", "grocery bag"]),
        ("burger", ["burger"]),
        ("book", ["book"]),
        ("stool", ["stool"]),
        ("scanner", ["scanner", "barcode", "scan"]),
        ("kiosk", ["kiosk", "checkout"]),
    ]

    lowered = text.lower()

    for name, keywords in rules:
        if any(keyword in lowered for keyword in keywords):
            path = PROP_FILES[name]

            if os.path.exists(path):
                return name, path

    return None, None


def choose_background(story):
    requested = story.get("background", "").lower()

    for key in BACKGROUND_FILES:
        if key in requested:
            return key

    text = " ".join([
        story.get("scene_1", ""),
        story.get("scene_2", ""),
        story.get("scene_3", ""),
        story.get("twist_ending", "")
    ]).lower()

    if has(text, "bed", "sleep", "alarm", "pillow"):
        return "bedroom"

    if has(text, "class", "teacher", "school", "exam"):
        return "classroom"

    if has(text, "office", "boss", "work", "laptop"):
        return "office"

    if has(text, "kitchen", "fridge", "burger", "food"):
        return "kitchen"

    return "street"


def caption_limit(text):
    words = text.split()[:5]
    return " ".join(words)


def main():
    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story = json.load(f)

    bg_key = choose_background(story)
    bg_asset = BACKGROUND_FILES[bg_key]

    scene_data = [
        (
            story.get("scene_1", ""),
            story.get("scene_1_caption", "")
        ),
        (
            story.get("scene_2", ""),
            story.get("scene_2_caption", "")
        ),
        (
            story.get("scene_3", ""),
            story.get("scene_3_caption", "")
        ),
        (
            story.get("twist_ending", ""),
            story.get("twist_caption", "")
        ),
    ]

    durations = [
        3.3,
        3.3,
        3.3,
        5.1
    ]

    plan = {
        "topic": story.get("topic", ""),
        "hook_text": " ".join(
            story.get("hook_text", "WAIT FOR IT").split()[:4]
        ),
        "reaction_text": story.get("reaction_text", "What?!"),
        "reaction_start": 11.0,
        "background_asset": bg_asset,
        "video_title": story.get("video_title", ""),
        "facebook_caption": story.get("facebook_caption", ""),
        "youtube_description": story.get("youtube_description", ""),
        "hashtags": story.get("hashtags", []),
        "scenes": []
    }

    for index, (text, caption) in enumerate(scene_data):
        character_asset, pose, expression = choose_character(text)

        prop_name, prop_asset = choose_prop(text)

        plan["scenes"].append({
            "scene_number": index + 1,
            "duration_seconds": durations[index],
            "story_text": text,
            "short_caption": caption_limit(caption),
            "background_asset": bg_asset,
            "character_asset": character_asset,
            "pose": pose,
            "expression": expression,
            "prop": prop_name,
            "prop_asset": prop_asset
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            plan,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(json.dumps(plan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
