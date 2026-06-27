from __future__ import annotations

from pydantic import BaseModel, Field

from .discovery import ChatMessage


class RubricScores(BaseModel):
    correctness: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    depth: int = Field(ge=0, le=10)
    structure: int = Field(ge=0, le=10, description="STAR / organized reasoning")
    communication: int = Field(ge=0, le=10)


class AnswerFeedback(BaseModel):
    overall: int = Field(ge=0, le=10)
    scores: RubricScores
    strengths: list[str]
    improvements: list[str]
    better_answer: str = Field(description="Outline of a stronger answer")


class FeedbackItem(BaseModel):
    question: str
    answer: str
    overall: int
    scores: RubricScores
    strengths: list[str]
    improvements: list[str]
    better_answer: str


class InterviewMessageIn(BaseModel):
    session_id: str
    message: str


class InterviewState(BaseModel):
    session_id: str
    target_role: str
    messages: list[ChatMessage] = Field(default_factory=list)
    feedbacks: list[FeedbackItem] = Field(default_factory=list)
    readiness: int = 0
    turns: int = 0
