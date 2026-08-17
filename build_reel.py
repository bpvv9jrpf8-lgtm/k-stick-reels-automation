import json
import os
import subprocess
import textwrap

PLAN_FILE = "scene_plan.json"
NARRATOR_FILE = "audio/narrator.mp3"
REACTION_FILE = "audio/reaction.mp3"

OUTPUT_DIR = "output"
TEMP_DIR = "temp"

FINAL_VIDEO = os.path.join(
    OUTPUT_DIR,
    "k_stick_reel_polished.mp4"
)

WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_DURATION = 15


def run(cmd):
    print("\nRUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def esc(text):
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
    )


def wrap_caption(text):
    words = text.split()[:5]

    if len(words) <= 3:
        return " ".join(words)

    midpoint = (len(words) + 1) // 2

    return (
        " ".join(words[:midpoint])
        + "\n"
        + " ".join(words[midpoint:])
    )


def prop_position(scene_number):
    positions = {
        1: ("W*0.66", "H*0.62"),
        2: ("W*0.25", "H*0.62"),
        3: ("W*0.66", "H*0.60"),
        4: ("W*0.25", "H*0.60"),
    }

    return positions.get(
        scene_number,
        ("W*0.68", "H*0.62")
    )


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    hook = esc(
        " ".join(
            plan.get("hook_text", "WAIT FOR IT").split()[:4]
        )
    )

    scenes = plan["scenes"]

    scene_files = []

    for scene in scenes:
        number = scene["scene_number"]
        duration = float(scene["duration_seconds"])

        background = scene["background_asset"]
        character = scene["character_asset"]

        caption = esc(
            wrap_caption(
                scene.get("short_caption", "")
            )
        )

        prop = scene.get("prop_asset")

        out_file = os.path.join(
            TEMP_DIR,
            f"scene_{number}.mp4"
        )

        scene_files.append(out_file)

        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", background,
            "-loop", "1",
            "-t", str(duration),
            "-i", character,
        ]

        use_prop = (
            prop is not None
            and os.path.exists(prop)
        )

        if use_prop:
            cmd += [
                "-loop", "1",
                "-t", str(duration),
                "-i", prop
            ]

        bg_filter = (
            f"[0:v]"
            f"scale=1200:2133,"
            f"zoompan="
            f"z='min(zoom+0.00045,1.045)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={int(duration * FPS)}:"
            f"s={WIDTH}x{HEIGHT}:"
            f"fps={FPS}"
            f"[bg];"
        )

        char_filter = (
            "[1:v]"
            "scale=350:-1"
            "[char];"
        )

        if use_prop:
            px, py = prop_position(number)

            prop_filter = (
                "[2:v]"
                "scale=155:-1"
                "[prop];"
            )

            compose = (
                "[bg][char]"
                "overlay="
                "x='(W-w)/2 + 6*sin(2*PI*t)':"
                "y='H-h-410 + 4*sin(3*PI*t)'"
                "[base];"

                "[base][prop]"
                f"overlay=x='{px}':y='{py}'"
                "[final];"
            )

            source = "[final]"

        else:
            prop_filter = ""

            compose = (
                "[bg][char]"
                "overlay="
                "x='(W-w)/2 + 6*sin(2*PI*t)':"
                "y='H-h-410 + 4*sin(3*PI*t)'"
                "[final];"
            )

            source = "[final]"

        text_filter = (
            f"{source}"
            f"drawtext="
            f"text='{hook}':"
            f"fontcolor=white:"
            f"fontsize=52:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"x=max(70\\,(w-text_w)/2):"
            f"y=180,"
            f"drawtext="
            f"text='{caption}':"
            f"fontcolor=white:"
            f"fontsize=44:"
            f"borderw=5:"
            f"bordercolor=black:"
            f"line_spacing=8:"
            f"x=max(70\\,(w-text_w)/2):"
            f"y=h-360"
        )

        filter_complex = (
            bg_filter
            + char_filter
            + prop_filter
            + compose
            + text_filter
        )

        cmd += [
            "-filter_complex",
            filter_complex,
            "-r", str(FPS),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            out_file
        ]

        run(cmd)

    concat_file = os.path.join(
        TEMP_DIR,
        "concat.txt"
    )

    with open(concat_file, "w", encoding="utf-8") as f:
        for path in scene_files:
            f.write(
                f"file '{os.path.abspath(path)}'\n"
            )

    silent_video = os.path.join(
        TEMP_DIR,
        "silent.mp4"
    )

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

    # Audio:
    # narrator
    # delayed K-Stick reaction
    # soft synthetic pop at ~3.2 sec
    # alert beep at ~9.8 sec
    # punchline pop at ~11 sec

    audio_filter = (
        "[1:a]"
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "volume=1.0"
        "[narr];"

        "[2:a]"
        "volume=1.20,"
        "adelay=11000|11000"
        "[react];"

        "[3:a]"
        "volume=0.10,"
        "atrim=0:0.18,"
        "adelay=3200|3200"
        "[pop1];"

        "[4:a]"
        "volume=0.075,"
        "atrim=0:0.22,"
        "adelay=9800|9800"
        "[beep];"

        "[5:a]"
        "volume=0.12,"
        "atrim=0:0.22,"
        "adelay=11000|11000"
        "[pop2];"

        "[narr][react][pop1][beep][pop2]"
        "amix=inputs=5:"
        "duration=longest:"
        "dropout_transition=0"
        "[mix]"
    )

    run([
        "ffmpeg",
        "-y",

        "-i", silent_video,
        "-i", NARRATOR_FILE,
        "-i", REACTION_FILE,

        "-f", "lavfi",
        "-t", "15",
        "-i",
        "sine=frequency=420:sample_rate=44100",

        "-f", "lavfi",
        "-t", "15",
        "-i",
        "sine=frequency=850:sample_rate=44100",

        "-f", "lavfi",
        "-t", "15",
        "-i",
        "sine=frequency=260:sample_rate=44100",

        "-filter_complex",
        audio_filter,

        "-map", "0:v",
        "-map", "[mix]",

        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "160k",

        "-t", str(TOTAL_DURATION),

        FINAL_VIDEO
    ])

    print(f"FINAL VIDEO: {FINAL_VIDEO}")


if __name__ == "__main__":
    main()
