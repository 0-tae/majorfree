from mcp.server.fastmcp import FastMCP
from agent.sql_agent import SQLAgent
from mcp_server_config_loader import get_server_config_from_db
from starlette.requests import Request
from starlette.responses import PlainTextResponse
import sys

sql_agent = SQLAgent(allowed_tables=['syllabus','departments','course_registration_info'])

# 데이터베이스에서 서버 설정 로드
server_config = get_server_config_from_db(
    "cnu_data_mcp",
    default_name="lecture_major_query_tool",
    default_description="This tool is designed for searching and retrieving information about university departments, majors, and courses, including detailed lecture plans and syllabi. To carry out the user’s request flawlessly, always copy their most recent question exactly as it was asked."
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
def query_for_cnu_data(full_instruction: str) -> str:
    try:
        prompt = '''
        학과 이름으로 추정되는 정보가 명시된 경우 WHERE 조건절에 반드시 추가하세요.
        구체적인 학년이 명시된 경우 target_year를 WHERE 조건절에 반드시 추가하세요.
        대학원에서 개설된 과목일 경우, 대학원 개설 과목임을 명시해주세요.
        '''
        
        result = sql_agent.question(prompt, full_instruction)
        
        answer = result["output"]
    
        print(f"데이터 조회 쿼리 : {full_instruction}", file=sys.stderr)
        print(f"데이터 조회 결과 : {result}", file=sys.stderr)
        
        return answer 
    except Exception as e:
        print(f"데이터 조회 오류 : {e}", file=sys.stderr)
        return "데이터 조회 오류가 발생했습니다. 다시 시도해주세요. 오류 메시지: {e}"
    

    

print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")