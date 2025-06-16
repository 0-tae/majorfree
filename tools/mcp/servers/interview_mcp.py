from mcp.server.fastmcp import FastMCP
from tools.llm.chat_gpt import model_instance as chat_gpt
from vectordb import db_instance as chroma_db

mcp = FastMCP(
    name="Interview RAG MCP",
    description="대학교 전공 적성 및 역량 파악을 위한 인터뷰 정보 조회에 특화된 도구. 사용자가 자신의 전공 적성을 말하면 전공 교수의 인터뷰 정보를 찾아 답변을 생성",
    host='localhost',
    port = 8002
)

@mcp.tool(
    name="Interview RAG MCP",
    description="대학교 전공 적성 및 역량 파악을 위한 인터뷰 정보 조회에 특화된 도구. 사용자가 자신의 전공 적성을 말하면 전공 교수의 인터뷰 정보를 찾아 답변을 생성"
)
def query_for_interview(user_input: str) -> str:
    context = retreive(user_input)
    
    prompt = f'''주어진 문맥 정보를 사용하여 다음 질문에 답변해 주세요.
            만약 문맥에서 답변을 찾을 수 없다면, "정보를 찾을 수 없습니다"라고 답변하세요.

            [문맥]
            {context}

            [질문]
            {user_input}'''
            
    answer = chat_gpt.query(prompt)
    
    result = answer
    
    return result


def retreive(instruction: str) -> str:
    retreive_result = chroma_db.query(input = instruction, filter=[], n_results=10)
    return retreive_result


print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")