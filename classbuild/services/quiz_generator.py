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

from classbuild.models.lesson import LessonContent
from classbuild.models.quiz import Quiz


def quiz_generator(
    topic: str,
    difficulty: str,
    lesson_title: str,
    lesson_content: LessonContent,
) -> Quiz:
    if not topic.strip():
        raise ValueError("Course topic cannot be empty.")

    if difficulty not in {"Beginner", "Intermediate", "Advanced"}:
        raise ValueError("Invalid difficulty level.")

    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    client = Groq(
        api_key=api_key,
        timeout=30.0,
        max_retries=1,
    )

    lesson_data = lesson_content.model_dump_json()

    prompt = f"""
Create a multiple-choice quiz based ONLY on this lesson.

Course topic: {topic}
Difficulty: {difficulty}
Lesson title: {lesson_title}
Lesson content:
{lesson_data}

Return a JSON object with one field:
- questions: a list containing EXACTLY 5 questions.

Each question must contain:
- question: a clear question stem
- options: exactly 4 distinct answer options
- correct_answer: exactly one option copied verbatim from options
- explanation: an explanation of why the correct answer is right

Requirements:
- Questions must test knowledge covered in the supplied lesson.
- Match the requested difficulty.
- Include exactly one correct answer per question.
- Do not include the answer separately outside the JSON.
- Return valid JSON only.
"""

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
            )

            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("The AI returned an empty response.")

            data = json.loads(raw_content)
            quiz = Quiz.model_validate(data)

            return quiz

        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            if attempt == 1:
                raise ValueError(
                    "Could not generate a valid quiz. Please try again."
                ) from exc

        except (APITimeoutError, APIConnectionError) as exc:
            raise RuntimeError(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ) from exc

        except APIStatusError as exc:
            print("Quiz API error:", exc.status_code, exc.response.text)
            raise RuntimeError(
                "The AI service returned an API error. "
                "Please try again later."
            ) from exc