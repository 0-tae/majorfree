from graphs.graph_status import GraphStatus
from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt

from graphs.nodes.node_utils import node

@node
async def fast_forward_question(state: GraphStatus) -> GraphStatus:
    """
    빠른 질문
    """
    
    model = chat_gpt
    
    answer = model.query_by_single_instruction(state["instruction"])

    return {
        "answer": answer
    }