from graphs.graph_status import GraphStatus
from graphs.nodes.node_utils import node

@node
async def none_action(state: GraphStatus) -> GraphStatus:
    return state