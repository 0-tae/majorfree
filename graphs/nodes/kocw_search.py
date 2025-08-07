from graphs.graph_status import GraphStatus
from mcp_server_api import get_multi_server_mcp_clients_from_api
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt
from tools.mcp.vectordb.chroma.chroma_db import db_instance as chroma_db

from graphs.nodes.node_utils import node

@node
async def kocw_search(state: GraphStatus) -> GraphStatus:
    """
    학습자료 추천
    """
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    tools = await client.get_tools(server_name="kocw_lecture_search_mcp")
            
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    result = await agent.ainvoke({
        "messages": [{"role":"user", "content":state["instruction"]}]
    })
    
    print("😇 RESULT: ",result)
        
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }