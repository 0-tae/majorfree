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
    
    And After search, format the result as follows. For each video entry, apply the following rules:

    1. Wrap the entire video block with [[YOUTUBE_VIDEO]] and [[/YOUTUBE_VIDEO]].
    2. If a **title** exists, wrap it with [[TITLE]] and [[/TITLE]].
    3. If a **URL/link** exists, wrap it with [[LINK]] and [[/LINK]].
    4. If a **thumbnail** exists, wrap it with [[THUMBNAIL]] and [[/THUMBNAIL]].
    5. If there is any remaining **description or metadata**, place it outside the above tags and wrap it with [[DESCRIPTION]] and [[/DESCRIPTION]].
    6. If any of the title, link, or thumbnail is **missing**, do not include their corresponding tags at all.
    7. Repeat this structure for each video item in the input.

    Only output the properly tagged content. Do not add explanations or comments. Do this consistently for all videos in the list. 
    
    Example:
    [[YOUTUBE_VIDEO]]
    [[LINK]] 검색 결과 링크 [[/LINK]]
    [[TITLE]]How to Learn Python in 2025[[/TITLE]]
    [[THUMBNAIL]]썸네일 링크[[/THUMBNAIL]]
    [[DESCRIPTION]]This video is a beginner-friendly guide to learning Python. Uploaded by CodeAcademy. Duration: 12:34. Views: 1.2M[[/DESCRIPTION]]
    [[/YOUTUBE_VIDEO]]
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