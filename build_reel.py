import json
import os
import subprocess
import textwrap

SCENE_PLAN = "scene_plan.json"
OUTPUT_DIR = "output"
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "k_stick_reel.mp4")

WIDTH = 1080
HEIGHT = 1920
FPS = 30


def run(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def escape_drawtext(text):
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
    )


def main():
    if not os.path.exists(SCENE_PLAN):
        raise FileNotFoundError("scene_plan.json not found")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    with open(SCENE_PLAN, "r", encoding="utf-8") as f:
        plan = json.load(f)

    hook_text = plan.get("hook_text", "WAIT FOR END 😂")
    scenes = plan.get("scenes", [])

    scene_files = []

    for scene in scenes:
        num = scene["scene_number"]
        duration = scene["duration_seconds"]
        background = scene["background_asset"]
        character = scene["character_asset"]
        story_text = scene["story_text"]

        out_file = f"temp/scene_{num}.mp4"
        scene_files.append(out_file)

        subtitle = escape_drawtext(
            "\n".join(textwrap.wrap(story_text, width=34))
        )

        hook = escape_drawtext(hook_text)

        filter_complex = (
            f"[0:v]scale={WIDTH}:{HEIGHT},setsar=1[bg];"
            f"[1:v]scale=520:-1[char];"
            f"[bg][char]overlay=(W-w)/2:H-h-260,"
            f"drawtext=text='{hook}':"
            f"fontcolor=white:fontsize=72:"
            f"borderw=6:bordercolor=black:"
            f"x=(w-text_w)/2:y=110,"
            f"drawtext=text='{subtitle}':"
            f"fontcolor=white:fontsize=54:"
            f"borderw=5:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-330:"
            f"enable='between(t,0,{duration})'"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", background,
            "-loop", "1",
            "-t", str(duration),
            "-i", character,
            "-filter_complex", filter_complex,
            "-r", str(FPS),
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-t", str(duration),
            out_file
        ]

        run(cmd)

    concat_file = "temp/concat.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for path in scene_files:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        FINAL_VIDEO
    ]

    run(cmd)

    print(f"\nFINAL VIDEO CREATED: {FINAL_VIDEO}")


if __name__ == "__main__":
    main()
