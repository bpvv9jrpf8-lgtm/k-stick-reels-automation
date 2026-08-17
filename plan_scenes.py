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


def contains_any(text, words):
    text = text.lower()

    for word in words:
        if word in text:
            return True

    return False


def choose_pose(text):
    text = text.lower()

    if contains_any(
        text,
        [
            "falling",
            "falls",
            "fell",
            "trips",
            "slips",
            "loses balance"
        ]
    ):
        return "falling"

    if contains_any(
        text,
        [
            "running",
            "runs",
            "rushes",
            "races"
        ]
    ):
        return "running"

    if contains_any(
        text,
        [
            "walking",
            "walks"
        ]
    ):
        return "walking"

    if contains_any(
        text,
        [
            "sitting",
            "sits",
            "sat",
            "sit down",
            "sits on the floor"
        ]
    ):
        return "sitting"

    if contains_any(
        text,
        [
            "sleeping",
            "sleeps",
            "asleep",
            "lying down",
            "lies down"
        ]
    ):
        return "sleeping"

    if contains_any(
        text,
        [
            "pointing",
            "points at",
            "points to"
        ]
    ):
        return "pointing"

    if contains_any(
        text,
        [
            "holding his phone",
            "looks at his phone",
            "smartphone",
            "texting"
        ]
    ):
        return "phone"

    if contains_any(
        text,
        [
            "working",
            "typing",
            "using laptop",
            "using a laptop"
        ]
    ):
        return "working"

    if contains_any(
        text,
        [
            "hiding",
            "hides",
            "crouches",
            "sneaks"
        ]
    ):
        return "hiding"

    if contains_any(
        text,
        [
            "celebrates",
            "celebrating",
            "victory",
            "wins"
        ]
    ):
        return "celebrating"

    if contains_any(
        text,
        [
            "confused",
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
            "shocked",
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
            "yawn"
        ]
    ):
        return "sleepy"

    return "happy"


def choose_prop(text):
    text = text.lower()

    rules = {
        "apple": [
            "apple"
        ],

        "phone": [
            "phone",
            "smartphone"
        ],

        "laptop": [
            "laptop",
            "computer"
        ],

        "chair": [
            "chair"
        ],

        "pillow": [
            "pillow"
        ],

        "alarm_clock": [
            "alarm",
            "alarm clock"
        ],

        "shopping_bag": [
            "shopping bag",
            "grocery bag",
            "bagging"
        ],

        "burger": [
            "burger",
            "hamburger"
        ],

        "book": [
            "book"
        ],

        "stool": [
            "stool"
        ],

        "scanner": [
            "scanner",
            "barcode",
            "scans",
            "scan"
        ],

        "kiosk": [
            "kiosk",
            "self-checkout",
            "checkout"
        ],
    }

    for prop_name, keywords in rules.items():
        for keyword in keywords:
            if keyword in text:
                return prop_name

    return None


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
            "boss"
        ]
    ):
        return "office"

    if contains_any(
        all_text,
        [
            "kitchen",
            "fridge",
            "burger",
            "snack"
        ]
    ):
        return "kitchen"

    return "street"


def choose_character(text):
    pose = choose_pose(text)

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
        "character_asset": EXPRESSION_FILES[
            expression
        ]
    }


def shorten_caption(text):
    words = text.split()

    if len(words) <= 6:
        return text

    return " ".join(words[:6]) + "..."


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

    background_key = choose_background(
        story
    )

    background_asset = BACKGROUND_FILES[
        background_key
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

    hook = story.get(
        "hook_text",
        "WAIT FOR IT"
    )

    hook_words = hook.split()

    if len(hook_words) > 6:
        hook = " ".join(hook_words[:6])

    plan = {
        "topic": story.get(
            "topic",
            ""
        ),

        "hook_text": hook,

        "background": background_key,

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
        character = choose_character(
            text
        )

        prop_name = choose_prop(
            text
        )

        prop_asset = None

        if prop_name:
            prop_asset = PROP_FILES.get(
                prop_name
            )

        plan["scenes"].append(
            {
                "scene_number": index + 1,

                "duration_seconds": durations[
                    index
                ],

                "story_text": text,

                "short_caption": shorten_caption(
                    text
                ),

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
                ],

                "prop": prop_name,

                "prop_asset": prop_asset
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
        "\nScene plan saved successfully."
    )


if __name__ == "__main__":
    main()
