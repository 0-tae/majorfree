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
    
    And After search, format the result as follows. apply the following rules:

    1. Wrap the entire video block with [[WEB_SEARCH]] and [[/WEB_SEARCH]].
    2. If a **title** exists, wrap it with [[TITLE]] and [[/TITLE]].
    3. If a **URL/link** exists, wrap it with [[LINK]] and [[/LINK]].
    4. If a **thumbnail** exists, wrap it with [[THUMBNAIL]] and [[/THUMBNAIL]].
    5. If there is any remaining **description or metadata**, place it outside the above tags and wrap it with [[DESCRIPTION]] and [[/DESCRIPTION]].
    6. If any of the title, link, or thumbnail is **missing**, do not include their corresponding tags at all.
    7. Repeat this structure for each video item in the input.

    Only output the properly tagged content. Do not add explanations or comments. Do this consistently for all videos in the list. 
    DESCRIPTION must be in Korean. 
    
    Example:
    [[WEB_SEARCH]]
    [[LINK]] 검색 결과 링크 [[/LINK]]
    [[TITLE]]How to Learn Python in 2025[[/TITLE]]
    [[DESCRIPTION]]This video is a beginner-friendly guide to learning Python. Uploaded by CodeAcademy. Duration: 12:34. Views: 1.2M[[/DESCRIPTION]]
    [[/WEB_SEARCH]]
    '''
    question_message = {"role":"user", "content": prompt}
        
    result = await agent.ainvoke(
        {"messages": [question_message]}
    )
     
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [question_message, generated_message],
        "answer": answer
    }