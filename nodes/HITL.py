from graphs.state import State
from langgraph.types import interrupt

def human_in_the_loop(state: State):
    
    human_decision = interrupt({
        'shortlist': state['shortlist'],
        'question': 'Please review the shortlist. Do you approve it? (approve / adjust / reject)'
    })
    
    if human_decision == 'approve':
        return {'reviewed': True}
    
    elif human_decision == 'reject':
        return {'reviewed': False, 'shortlist': []}