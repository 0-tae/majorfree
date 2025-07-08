from mcp.server.fastmcp import FastMCP
from agent.sql_agent import SQLAgent
from mcp_server_config_loader import get_server_config_from_db
from starlette.requests import Request
from starlette.responses import PlainTextResponse

sql_agent = SQLAgent(allowed_tables=['lecture_plan','departments','course_registration_info'])

# 데이터베이스에서 서버 설정 로드
server_config = get_server_config_from_db(
    "cnu_data_mcp",
    default_name="lecture_major_query_tool",
    default_description="대학교 학과 학부 전공 강의 추천 및 관련 정보 조회, 강의계획서 조회에 특화된 도구. 사용자가 자신의 학년, 학과, 관심사를 말하면 가장 적합한 강의를 찾아 MySQL 쿼리로 반환함."
)

mcp = FastMCP(
    name=server_config["name"],
    description=server_config["description"],
    host='localhost',
    port = 8001
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


@mcp.tool(
    name=server_config["name"],
    description=server_config["description"]

)
def query_for_cnu_data(user_input: str) -> str:
    result = sql_agent.question(user_input)
    answer = result["output"]
    
    print("RESULT:", result)
    
    return answer 

print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")
mcp.run(transport="sse")