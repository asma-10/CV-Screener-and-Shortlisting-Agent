from fastapi import APIRouter
from api.schemas import ReportResponse, ConfirmRequest
from graphs.instance import graph
from langgraph.types import Command

router = APIRouter()

@router.post('/confirm', response_model=ReportResponse)
async def confirm(request: ConfirmRequest):
    config = {'configurable': {'thread_id': request.thread_id}}
    
    response = graph.invoke(
        Command(resume=request.decision),
        config=config
    )
    
    return ReportResponse(
        final_report=response['final_report']
    )

@router.get('/report', response_model=ReportResponse)
async def report(thread_id: str):
    config = {'configurable': {'thread_id': thread_id}}
    
    state = graph.get_state(config)
    
    return ReportResponse(
        final_report=state.values['final_report']
    )