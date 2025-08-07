from graphs.graph_status import GraphStatus
from mcp_server_api import get_multi_server_mcp_clients_from_api
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt

from graphs.nodes.node_utils import node


@node
async def web_search(state: GraphStatus) -> GraphStatus:
    """
    웹 검색을 하는 단계
    """
    
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    tools = await client.get_tools(server_name="naver_search_mcp")
    
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    prompt = f'''
    Search for information about the question. Please cite the sources of search results and respond in Korean.
    Question: {state["instruction"]}
    '''
    question_message = {"role":"user", "content": prompt}
        
    result = await agent.ainvoke({
        "messages": [question_message]
    })
        
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [question_message, generated_message],
        "answer": answer
    }