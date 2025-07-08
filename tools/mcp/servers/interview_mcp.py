from mcp.server.fastmcp import FastMCP
from llm_models.chat_gpt import model_instance as chat_gpt
from vectordb.chroma.chroma_db import db_instance as chroma_db
from mcp_server_config_loader import get_server_config_from_db
from utils import write_rag_log
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# 데이터베이스에서 서버 설정 로드
server_config = get_server_config_from_db(
    "interview_mcp",
    default_name="Interview RAG MCP",
    default_description="대학교 전공 적성 및 역량 파악을 위한 인터뷰 정보 조회에 특화된 도구. 사용자가 자신의 전공 적성을 말하면 전공 교수의 인터뷰 정보를 찾아 답변을 생성"
)

mcp = FastMCP(
    name=server_config["name"],
    description=server_config["description"],
    host='localhost',
    port = 8002
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")

@mcp.tool(
    name="interview_rag_tool",
    description=server_config["description"]
)
def query_for_interview(user_input: str) -> str:
    context = retreive(user_input)
    
    prompt = f'''주어진 문맥 정보를 사용하여 다음 질문에 답변해 주세요.
            만약 문맥에서 답변을 찾을 수 없다면, "정보를 찾을 수 없습니다"라고 답변하세요.

            [문맥]
            {context}

            [질문]
            {user_input}'''
            
    result = chat_gpt.query(prompt)
    
    write_rag_log(
        mcp_server="interview_rag_tool",
        name=server_config["name"],
        description=server_config["description"], 
        instruction=user_input,
        prompt=prompt,
        answer=result
    )
    
    return result


def retreive(instruction: str) -> str:
    retreive_result = chroma_db.query(input = instruction, filter=[], n_results=10)
    return retreive_result


print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")