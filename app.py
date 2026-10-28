
import streamlit as st

from classbuild.services.course_generator import course_generator
from classbuild.services.lesson_generator import lesson_generator
from classbuild.services.quiz_generator import quiz_generator
from classbuild.services.quiz_grader import grade_quiz

def initialize_session_state():
    """Initialize session state without overwriting existing values."""
    defaults = {
    "course_settings": {},
    "outline": None,
    "selected_lesson": None,
    "generated_lesson": None,
    "lesson_contents": {},
    "quiz": None,
    "quizzes": {},
    "quiz_results": {},
}

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def generate_course_outline(topic, difficulty, lesson_count):
    """Generate and save a course outline."""
    if not topic.strip():
        st.error("Please enter a course topic before generating the outline.")
        return

    if not difficulty or not lesson_count:
        st.error("Please select a difficulty level and number of lessons.")
        return

    try:
        with st.spinner("Generating course outline... Please wait"):
            course_data = course_generator(
                topic=topic.strip(),
                difficulty=difficulty,
                lesson_count=lesson_count,
            )

        st.session_state.course_settings = {
            "topic": topic.strip(),
            "difficulty": difficulty,
            "lesson_count": lesson_count,
        }
        st.session_state.outline = course_data

        st.session_state.lesson_contents = {}
        st.session_state.selected_lesson = None
        st.session_state.generated_lesson = None

        st.success("Course outline generated successfully!")

    except (ValueError, RuntimeError) as error:
        st.error(str(error))


def render_course_form():
    """Display the course settings form."""
    st.title("Mini ClassBuild")
    st.subheader("AI-powered learning")

    st.write(
        """
        Mini ClassBuild is an AI-powered learning application that helps you
        create course outlines, generate lesson content, and practice your
        knowledge through interactive quizzes.
        """
    )

    topic = st.text_input(
        "Course Topic",
        placeholder="Enter a course topic...",
    )

    with st.container(border=True):
        st.markdown("Select the difficulty level:")

        difficulty = st.pills(
            "Choose Difficulty",
            ["Beginner", "Intermediate", "Advanced"],
            selection_mode="single",
            label_visibility="collapsed",
            width="stretch",
        )

    with st.container(border=True):
        st.markdown("Number of Lessons:")

        lesson_count = st.pills(
            "Number of Lessons",
            [2, 3, 4, 5],
            selection_mode="single",
            label_visibility="collapsed",
            width="stretch",
        )

    if st.button("Generate Course Outline"):
        generate_course_outline(
            topic=topic,
            difficulty=difficulty,
            lesson_count=lesson_count,
        )


def render_course_outline():
    """Display the generated course outline."""
    course = st.session_state.outline

    if course is None:
        return

    st.header(course.title)
    st.write(course.description)

    st.subheader("Course Objectives")
    for objective in course.objectives:
        st.markdown(f"- {objective}")

    st.subheader("Lessons")

    for index, lesson in enumerate(course.lessons, start=1):
        with st.expander(f"{index}. {lesson.title}"):
            st.write(lesson.summary)

            st.markdown("**Learning Objectives**")
            for objective in lesson.learning_objectives:
                st.markdown(f"- {objective}")


def generate_lesson_content(cache_key, topic, difficulty, lesson):
    """Generate lesson content only when it is not already cached."""
    if cache_key in st.session_state.lesson_contents:
        st.info("Showing previously generated lesson content.")
        return

    try:
        with st.spinner("Generating lesson content..."):
            content = lesson_generator(
                topic=topic,
                difficulty=difficulty,
                lesson=lesson,
            )

        st.session_state.lesson_contents[cache_key] = content
        st.session_state.generated_lesson = content

        st.success("Lesson content generated successfully!")

    except (ValueError, RuntimeError) as error:
        st.error(str(error))


def render_lesson_content(content):
    """Display the complete lesson in a readable format."""
    st.markdown("### Introduction")
    st.write(content.introduction)

    st.markdown("### Lesson Sections")

    for index, section in enumerate(content.sections, start=1):
        st.markdown(f"#### {index}. {section.heading}")
        st.write(section.explanation)

        st.markdown("**Example**")
        st.code(section.example)

    st.markdown("### Summary")
    st.write(content.summary)

    st.markdown("### Exercises")

    for index, exercise in enumerate(content.exercises, start=1):
        with st.expander(f"Exercise {index}"):
            st.write(exercise.task)
            st.markdown("**Hint**")
            st.write(exercise.hint)


