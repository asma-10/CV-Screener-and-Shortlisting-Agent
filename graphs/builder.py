from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from graphs.state import State
from nodes.report import generate_final_report
from nodes.key_req_extractor import extract_key_requirements, distribute_cvs
from nodes.score_cv import score_cv
from nodes.shortlist import shortlist_cvs
from nodes.HITL  import human_in_the_loop


def build():
    graph_builder = StateGraph(State)

    graph_builder.add_node('requirements_extractor', extract_key_requirements)
    graph_builder.add_node('scorer', score_cv)
    graph_builder.add_node('shortlister', shortlist_cvs)
    graph_builder.add_node('final_report', generate_final_report)
    graph_builder.add_node('human_in_the_loop', human_in_the_loop)

    graph_builder.add_edge(START, 'requirements_extractor')
    graph_builder.add_conditional_edges('requirements_extractor', distribute_cvs, ['scorer'])
    graph_builder.add_edge('scorer', 'shortlister')
    graph_builder.add_edge('shortlister', 'human_in_the_loop')
    graph_builder.add_edge('human_in_the_loop', 'final_report')
    graph_builder.add_edge('final_report', END)

    checkpointer = InMemorySaver()
    return graph_builder.compile(checkpointer=checkpointer)