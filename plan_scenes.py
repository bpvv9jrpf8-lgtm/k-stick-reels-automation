import json
import os
import re

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


def contains_any(text, words):
    text = text.lower()

    for word in words:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            return True

    return False


def choose_pose(text):
    text = text.lower()

    # Action poses get priority over facial expressions.

    if contains_any(
        text,
        [
            "fall",
            "falls",
            "fell",
            "falling",
            "trip",
            "trips",
            "slips",
            "loses balance"
        ]
    ):
        return "falling"

    if contains_any(
        text,
        [
            "run",
            "runs",
            "running",
            "rush",
            "races"
        ]
    ):
        return "running"

    if contains_any(
        text,
        [
            "walk",
            "walks",
            "walking"
        ]
    ):
        return "walking"

    if contains_any(
        text,
        [
            "sit",
            "sits",
            "sitting",
            "sat",
            "floor",
            "chair"
        ]
    ):
        return "sitting"

    if contains_any(
        text,
        [
            "sleep",
            "sleeps",
            "sleeping",
            "asleep",
            "lies down",
            "lying",
            "bed"
        ]
    ):
        return "sleeping"

    if contains_any(
        text,
        [
            "point",
            "points",
            "pointing"
        ]
    ):
        return "pointing"

    if contains_any(
        text,
        [
            "phone",
            "smartphone",
            "texting",
            "texts",
            "scrolls"
        ]
    ):
        return "phone"

    if contains_any(
        text,
        [
            "laptop",
            "computer",
            "working",
            "work",
            "typing",
            "desk"
        ]
    ):
        return "working"

    if contains_any(
        text,
        [
            "hide",
            "hides",
            "hiding",
            "sneaks",
            "crouches"
        ]
    ):
        return "hiding"

    if contains_any(
        text,
        [
            "celebrates",
            "celebrate",
            "wins",
            "victory",
            "jumps happily"
        ]
    ):
        return "celebrating"

    if contains_any(
        text,
        [
            "confused",
            "confusion",
            "shrugs",
            "doesn't understand",
            "does not understand"
        ]
    ):
        return "confused"

    return None


def choose_expression(text):
    text = text.lower()

    if contains_any(
        text,
        [
            "shock",
            "shocked",
            "surprise",
            "surprised",
            "panic",
            "scared",
            "terrified"
        ]
    ):
        return "shocked"

    if contains_any(
        text,
        [
            "angry",
            "mad",
            "furious",
            "annoyed",
            "frustrated"
        ]
    ):
        return "angry"

    if contains_any(
        text,
        [
            "sad",
            "cry",
            "crying",
            "upset",
            "tears",
            "disappointed"
        ]
    ):
        return "sad"

    if contains_any(
        text,
        [
            "sleepy",
            "tired",
            "yawn",
            "yawning"
        ]
    ):
        return "sleepy"

    return "happy"


def choose_character_asset(text):
    pose = choose_pose(text)

    # If story clearly contains an action,
    # use the matching action pose.
    if pose and pose in POSE_FILES:
        return {
            "asset_type": "pose",
            "pose": pose,
            "expression": None,
            "character_asset": POSE_FILES[pose]
        }

    expression = choose_expression(text)

    return {
        "asset_type": "expression",
        "pose": "standing",
        "expression": expression,
        "character_asset": EXPRESSION_FILES[expression]
    }


def choose_background(story):
    requested = story.get(
        "background",
        ""
    ).lower()

    for key in BACKGROUND_FILES:
        if key in requested:
            return key

    all_text = " ".join(
        [
            story.get("scene_1", ""),
            story.get("scene_2", ""),
            story.get("scene_3", ""),
            story.get("twist_ending", "")
        ]
    ).lower()

    if contains_any(
        all_text,
        [
            "bedroom",
            "bed",
            "sleep",
            "alarm",
            "pillow"
        ]
    ):
        return "bedroom"

    if contains_any(
        all_text,
        [
            "classroom",
            "teacher",
            "student",
            "school",
            "exam"
        ]
    ):
        return "classroom"

    if contains_any(
        all_text,
        [
            "office",
            "work",
            "laptop",
            "desk",
            "boss"
        ]
    ):
        return "office"

    if contains_any(
        all_text,
        [
            "kitchen",
            "fridge",
            "food",
            "snack",
            "burger"
        ]
    ):
        return "kitchen"

    return "street"


def main():
    if not os.path.exists(STORY_FILE):
        raise FileNotFoundError(
            "latest_story.json not found"
        )

    with open(
        STORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        story = json.load(f)

    bg_key = choose_background(story)

    background_asset = BACKGROUND_FILES[
        bg_key
    ]

    scene_texts = [
        story.get("scene_1", ""),
        story.get("scene_2", ""),
        story.get("scene_3", ""),
        story.get("twist_ending", "")
    ]

    durations = [
        3.5,
        3.5,
        3.5,
        4.5
    ]

    plan = {
        "topic": story.get("topic", ""),
        "hook_text": story.get(
            "hook_text",
            "WAIT FOR IT"
        ),
        "background": bg_key,
        "background_asset": background_asset,
        "video_title": story.get(
            "video_title",
            ""
        ),
        "facebook_caption": story.get(
            "facebook_caption",
            ""
        ),
        "youtube_description": story.get(
            "youtube_description",
            ""
        ),
        "hashtags": story.get(
            "hashtags",
            []
        ),
        "scenes": []
    }

    for index, text in enumerate(
        scene_texts
    ):
        character = choose_character_asset(
            text
        )

        plan["scenes"].append(
            {
                "scene_number": index + 1,
                "duration_seconds": durations[index],
                "story_text": text,
                "background_asset": background_asset,
                "character_asset": character[
                    "character_asset"
                ],
                "asset_type": character[
                    "asset_type"
                ],
                "pose": character[
                    "pose"
                ],
                "expression": character[
                    "expression"
                ]
            }
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            plan,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        json.dumps(
            plan,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "\nScene plan saved as scene_plan.json"
    )


if __name__ == "__main__":
    main()
