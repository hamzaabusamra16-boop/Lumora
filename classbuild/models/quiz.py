from pydantic import BaseModel, Field, model_validator
class QuizQuestion(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    @model_validator(mode="after")
    def validate_correct_answer(self):
        if any(not option.strip() for option in self.options):
            raise ValueError("Options cannot be empty.")
        if len(set(self.options)) != 4:
            raise ValueError("Options must be unique.")

        if self.correct_answer not in self.options:
            raise ValueError(
                "The correct answer must match one of the options."
            )

        return self
class Quiz(BaseModel):
        questions: list[QuizQuestion] = Field(
        min_length=5,
        max_length=5,
    )
   

