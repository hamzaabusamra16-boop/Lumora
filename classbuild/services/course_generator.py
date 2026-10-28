import json
import os
from dotenv import load_dotenv
from groq import Groq, APITimeoutError, APIConnectionError, APIStatusError
from classbuild.models.course import Course
from pydantic import ValidationError
def course_generator(
    topic: str,
    difficulty: str,
    lesson_count: int,
    ) -> Course:
    if not topic.strip():
        raise ValueError("Course topic cannot be empty.")

    if difficulty not in {"Beginner", "Intermediate", "Advanced"}:
        raise ValueError("Invalid difficulty level.")

    if not 2 <= lesson_count <= 5:
        raise ValueError("Lesson count must be between 2 and 5.")
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    client = Groq(api_key=api_key, timeout=30.0, max_retries=1)
    prompt = f"""
    Create a course with the following requirements:
    Topic: {topic.strip()}
    Difficulty: {difficulty}
    Number of lessons: exactly {lesson_count}

    Return a JSON object with these fields:
    - title: string
    - description: string
    - objectives: list of strings
    - lessons: list of lesson objects

    Each lesson object must contain:
    - title: string
    - learning_objectives: list of strings
    - summary: string

    Return valid JSON only.
    """
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("The AI returned an empty response.")

            data = json.loads(content)
            course_data = Course.model_validate(data)

            if len(course_data.lessons) != lesson_count:
                raise ValueError(
                    f"Expected {lesson_count} lessons, "
                    f"but received {len(course_data.lessons)}."
                )

            return course_data
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            if  attempt == 1:
                raise ValueError(
                    "Could not generate a valid course outline. "
                    "Please try again."
                ) from exc
        except (APITimeoutError, APIConnectionError) as exc:
            raise RuntimeError(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ) from exc

        except APIStatusError as exc:
            raise RuntimeError(
                "The AI service returned an API error. "
                "Please try again later."
            ) from exc
