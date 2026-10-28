
from pydantic import BaseModel, Field


class Lesson(BaseModel):
    title: str = Field(min_length=1)
    learning_objectives: list[str] = Field(min_length=1)
    summary: str = Field(min_length=1)


class LessonSection(BaseModel):
    heading: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    example: str = Field(min_length=1)


class LessonExercise(BaseModel):
    task: str = Field(min_length=1)
    hint: str = Field(min_length=1)


class LessonContent(BaseModel):
    introduction: str = Field(min_length=1)
    sections: list[LessonSection] = Field(min_length=2, max_length=4)
    summary: str = Field(min_length=1)
    exercises: list[LessonExercise] = Field(min_length=2, max_length=2)
