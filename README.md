
# Mini ClassBuild

Mini ClassBuild is an AI-powered educational application built with Python and Streamlit. It helps learners generate course outlines, explore complete lesson content, and assess their understanding through interactive multiple-choice quizzes.

## Features

- **Course Outline Generation:** Generate a course outline by entering a topic, selecting a difficulty level, and choosing between 2 and 5 lessons.
- **Complete Lesson Generation:** Generate a lesson introduction, educational sections, examples, a summary, and exercises with hints.
- **AI-Generated Quizzes:** Generate exactly five multiple-choice questions based on the selected lesson.
- **Quiz Validation:** Validate the quiz structure using Pydantic, including four options per question and a correct answer that matches one of the options.
- **Local Quiz Grading:** Grade student answers in Python without making another Groq API request.
- **Score and Explanations:** Display a score out of five and explain the correct answers after submission.
- **Quiz Retakes:** Allow learners to retake the same quiz while keeping the original questions and resetting the previous attempt.
- **Session State:** Use Streamlit session state to manage generated courses, lesson content, quizzes, and quiz results during the session.

## Technologies Used

- Python
- Streamlit
- Groq API
- Pydantic
- python-dotenv

## Project Structure

```text
SkillForge/
├── app.py
├── README.md
├── README.ar.md
├── requirements.txt
├── classbuild/
│   ├── llm/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── course.py
│   │   ├── lesson.py
│   │   └── quiz.py
│   └── services/
│       ├── course_generator.py
│       ├── lesson_generator.py
│       ├── quiz_generator.py
│       └── quiz_grader.py
├── scripts/
└── test/test_groq_connection.py
```

## Requirements

- Python 3.10 or later.
- A valid Groq API key.
- Internet access to communicate with the Groq API.

## Installation

1. Open a terminal in the project directory.

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment.

   On macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

   On Windows:

   ```bash
   .venv\Scripts\activate
   ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add your Groq credentials:

   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL=openai/gpt-oss-20b
   ```

   Replace the placeholder with your own API key. Keep `.env` private and never commit it to GitHub.

## Usage

Run the application from the project root:

```bash
python -m streamlit run app.py
```

Then follow these steps:

1. Enter a course topic, such as `Python Programming for Beginners`.
2. Select the difficulty level.
3. Choose the number of lessons.
4. Click **Generate Course Outline**.
5. Select a lesson and click **Generate Lesson Content**.
6. Generate a quiz for the selected lesson.
7. Answer the five multiple-choice questions and submit your answers.
8. Review your score and the explanations.
9. Click **Retake Quiz** to attempt the same questions again.

## Quiz Grading

The Groq API is used to generate quiz questions. Grading is performed locally in Python by comparing each selected answer with the corresponding correct answer.

Each correct answer earns one point, resulting in a score between 0 and 5. Correct answers and explanations are displayed after submission.

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to access the Groq service. |
| `GROQ_MODEL` | Model identifier used for AI generation. |

## Current Scope

The current version focuses on course outline generation, complete lesson generation, multiple-choice quizzes, local grading, and quiz retakes.

PDF processing, embeddings, Retrieval-Augmented Generation (RAG), chatbot functionality, and permanent data storage are outside the current scope and are reserved for later development.

## Security

- Store API credentials in environment variables.
- Never commit `.env` or expose API keys publicly.
- Validate AI-generated data before using it in the application.

## Documentation

For the Arabic version, see [README.ar.md](README.ar.md).
