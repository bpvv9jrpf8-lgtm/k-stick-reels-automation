import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def main():
    print("K-Stick automation started.")

    response = client.responses.create(
        model="gpt-5.6-luna",
        input="""
Create one original 15-second funny stickman reel idea.

Rules:
- Main character name: K-Stick
- Simple setup
- Fast problem
- Funny twist ending
- Family-friendly
- No copyrighted characters
- Output only:
  Hook:
  Story:
  Ending:
"""
    )

    print(response.output_text)

if __name__ == "__main__":
    main()
