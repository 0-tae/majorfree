from mcp.server.fastmcp import FastMCP
from tools.agent.sql_agent import SQLAgent

sql_agent = SQLAgent(allowed_tables=['강의계획서','수강신청정보','학과정보'])


mcp = FastMCP(
    name="lecture_major_query_tool",
    description="대학교 학과 학부 전공 강의 추천 및 관련 정보 조회, 강의계획서 조회에 특화된 도구. 사용자가 자신의 학년, 학과, 관심사를 말하면 가장 적합한 강의를 찾아 MySQL 쿼리로 반환함.",
    host='localhost',
    port = 8001
)

@mcp.tool(
    name="lecture_major_query_tool", # TODO: 툴 이름도 참고하므로 의도에 맞게 정의해야함
    description="대학교 학과 학부 전공 강의 추천 및 관련 정보 조회, 강의계획서 조회에 특화된 도구. 사용자가 자신의 학년, 학과, 관심사를 말하면 가장 적합한 강의를 찾아 MySQL 쿼리로 반환함.",
)
def query_for_cnu_data(user_input: str) -> str:
    answer = sql_agent.question(user_input)
    
    result = answer["output"]
    
    return result

print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")