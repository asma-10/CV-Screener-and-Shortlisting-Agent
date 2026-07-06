from typing import TypedDict, Annotated, List
from operator import add


class State(TypedDict):
    job_description: str
    cvs: list[dict]
    requirements: dict
    scores: Annotated[list, add]
    shortlist: list[dict]
    reviewed: bool
    final_report: str

class CVScorerState(TypedDict):
    cv: dict
    requirements: dict