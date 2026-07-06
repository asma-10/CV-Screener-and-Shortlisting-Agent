from graphs.state import State
from api.schemas import RequirementsOutput
from langchain_core.messages import HumanMessage
from config.llm import llm
from langgraph.types import Send


def extract_key_requirements(state: State):
    structured_llm = llm.with_structured_output(RequirementsOutput)
    message = HumanMessage(
        content=f"Extract key requirements from the following job description:\n{state['job_description']}"
    )
    response = structured_llm.invoke([message])
    return {'requirements': {'must_have': response.must_have, 'nice_to_have': response.nice_to_have}}

def distribute_cvs(state: State):
    return [
        Send('scorer', {'cv': cv, 'requirements': state['requirements']})
        for cv in state['cvs']
    ]