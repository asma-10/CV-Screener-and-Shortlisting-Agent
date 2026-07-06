from pydantic import BaseModel, Field


class ScreenRequest(BaseModel):
    job_description: str = Field(..., description="The job description text to analyze")

class ScreenResponse(BaseModel):
    scores: list[dict] = Field(..., description="List of CV scores and justifications")
    shortlist: list[dict] = Field(..., description="List of shortlisted CVs")
    interrupted: bool = Field(..., description="Indicates if the process was interrupted")
    interrupt_question: str | None = Field(None, description="Question to ask if interrupted")

class ConfirmRequest(BaseModel):
    decision: str = Field(..., description="Decision made by the user (e.g., 'accept', 'reject')")
    thread_id: str = Field(..., description="Identifier for the specific recruitment thread")

class ReportResponse(BaseModel):
    final_report: str = Field(..., description="The final recruitment report generated after processing")

class CVOutput(BaseModel):
    score: float = Field(..., description="Score between 0 and 1")
    justification: str = Field(..., description="Clear justification for the score")

class RequirementsOutput(BaseModel):
    must_have: list[str] = Field(..., description="Non-negotiable requirements from the job description")
    nice_to_have: list[str] = Field(..., description="Preferred but not mandatory requirements")
