from pydantic import BaseModel, Field
from classbuild.models.lesson import Lesson

class Course(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    objectives: list[str] = Field(min_length=1)
    lessons: list[Lesson] = Field(min_length=2, max_length=5)
