import os

def main():
    print("K-Stick automation started successfully.")

    openai_key = os.getenv("OPENAI_API_KEY")

    if openai_key:
        print("OpenAI API key detected.")
    else:
        print("OPENAI_API_KEY is not set yet.")

if __name__ == "__main__":
    main()
