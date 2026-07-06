from api.schemas import CVOutput
from graphs.state import CVScorerState
from langchain_core.messages import HumanMessage
from config.llm import llm


def score_cv(state: CVScorerState):
    structured_llm = llm.with_structured_output(CVOutput)
    requirements = state['requirements']
    cv = state['cv']
    requirements_str = f"Must have: {requirements['must_have']}\nNice to have: {requirements['nice_to_have']}"
    message = HumanMessage(
        content=f"Score the following CV between 0 and 1 based on these requirements:\n{requirements_str}\n\nGive a clear justification.\n\nCV:\n{cv['text']}"
    )
    response = structured_llm.invoke([message])
    return {'scores': [{'filename': cv['filename'], 'score': response.score, 'justification': response.justification}]}