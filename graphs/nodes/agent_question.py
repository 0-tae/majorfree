from graphs.graph_status import GraphStatus
from mcp_server_api import get_multi_server_mcp_clients_from_api
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt

from graphs.nodes.node_utils import node

@node
async def agent_question(state: GraphStatus) -> GraphStatus:
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    # 클라이언트 연결
    tools = await client.get_tools()
        
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    result = await agent.ainvoke({
        "messages": state["messages"]
    })
    
    print("😇 RESULT: ",result)
    
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }