import os

from dotenv import load_dotenv
from groq import Groq
from groq import APIConnectionError, APIStatusError, APITimeoutError

def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    if not api_key or not api_key.strip():
        print("Error: GROQ_API_KEY is missing. Check your .env file.")
        return
    try:
        client = Groq(
            api_key=api_key,
            timeout=15.0,
            max_retries=1,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "In one sentence, explain what Python is.",
                }
            ],
        )
        reply = response.choices[0].message.content
        if reply and reply.strip():
            print("Groq connection successful!")
            print("Model reply:", reply)
        else:
            print("Error: The model returned an empty response.")
    except APITimeoutError:
        print("Error: The request timed out. Please try again.")
    except APIConnectionError:
        print("Error: Could not connect to Groq. Check your internet connection.")
    except APIStatusError as error:
        print(f"Groq API error: HTTP {error.status_code}. Check your API key and request.")
    except Exception as error:
        print(f"Unexpected error: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()




