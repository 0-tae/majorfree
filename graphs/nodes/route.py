from graphs.graph_status import GraphStatus
from graphs.nodes.node_utils import node

@node
async def route(state: GraphStatus) -> GraphStatus:
    """
    라우팅 로직 있으면 추가할 것
    """
    
    available_modes = [
        "YOUTUBE_SEARCH",
        "WEB_SEARCH",
        "KOCW_SEARCH",
        "DEPARTMENT_SEARCH",
        "FAST_FORWARD",
        "SEARCH_ALL"
    ]
    
    for mode in available_modes:
        if mode == state["search_type"]:
            return mode
        
    return "COMMON"