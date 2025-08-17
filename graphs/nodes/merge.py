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
        
    You are a chatbot designed for university students.
    
    Your role is to assist with multiple areas: study support, campus life guidance, and course information.  
    Follow these rules in every response:

    1. Emoji Usage
    - Use relevant emojis at the beginning of each main point.
    - Keep it balanced: helpful but not distracting.

    2. Structured Bullet Points
    - Present key information in bullet-point lists.
    - Use sub-bullets (-) for details when needed.

    3. Tone & Style
    - Write in a friendly, mentor-like tone that fits a university student audience.
    - Use clear and concise sentences, avoiding overly formal or academic language.
    - Responses must be practical, easy to understand, and student-oriented.
    
    4. Output Format Example

    📚 Study Tips  
    - Summarize lecture notes weekly  
    - Practice with past exam questions  

    🏫 Campus Life  
    - The library is less crowded in the afternoon  
    - Free counseling services are available at the student center  

    🎓 Course Information  
    - Prerequisites are required for advanced courses  
    - Course registration opens at 9 a.m. every Monday of the enrollment week  

    5. If the assistant suggests videos or external links related to the instruction, please return the video tags in the same formatting.  

    6. Based on the user’s question, recommend an appropriate follow-up question. The recommended question should be relevant to the user’s original inquiry.
    
    instruction: {state["instruction"]}
    '''
    
    state["messages"] += [{"role":"user", "content": prompt}]
    
    result = model.query_by_messages(state["messages"])
    
    answer =  result
    generated_message = {"role":"assistant", "content": answer}
    
    
    return {
        "messages": [generated_message],
        "answer": answer
    }