from mcp.server.fastmcp import FastMCP
from agent.sql_agent import SQLAgent
from starlette.requests import Request
from starlette.responses import PlainTextResponse
import sys

sql_agent = SQLAgent(allowed_tables=['kocw_lecture'])

mcp = FastMCP(
    name="kocw_lecture_search_mcp",
    description="This server searches for KOCW (Korea Open CourseWare) lectures. When given a `subject_name` and a `department`, it returns lectures with similar information..",
    host='localhost',
    port = 8002
)

@mcp.tool(
    name="kocw_lecture_search",
    description="This server searches for KOCW (Korea Open CourseWare) lectures. When given a `subject_name` and a `department`, it returns lectures with similar information.."
)
def kocw_lecture_search(full_instruction: str) -> str:
    try:
        prompt = f'''
        You are a database administrator with 30 years of experience and act as a query assistant for retrieving lecture information from KOCW (Korea Open CourseWare).
        Your task is to write a SQL `SELECT` query to find lectures from the `kocw_lecture` table that are similar to the given lecture name and department.
        LIMIT data is 10;

        If `full_instruction` includes text that can reasonably be interpreted as a department name, **you must** include a corresponding `WHERE` clause using that department.
        Only include department names that exist in the `kocw_lecture` table. If a non-existent department is specified, the query must result in an error.

        If the course is not found in the database, extract and separate the core keywords from the input course title.
        Example: "%인간컴퓨터상호작용%" -> "%인간%", "%컴퓨터%", "%상호작용%"

        Find the department name that is most similar to the department name provided in the instruction, and write a SQL query using that matched department name.

        The query must return the following columns: `(subject_name, description,university, professor_name, created_at, url)`.
        '''
        
        result = sql_agent.question(prompt, full_instruction)
        
        answer = result["output"]
    
        print(f"데이터 조회 쿼리 : {full_instruction}", file=sys.stderr)
        print(f"데이터 조회 결과 : {result}", file=sys.stderr)
        
        return answer
    except Exception as e:
        print(f"데이터 조회 오류 : {e}", file=sys.stderr)
        return "데이터 조회 오류가 발생했습니다. 다시 시도해주세요. 오류 메시지: {e}"
    
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")

print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")