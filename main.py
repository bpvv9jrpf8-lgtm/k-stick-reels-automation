import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def load_used_topics():
    if not os.path.exists("used_topics.json"):
        return []

    try:
        with open("used_topics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_used_topics(topics):
    with open("used_topics.json", "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)


def main():
    used_topics = load_used_topics()

    used_text = ", ".join(used_topics[-50:]) if used_topics else "None"

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=f"""
Create ONE original 15-second funny K-Stick cartoon story.

K-STICK:
- simple black stick body
- round white face
- big expressive eyes
- red baseball cap
- innocent but unlucky personality
- family friendly

Already used topics:
{used_text}

RULES:
- Do not repeat previous topics
- Keep the story visually simple
- Use reusable environments:
  bedroom, office, classroom, kitchen, street
- Prefer reusable props:
  apple, phone, laptop, chair, pillow, alarm clock,
  shopping bag, burger, book, stool, scanner, kiosk
- Every scene must describe a visible physical action
- Avoid actions that cannot be shown with a static pose
- Make the final scene a clear visual comedy twist

HOOK RULE:
- Maximum 4 words
- Curiosity driven
- No punctuation-heavy sentence
- Example style:
  "BAD IDEA"
  "WAIT FOR IT"
  "HE MESSED UP"

CAPTION RULE:
Each scene must also have a short on-screen caption:
- maximum 5 words
- readable in one or two lines
- do not narrate the entire action

REACTION RULE:
Create ONE very short K-Stick spoken reaction:
- 1 to 4 words
- funny
- happens near the twist
Examples:
"What?!"
"Oh no!"
"Seriously?"
"Not again!"

Narration:
- maximum about 35 words total
- sounds like a funny human narrator
- clear setup and payoff

Return ONLY valid JSON:

{{
  "topic": "",
  "hook_text": "",
  "background": "",
  "scene_1": "",
  "scene_1_caption": "",
  "scene_2": "",
  "scene_2_caption": "",
  "scene_3": "",
  "scene_3_caption": "",
  "twist_ending": "",
  "twist_caption": "",
  "narration": "",
  "reaction_text": "",
  "video_title": "",
  "facebook_caption": "",
  "youtube_description": "",
  "hashtags": ["", "", "", ""]
}}
"""
    )

    raw = response.output_text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    story = json.loads(raw)

    # Hard safety limits
    story["hook_text"] = " ".join(
        story.get("hook_text", "WAIT FOR IT").split()[:4]
    )

    story["reaction_text"] = " ".join(
        story.get("reaction_text", "What?!").split()[:4]
    )

    with open("latest_story.json", "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2, ensure_ascii=False)

    print(json.dumps(story, indent=2, ensure_ascii=False))

    topic = story.get("topic", "").strip()

    if topic and topic not in used_topics:
        used_topics.append(topic)
        save_used_topics(used_topics)


if __name__ == "__main__":
    main()
