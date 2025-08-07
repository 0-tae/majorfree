from graphs.graph_status import GraphStatus
from graphs.nodes.node_utils import node
from mcp_server_api import get_multi_server_mcp_clients_from_api
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt

@node
async def youtube_search(state: GraphStatus) -> GraphStatus:
    """
    유튜브 검색을 하는 단계
    """
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    tools = await client.get_tools(server_name="youtube_search_mcp")
    
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    prompt = f'''
    Search for 7 YouTube videos related to the instruction.
    For each video, provide the video title, link, thumbnail, and a clear description.
    Exclude negative or inappropriate content and explain how such content was filtered out.
    instruction: {state["instruction"]}
    '''
    
    question_message =  {"role":"user", "content": prompt}
        
    result = await agent.ainvoke({
        "messages": [question_message]
    })
    
    print("😇 YOUTUBE SEARCH RESULT: ",result)
    
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [question_message,generated_message],
        "answer": answer
    }