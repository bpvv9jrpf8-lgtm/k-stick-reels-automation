import json
import os
import subprocess
import textwrap

PLAN_FILE = "scene_plan.json"
VOICE_FILE = "audio/voiceover.mp3"
OUTPUT_DIR = "output"
TEMP_DIR = "temp"

FINAL_VIDEO = os.path.join(OUTPUT_DIR, "k_stick_reel_v2.mp4")

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Exact target length
TOTAL_DURATION = 15

# Four scenes totaling 15 seconds
SCENE_DURATIONS = [3.5, 3.5, 3.5, 4.5]


def run(cmd):
    print("\nRUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ffmpeg_escape(text):
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
    )


def main():
    if not os.path.exists(PLAN_FILE):
        raise FileNotFoundError("scene_plan.json not found")

    if not os.path.exists(VOICE_FILE):
        raise FileNotFoundError("audio/voiceover.mp3 not found")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    scenes = plan.get("scenes", [])
    hook_text = plan.get("hook_text", "WAIT FOR END")

    if len(scenes) < 4:
        raise ValueError("Need 4 scenes in scene_plan.json")

    scene_files = []

    for i in range(4):
        scene = scenes[i]
        duration = SCENE_DURATIONS[i]

        background = scene["background_asset"]
        character = scene["character_asset"]
        story_text = scene.get("story_text", "")

        out_file = os.path.join(TEMP_DIR, f"scene_{i+1}.mp4")
        scene_files.append(out_file)

        # Keep text concise and inside mobile-safe width
        wrapped = "\n".join(textwrap.wrap(story_text, width=27))
        wrapped = ffmpeg_escape(wrapped)
        hook = ffmpeg_escape(hook_text)

        # Mild zoom on background + subtle character movement
        filter_complex = (
            f"[0:v]scale=1200:2133,"
            f"zoompan=z='min(zoom+0.0008,1.08)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={int(duration * FPS)}:"
            f"s={WIDTH}x{HEIGHT}:fps={FPS}[bg];"

            f"[1:v]scale=460:-1[char];"

            f"[bg][char]overlay="
            f"x='(W-w)/2 + 10*sin(2*PI*t)':"
            f"y='H-h-360 + 6*sin(3*PI*t)':"
            f"shortest=1,"
            
            f"drawtext="
            f"text='{hook}':"
            f"fontcolor=white:"
            f"fontsize=64:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=120,"

            f"drawtext="
            f"text='{wrapped}':"
            f"fontcolor=white:"
            f"fontsize=46:"
            f"borderw=5:"
            f"bordercolor=black:"
            f"line_spacing=8:"
            f"x=(w-text_w)/2:"
            f"y=h-290"
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
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            out_file
        ]

        run(cmd)

    concat_file = os.path.join(TEMP_DIR, "concat.txt")

    with open(concat_file, "w", encoding="utf-8") as f:
        for path in scene_files:
            f.write(f"file '{os.path.abspath(path)}'\n")

    silent_video = os.path.join(TEMP_DIR, "silent_15s.mp4")

    run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-t", str(TOTAL_DURATION),
        silent_video
    ])

    # Add AI narration and normalize it to exactly fit the reel.
    # If narration is shorter, audio will end earlier;
    # video still remains exactly 15 seconds.
    run([
        "ffmpeg",
        "-y",
        "-i", silent_video,
        "-i", VOICE_FILE,
        "-filter_complex",
        "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "160k",
        "-t", str(TOTAL_DURATION),
        "-shortest",
        FINAL_VIDEO
    ])

    print("\n===================================")
    print(f"FINAL V2 VIDEO: {FINAL_VIDEO}")
    print("Target duration: 15 seconds")
    print("===================================")


if __name__ == "__main__":
    main()
