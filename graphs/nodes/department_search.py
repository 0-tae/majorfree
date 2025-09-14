from graphs.graph_status import GraphStatus
from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt
from tools.mcp.vectordb.chroma.chroma_db import db_instance as chroma_db

from graphs.nodes.node_utils import node

@node
async def department_search(state: GraphStatus) -> GraphStatus:
    """
    학과 정보 탐색을 하는 단계
    """
    model = chat_gpt
    
    instruction = state["instruction"]
    optional_args = state["optional_args"]
    
    if optional_args is None:
        generated_message = {"role":"system", "content": "학과 정보가 주어지지 않아서 답변을 대답할 수 없다는 맥락으로 답변하세요."}
        return {
            "messages": [generated_message],
            "answer": generated_message["content"]
        }
    
    department = optional_args.get("department")
    
    context = retreive(instruction=instruction, department=department)
    
    prompt = f'''Please answer the following question using the provided context information.
                Please follow these guidelines when generating your response:
                    1. Mandatory source citation for all content derived from the provided context
                    2. Format citations as "**[id, question(in context, not instruction), answer]**" after each relevant information
                    3. Distinguish between different sources when using information from multiple references
                    4. Clearly indicate when using general knowledge by noting "commonly known fact" or "general knowledge"
                
                Please respond in Korean.
                
                ### Question
                {instruction}
                
                ### Context
                {context}'''
            
    answer = model.query_by_single_instruction(prompt)
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }

def retreive(instruction: str, department: str = None) -> str:
    retreive_result = chroma_db.query(input = instruction, filter=[department], n_results=10)
    return retreive_result
    