def render_lesson_section():
    """Allow the user to select and generate a complete lesson."""
    course = st.session_state.outline

    if course is None:
        return

    st.subheader("Generate Complete Lesson")

    lesson_options = [
        f"{index}. {lesson.title}"
        for index, lesson in enumerate(course.lessons, start=1)
    ]

    selected_option = st.selectbox(
        "Select a lesson",
        lesson_options,
        key="selected_lesson_title",
    )

    selected_index = lesson_options.index(selected_option)
    selected_lesson = course.lessons[selected_index]

    st.session_state.selected_lesson = selected_lesson

    settings = st.session_state.course_settings

    cache_key = (
        settings["topic"],
        settings["difficulty"],
        tuple(
            (
                item.title,
                tuple(item.learning_objectives),
                item.summary,
            )
            for item in course.lessons
        ),
        selected_index,
        selected_lesson.title,
    )

    if st.button("Generate Lesson Content"):
        generate_lesson_content(
            cache_key=cache_key,
            topic=settings["topic"],
            difficulty=settings["difficulty"],
            lesson=selected_lesson,
        )

    content = st.session_state.lesson_contents.get(cache_key)

    if content is not None:
        render_lesson_content(content)

def reset_quiz_attempt(quiz_key, answer_keys):
    """Clear attempt data while preserving the original questions."""
    for key in answer_keys:
        st.session_state.pop(key, None)

    st.session_state.quiz_results.pop(quiz_key, None)

def render_quiz_section():
    course = st.session_state.outline
    if course is None:
        return
    settings = st.session_state.course_settings

    if not settings:
        return
    lesson_options = [
        f"{index}. {lesson.title}"
        for index, lesson in enumerate(course.lessons, start=1)
    ]
    selected_option = st.session_state.get("selected_lesson_title")

    if selected_option not in lesson_options:
        return

    selected_index = lesson_options.index(selected_option)
    selected_lesson = course.lessons[selected_index]
    quiz_key = (
        settings["topic"],
        settings["difficulty"],
        tuple(
            (
                item.title,
                tuple(item.learning_objectives),
                item.summary,
            )
            for item in course.lessons
        ),
        selected_index,
        selected_lesson.title,
    )
    quiz_key_id = str(quiz_key)
    answer_keys = [
        f"quiz_answer_{quiz_key_id}_{i}"
        for i in range(5)
    ]
    form_key = f"quiz_form_{quiz_key_id}"
    content_key = (
        settings["topic"],
        settings["difficulty"],
        quiz_key[2],
        selected_index,
        selected_lesson.title,
    )

    lesson_content = st.session_state.lesson_contents.get(content_key)
    if lesson_content is None:
        st.info("Generate the complete lesson content before creating a quiz.")
        return

    st.subheader("Lesson Quiz")

    if quiz_key not in st.session_state.quizzes:
        if st.button("Generate Quiz", key=f"generate_quiz_{quiz_key_id}"):
            try:
                with st.spinner("Generating five quiz questions..."):
                    quiz = quiz_generator(
                        topic=settings["topic"],
                        difficulty=settings["difficulty"],
                        lesson_title=selected_lesson.title,
                        lesson_content=lesson_content,
                    )

                st.session_state.quizzes[quiz_key] = quiz
                st.session_state.quiz_results.pop(quiz_key, None)
                st.success("Quiz generated successfully!")
                st.rerun()

            except (ValueError, RuntimeError) as error:
                st.error(str(error))

        return
    quiz = st.session_state.quizzes[quiz_key]
    previous_result = st.session_state.quiz_results.get(quiz_key)
    with st.form(key=form_key):
        for index, question in enumerate(quiz.questions):
            st.markdown(f"**Question {index + 1}: {question.question}**")

            st.radio(
                "Choose one answer:",
                question.options,
                index=None,
                key=answer_keys[index],
                label_visibility="collapsed",
            )
        submitted = st.form_submit_button("Submit Answers")

    if submitted:
        answers = [
            st.session_state.get(key)
            for key in answer_keys
        ]
        if any(answer is None for answer in answers):
            st.warning("Please answer all five questions before submitting.")
        else:
            score, results = grade_quiz(quiz, answers)
            st.session_state.quiz_results[quiz_key] = {
                    "score": score,
                    "results": results,
                }

            st.rerun()
    previous_result = st.session_state.quiz_results.get(quiz_key)

    if previous_result is not None:
        st.markdown("### Your Result")
        st.subheader(
            f"Score: {previous_result['score']} / 5"
        )
        for index, result in enumerate(
            previous_result["results"],
            start=1,
        ):
            st.markdown(f"**Question {index}: {result['question']}**")

            if result["is_correct"]:
                st.success("Correct answer!")
            else:
                st.error("Incorrect answer.")

            st.write(
                f"Your answer: {result['selected_answer']}"
            )
            st.write(
                f"Correct answer: {result['correct_answer']}"
            )
            st.write(
                f"Explanation: {result['explanation']}"
            )
    if st.button(
            "Retake Quiz",
            key=f"retake_{quiz_key_id}",
            on_click=reset_quiz_attempt,
            args=(quiz_key, answer_keys),
        ):
            pass



def main():
    st.set_page_config(
        page_title="Mini ClassBuild",
        page_icon="🤖",
    )

    initialize_session_state()

    render_course_form()
    render_course_outline()
    render_lesson_section()
    render_quiz_section()


if __name__ == "__main__":
    main()
