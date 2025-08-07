from mcp.server.fastmcp import FastMCP
from agent.sql_agent import SQLAgent
from mcp_server_config_loader import get_server_config_from_db
from starlette.requests import Request
from starlette.responses import PlainTextResponse
import sys

mcp = FastMCP(
    name="cnu_data_mcp",
    description="우리 학교(충남대학교)의 강의계획서, 수강신청, 강의, 과목 정보를 데이터베이스를 이용하여 조회",
    host='localhost',
    port = 8001
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


@mcp.tool(
    name="search_syllabus",
    description="우리 학교(충남대학교)의 과목 및 강의계획서 정보를 조회"
)
def search_syllabus(full_instruction: str) -> str:
    try:
        sql_agent = SQLAgent(allowed_tables=['syllabus'])
        
        print(full_instruction)
        
        prompt = '''
        학과 이름으로 추정되는 정보가 명시된 경우 WHERE 조건절에 반드시 추가하세요.
        구체적인 학년이 명시된 경우 target_year를 WHERE 조건절에 반드시 추가하세요.
        대학원에서 개설된 과목일 경우, 대학원 개설 과목임을 명시해주세요.
        college는 충남대학교가 아닌, 단과 대학을 의미합니다.
        
  
        If the course is not found in the database, extract and separate the core keywords from the input course title.
        Example : "%인간컴퓨터상호작용%" -> "%인간%", "%컴퓨터%", "%상호작용%"
        
        and, extract and separate the core keywords from the input department too.
        Example : ("전기공학과" -> "%전기%"), ("경영학부" -> "%경영%"), ("컴퓨터융합학부" -> "%컴퓨터%", "%융합%"), ("정보통신융합학부" -> "%정보%", "%통신%", "%융합%")
        
        '''
        
        result = sql_agent.question(prompt, full_instruction)
        
        answer = result["output"]
    
        print(f"데이터 조회 쿼리 : {full_instruction}", file=sys.stderr)
        print(f"데이터 조회 결과 : {result}", file=sys.stderr)
        
        return answer 
    except Exception as e:
        print(f"데이터 조회 오류 : {e}", file=sys.stderr)
        return "데이터 조회 오류가 발생했습니다. 다시 시도해주세요. 오류 메시지: {e}"


@mcp.tool(
    name="search_course_registration_info",
    description="우리 학교(충남대학교) 과목의 수강 신청 정보를 조회"
)
def search_course_registration_info(full_instruction: str) -> str:
    try:
        sql_agent = SQLAgent(allowed_tables=['course_registration_info'])
        
        prompt = '''
        학과 이름으로 추정되는 정보가 명시된 경우 WHERE 조건절에 반드시 추가하세요.
        구체적인 학년이 명시된 경우 target_year를 WHERE 조건절에 반드시 추가하세요.
        대학원에서 개설된 과목일 경우, 대학원 개설 과목임을 명시해주세요.
        college는 충남대학교가 아닌, 단과 대학을 의미합니다.
    
        If the course is not found in the database, extract and separate the core keywords from the input course title.
        Example : "%인간컴퓨터상호작용%" -> "%인간%", "%컴퓨터%", "%상호작용%"
        
        and, extract and separate the core keywords from the input department too.
        Example : ("전기공학과" -> "%전기%"), ("경영학부" -> "%경영%"), ("컴퓨터융합학부" -> "%컴퓨터%", "%융합%"), ("정보통신융합학부" -> "%정보%", "%통신%", "%융합%")
        
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