from fastapi import APIRouter
from api.schemas import ReportResponse
from graphs.instance import graph

router = APIRouter()

@router.get('/report', response_model=ReportResponse)
async def report(thread_id: str):
    config = {'configurable': {'thread_id': thread_id}}
    
    state = graph.get_state(config)
    
    return ReportResponse(
        final_report=state.values['final_report']
    )