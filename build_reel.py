import json
import os
import subprocess
import textwrap

PLAN_FILE = "scene_plan.json"
VOICE_FILE = "audio/voiceover.mp3"

OUTPUT_DIR = "output"
TEMP_DIR = "temp"

FINAL_VIDEO = os.path.join(
    OUTPUT_DIR,
    "k_stick_reel_final.mp4"
)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

TOTAL_DURATION = 15

SCENE_DURATIONS = [
    3.5,
    3.5,
    3.5,
    4.5
]


def run(cmd):
    print(
        "\nRUN:",
        " ".join(cmd)
    )

    subprocess.run(
        cmd,
        check=True
    )


def ffmpeg_escape(text):
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
    )


def wrap_caption(text):
    return "\n".join(
        textwrap.wrap(
            text,
            width=17
        )
    )


def main():
    if not os.path.exists(
        PLAN_FILE
    ):
        raise FileNotFoundError(
            "scene_plan.json not found"
        )

    if not os.path.exists(
        VOICE_FILE
    ):
        raise FileNotFoundError(
            "audio/voiceover.mp3 not found"
        )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        TEMP_DIR,
        exist_ok=True
    )

    with open(
        PLAN_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        plan = json.load(f)

    hook_text = plan.get(
        "hook_text",
        "WAIT FOR IT"
    )

    scenes = plan.get(
        "scenes",
        []
    )

    if len(scenes) < 4:
        raise ValueError(
            "Need 4 scenes."
        )

    scene_files = []

    for index in range(4):
        scene = scenes[index]

        duration = SCENE_DURATIONS[
            index
        ]

        background = scene[
            "background_asset"
        ]

        character = scene[
            "character_asset"
        ]

        prop = scene.get(
            "prop_asset"
        )

        caption = scene.get(
            "short_caption",
            ""
        )

        hook = ffmpeg_escape(
            hook_text
        )

        caption = ffmpeg_escape(
            wrap_caption(caption)
        )

        output_scene = os.path.join(
            TEMP_DIR,
            f"scene_{index + 1}.mp4"
        )

        scene_files.append(
            output_scene
        )

        inputs = [
            "ffmpeg",
            "-y",

            "-loop",
            "1",
            "-t",
            str(duration),
            "-i",
            background,

            "-loop",
            "1",
            "-t",
            str(duration),
            "-i",
            character
        ]

        if prop and os.path.exists(prop):
            inputs.extend(
                [
                    "-loop",
                    "1",
                    "-t",
                    str(duration),
                    "-i",
                    prop
                ]
            )

            filter_complex = (
                f"[0:v]"
                f"scale=1200:2133,"
                f"zoompan="
                f"z='min(zoom+0.0005,1.05)':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d={int(duration * FPS)}:"
                f"s={WIDTH}x{HEIGHT}:"
                f"fps={FPS}"
                f"[bg];"

                f"[1:v]"
                f"scale=370:-1"
                f"[char];"

                f"[2:v]"
                f"scale=180:-1"
                f"[prop];"

                f"[bg][char]"
                f"overlay="
                f"x='(W-w)/2':"
                f"y='H-h-430'"
                f"[scene1];"

                f"[scene1][prop]"
                f"overlay="
                f"x='W/2+120':"
                f"y='H-650'"
                f"[scene2];"

                f"[scene2]"
                f"drawtext="
                f"text='{hook}':"
                f"fontcolor=white:"
                f"fontsize=50:"
                f"borderw=6:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=180,"

                f"drawtext="
                f"text='{caption}':"
                f"fontcolor=white:"
                f"fontsize=46:"
                f"borderw=5:"
                f"bordercolor=black:"
                f"line_spacing=8:"
                f"x=(w-text_w)/2:"
                f"y=h-330"
            )

        else:
            filter_complex = (
                f"[0:v]"
                f"scale=1200:2133,"
                f"zoompan="
                f"z='min(zoom+0.0005,1.05)':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d={int(duration * FPS)}:"
                f"s={WIDTH}x{HEIGHT}:"
                f"fps={FPS}"
                f"[bg];"

                f"[1:v]"
                f"scale=370:-1"
                f"[char];"

                f"[bg][char]"
                f"overlay="
                f"x='(W-w)/2':"
                f"y='H-h-430',"

                f"drawtext="
                f"text='{hook}':"
                f"fontcolor=white:"
                f"fontsize=50:"
                f"borderw=6:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=180,"

                f"drawtext="
                f"text='{caption}':"
                f"fontcolor=white:"
                f"fontsize=46:"
                f"borderw=5:"
                f"bordercolor=black:"
                f"line_spacing=8:"
                f"x=(w-text_w)/2:"
                f"y=h-330"
            )

        command = (
            inputs
            + [
                "-filter_complex",
                filter_complex,

                "-r",
                str(FPS),

                "-c:v",
                "libx264",

                "-preset",
                "veryfast",

                "-pix_fmt",
                "yuv420p",

                "-t",
                str(duration),

                output_scene
            ]
        )

        run(command)

    concat_file = os.path.join(
        TEMP_DIR,
        "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:
        for path in scene_files:
            f.write(
                f"file '{os.path.abspath(path)}'\n"
            )

    silent_video = os.path.join(
        TEMP_DIR,
        "silent_video.mp4"
    )

    run(
        [
            "ffmpeg",
            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            concat_file,

            "-c:v",
            "libx264",

            "-pix_fmt",
            "yuv420p",

            "-r",
            str(FPS),

            "-t",
            str(TOTAL_DURATION),

            silent_video
        ]
    )

    run(
        [
            "ffmpeg",
            "-y",

            "-i",
            silent_video,

            "-i",
            VOICE_FILE,

            "-filter_complex",
            (
                "[1:a]"
                "loudnorm="
                "I=-16:"
                "TP=-1.5:"
                "LRA=11"
                "[voice]"
            ),

            "-map",
            "0:v",

            "-map",
            "[voice]",

            "-c:v",
            "copy",

            "-c:a",
            "aac",

            "-b:a",
            "160k",

            "-t",
            str(TOTAL_DURATION),

            FINAL_VIDEO
        ]
    )

    print(
        "\n================================="
    )

    print(
        f"FINAL VIDEO: {FINAL_VIDEO}"
    )

    print(
        "================================="
    )


if __name__ == "__main__":
    main()
