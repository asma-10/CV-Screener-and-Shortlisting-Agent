from graphs.state import State


def shortlist_cvs(state: State):
    shortlist = [s for s in state['scores'] if s['score'] >= 0.7]
    shortlist = sorted(shortlist, key=lambda x: x['score'], reverse=True)
    return {'shortlist': shortlist, 'reviewed': False}