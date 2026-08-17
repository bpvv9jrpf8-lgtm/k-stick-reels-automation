import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

STORY_FILE = "latest_story.json"
HISTORY_FILE = "used_topics.json"

ALLOWED_BACKGROUNDS = ["bedroom", "office", "classroom", "kitchen", "street"]
ALLOWED_POSES = [
    "standing", "sitting", "sleeping", "walking", "running", "pointing",
    "phone", "working", "hiding", "falling", "confused", "celebrating"
]
ALLOWED_EXPRESSIONS = ["happy", "sad", "angry", "shocked", "sleepy"]
ALLOWED_PROPS = [
    "none", "apple", "phone", "laptop", "chair", "pillow", "alarm_clock",
    "shopping_bag", "burger", "book", "stool", "scanner", "kiosk"
]


def load_used_topics():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_used_topics(topics):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(topics[-200:], f, indent=2, ensure_ascii=False)


def clamp_words(text, maximum):
    return " ".join(str(text or "").strip().split()[:maximum])


def validate_story(story):
    if not isinstance(story, dict):
        raise ValueError("Story is not a JSON object")

    story["hook_text"] = clamp_words(story.get("hook_text", "WAIT FOR IT"), 4).upper()
    story["reaction_text"] = clamp_words(story.get("reaction_text", "WHAT?!"), 4)

    background = str(story.get("background", "street")).lower().strip()
    if background not in ALLOWED_BACKGROUNDS:
        background = "street"
    story["background"] = background

    scenes = story.get("scenes")
    if not isinstance(scenes, list) or len(scenes) != 4:
        raise ValueError("Story must contain exactly 4 scenes")

    cleaned = []
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise ValueError(f"Scene {index} is invalid")

        pose = str(scene.get("pose", "standing")).lower().strip()
        expression = str(scene.get("expression", "happy")).lower().strip()
        prop = str(scene.get("prop", "none")).lower().strip()

        if pose not in ALLOWED_POSES:
            pose = "standing"
        if expression not in ALLOWED_EXPRESSIONS:
            expression = "happy"
        if prop not in ALLOWED_PROPS:
            prop = "none"

        cleaned.append({
            "action": str(scene.get("action", "K-Stick reacts."))[:300],
            "caption": clamp_words(scene.get("caption", "WAIT"), 5),
            "pose": pose,
            "expression": expression,
            "prop": prop,
        })

    story["scenes"] = cleaned

    narration = str(story.get("narration", "")).strip()
    story["narration"] = clamp_words(narration, 38)
    story["topic"] = str(story.get("topic", "K-Stick comedy"))[:120]
    story["video_title"] = str(story.get("video_title", story["topic"]))[:100]
    story["facebook_caption"] = str(story.get("facebook_caption", ""))[:500]
    story["youtube_description"] = str(story.get("youtube_description", ""))[:1000]

    hashtags = story.get("hashtags", [])
    if not isinstance(hashtags, list):
        hashtags = []
    story["hashtags"] = [str(x)[:40] for x in hashtags[:5]]

    return story


def generate_story(used_topics):
    used_text = "; ".join(used_topics[-40:]) if used_topics else "None yet"

    prompt = f"""
Create ONE original 15-second family-friendly K-Stick comedy reel.

K-Stick is a simple black stickman with a round white face, big expressive eyes,
and a red baseball cap. He is innocent, curious, and slightly unlucky.

IMPORTANT: This project uses a FIXED reusable asset library. You MUST only use
assets from the lists below. Never invent a prop, location, or pose outside them.

BACKGROUND — choose exactly ONE:
{', '.join(ALLOWED_BACKGROUNDS)}

POSES — choose one per scene:
{', '.join(ALLOWED_POSES)}

EXPRESSIONS — choose one per scene:
{', '.join(ALLOWED_EXPRESSIONS)}

PROPS — choose zero or one per scene:
{', '.join(ALLOWED_PROPS)}

Already-used topics to avoid:
{used_text}

STORY RULES:
- Exactly 4 scenes.
- The same background is used for all four scenes.
- Each scene must be visually understandable using its selected pose and prop.
- Do NOT describe liquid splashes, clothing changes, crowds, complex machines,
  broken objects, morphing, or any object that is not in the prop list.
- Prefer simple physical comedy: phone mistakes, alarm problems, burger mishaps,
  book surprises, chair/stool fails, shopping-bag confusion, laptop mistakes.
- Scene 4 must deliver a clear visual punchline.
- No copyrighted characters, brands, politics, violence, or unsafe behavior.

TEXT RULES:
- hook_text: maximum 4 short words.
- each caption: maximum 5 short words.
- reaction_text: 1–4 words.
- narration: maximum 38 words total, natural and funny.

Return ONLY valid JSON with exactly this structure:
{{
  "topic": "",
  "hook_text": "",
  "background": "street",
  "scenes": [
    {{"action":"", "caption":"", "pose":"standing", "expression":"happy", "prop":"none"}},
    {{"action":"", "caption":"", "pose":"standing", "expression":"happy", "prop":"none"}},
    {{"action":"", "caption":"", "pose":"standing", "expression":"happy", "prop":"none"}},
    {{"action":"", "caption":"", "pose":"standing", "expression":"shocked", "prop":"none"}}
  ],
  "narration": "",
  "reaction_text": "",
  "video_title": "",
  "facebook_caption": "",
  "youtube_description": "",
  "hashtags": ["#KStick", "#FunnyCartoon", "#Shorts", "#Comedy"]
}}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )

    raw = response.output_text.strip().replace("```json", "").replace("```", "").strip()
    return validate_story(json.loads(raw))


def main():
    used_topics = load_used_topics()

    last_error = None
    story = None
    for attempt in range(3):
        try:
            story = generate_story(used_topics)
            break
        except Exception as exc:
            last_error = exc
            print(f"Story attempt {attempt + 1} failed: {exc}")

    if story is None:
        raise RuntimeError(f"Could not generate a valid story: {last_error}")

    with open(STORY_FILE, "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2, ensure_ascii=False)

    print(json.dumps(story, indent=2, ensure_ascii=False))

    topic = story["topic"].strip()
    if topic and topic not in used_topics:
        used_topics.append(topic)
        save_used_topics(used_topics)


if __name__ == "__main__":
    main()
