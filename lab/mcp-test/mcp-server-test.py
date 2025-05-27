from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "전공강의추천",
    instructions = "You are a helpful assistant that can answer questions about major courses. you can answer only MySQL query text",
    host='0.0.0.0',
    port=8000,
)

@mcp.tool()
def query(query: str) -> str:
    # 데이터베이스 쿼리 실행
    # 쿼리 결과를 반환
    result="SELECT * FROM courses WHERE major = '컴퓨터공학과'"
    return result

if __name__ == "__main__":
    print("MCP Server is running...")
    mcp.run(transport="sse")