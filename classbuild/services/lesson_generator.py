import json
import os

from dotenv import load_dotenv
from groq import (
    Groq,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)
from pydantic import ValidationError

from classbuild.models.lesson import Lesson, LessonContent

def lesson_generator(
    topic: str,
    difficulty: str,
    lesson: Lesson,
)  -> LessonContent:
    if not topic.strip():
        raise ValueError("Course topic cannot be empty.")

    if difficulty not in {"Beginner", "Intermediate", "Advanced"}:
        raise ValueError("Invalid difficulty level.")

    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    client = Groq(api_key=api_key, timeout=30.0, max_retries=1)

    prompt = f"""
    Create a complete educational lesson using the information below.

    Course topic: {topic.strip()}
    Difficulty: {difficulty}
    Lesson title: {lesson.title}
    Learning objectives: {json.dumps(lesson.learning_objectives)}
    Original lesson summary: {lesson.summary}

    Return one valid JSON object with these fields:

    - introduction: a clear introduction to the lesson
    - sections: a list containing 2 to 4 sections
    - summary: a concise summary of the complete lesson
    - exercises: exactly 2 exercises

    Each section must contain:
    - heading: a section heading
    - explanation: a clear educational explanation
    - example: a relevant example

    Each exercise must contain:
    - task: an exercise for the student
    - hint: a helpful hint without directly giving away the answer

    Requirements:
    - Match the specified difficulty level.
    - Cover the lesson's learning objectives.
    - Make explanations and examples relevant to the course topic.
    - Return valid JSON only.
    """

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("The AI returned an empty response.")

            data = json.loads(content)
            lesson_content = LessonContent.model_validate(data)

            return lesson_content

        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            if attempt == 1:
                raise ValueError(
                    "Could not generate valid lesson content. "
                    "Please try again."
                ) from exc

        except (APITimeoutError, APIConnectionError) as exc:
            raise RuntimeError(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ) from exc

        except APIStatusError as exc:
            raise RuntimeError(
                f"The AI service returned an API error "
                f"(status {exc.status_code}). Check the terminal for details."
            ) from exc