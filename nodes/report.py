from graphs.state import State
from langchain_core.messages import HumanMessage
from config.llm import llm



def generate_final_report(state: State):
    shortlist_str = "\n".join([
        f"- {s['filename']}: {s['score']:.2f} — {s['justification']}"
        for s in state['shortlist']
    ])
    message = HumanMessage(
        content=f"Generate a professional recruitment report for these shortlisted candidates:\n{shortlist_str}"
    )
    response = llm.invoke([message])
    return {'final_report': response.content}