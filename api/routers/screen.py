from fastapi import APIRouter
from api.schemas import ScreenResponse
from fastapi import Form
from nodes.text_pdf_extractor import extract_text_from_pdf
from graphs.instance import graph

router = APIRouter()

@router.post('/screen', response_model=ScreenResponse)
async def screen_cvs(
    job_description: str = Form(...),
    thread_id: str = Form(...),
    cv_filenames: list[str] = Form(...)
):
    cv_texts = []
    for filename in cv_filenames:
        with open(filename, 'rb') as f:
            file_bytes = f.read()
        text = extract_text_from_pdf(file_bytes)
        cv_texts.append({'filename': filename, 'text': text})

    config = {'configurable': {'thread_id': thread_id}}
    response = graph.invoke({
        'job_description': job_description,
        'cvs': cv_texts,
        'requirements': {},
        'scores': [],
        'shortlist': [],
        'reviewed': False,
        'final_report': ''
    }, config=config)

    if response.get('__interrupt__'):
        interrupted_value = response['__interrupt__'][0].value
        return ScreenResponse(
            scores=response['scores'],
            shortlist=interrupted_value['shortlist'],
            interrupted=True,
            interrupt_question=interrupted_value['question']
        )

    return ScreenResponse(
        scores=response['scores'],
        shortlist=response['shortlist'],
        interrupted=False,
        interrupt_question=None
    )
