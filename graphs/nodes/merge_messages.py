from graphs.graph_status import GraphStatus
from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt

from graphs.nodes.node_utils import node

@node
async def merge_messages(state: GraphStatus) -> GraphStatus:
    """
    메시지를 병합하는 단계
    """
    
    model = chat_gpt
    
    prompt = f'''
    Please reconstruct the message content based on the conversation history so far. 
    
    Please structure your response so that it directly answers the user's most recent question.
    
    If the assistant suggests videos or external links related to the instruction, please provide accessible links to those contents.    
    
    instruction: {state["instruction"]}
    
    You can be a formatting assistant. For each video entry, apply the following rules:

    1. Wrap the entire video block with [[VIDEO]] and [[/VIDEO]].
    2. If a **title** exists, wrap it with [[TITLE]] and [[/TITLE]].
    3. If a **URL/link** exists, wrap it with [[LINK]] and [[/LINK]].
    4. If a **thumbnail** exists, wrap it with [[THUMBNAIL]] and [[/THUMBNAIL]].
    5. If there is any remaining **description or metadata**, place it outside the above tags and wrap it with [[DESCRIPTION]] and [[/DESCRIPTION]].
    6. If any of the title, link, or thumbnail is **missing**, do not include their corresponding tags at all.
    7. Repeat this structure for each video item in the input.

    Only output the properly tagged content. Do not add explanations or comments. Do this consistently for all videos in the list. 
    DESCRIPTION must be in Korean. 
    youtube, kocw, web 검색 결과를 구분하여 태그를 추가해주세요.
    
    Example:
    [[YOUTUBE_VIDEO]]
    [[LINK]]https://www.youtube.com/watch?v=abc123[[/LINK]]
    [[TITLE]]How to Learn Python in 2025[[/TITLE]]
    [[THUMBNAIL]]https://img.youtube.com/vi/abc123/hqdefault.jpg[[/THUMBNAIL]]
    [[DESCRIPTION]]This video is a beginner-friendly guide to learning Python. Uploaded by CodeAcademy. Duration: 12:34. Views: 1.2M[[/DESCRIPTION]]
    [[/YOUTUBE_VIDEO]]

    [[KOCW_VIDEO]]
    [[LINK]]https://www.youtube.com/watch?v=abc123[[/LINK]]
    [[TITLE]]How to Learn Python in 2025[[/TITLE]]
    [[DESCRIPTION]]This video is a beginner-friendly guide to learning Python. Uploaded by CodeAcademy. Duration: 12:34. Views: 1.2M[[/DESCRIPTION]]
    [[/KOCW_VIDEO]]
    
    [[WEB_SEARCH]]
    [[LINK]]https://www.naver.com/search.naver?query=python[[/LINK]]
    [[TITLE]]How to Learn Python in 2025[[/TITLE]]
    [[DESCRIPTION]]This video is a beginner-friendly guide to learning Python. Uploaded by CodeAcademy. Duration: 12:34. Views: 1.2M[[/DESCRIPTION]]
    [[/WEB_SEARCH]]
    '''
    
    state["messages"] += [{"role":"user", "content": prompt}]
    
    result = model.query_by_messages(state["messages"])
    
    answer =  result
    generated_message = {"role":"assistant", "content": answer}
    
    
    return {
        "messages": [generated_message],
        "answer": answer
    }