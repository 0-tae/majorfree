from mcp.server.fastmcp import FastMCP
from agent.sql_agent import SQLAgent
from mcp_server_config_loader import get_server_config_from_db
from llm_models.chat_gpt import model_instance as chat_gpt
from vectordb.chroma.chroma_db import db_instance as chroma_db

from starlette.requests import Request
from starlette.responses import PlainTextResponse
import sys

mcp = FastMCP(
    name="department_recommand_search_mcp",
    description="자신이 좋아하는 것, 잘하는 것을 바탕으로 학과 과목을 추천하는 MCP 서버",
    host='localhost',
    port = 8003
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


@mcp.tool(
    name="search_recommand_department",
    description="Call this tool when the user asks for department/major/course recommendations based on their interests, strengths, or hobbies (e.g., ‘What major fits me?’, ‘I like math; which department should I choose?’). It analyzes the university catalog and returns recommendations. Triggers include: ‘major recommendation’, ‘department recommendation’, ‘course suggestion’, ‘적성에 맞는 학과’, ‘학과 추천’, ‘전공 추천’. Input should include interests, strengths, hobbies, and optional constraints (grade, campus, top_k). Output must use only canonical department names from the department field and include reasons and suggested_courses."
)
def search_recommand_department(full_instruction: str) -> str:
    try:
        
        model = chat_gpt
        
        instruction = full_instruction
        
        context = retreive(instruction=instruction)
        
        prompt = f'''Please answer the following question using the provided context information.
                    Please follow these guidelines when generating your response:
                        1. Mandatory source citation for all content derived from the provided context
                        2. Format citations as "**[id, question(in context, not instruction), answer]**" after each relevant information
                        3. Distinguish between different sources when using information from multiple references
                        4. Clearly indicate when using general knowledge by noting "commonly known fact" or "general knowledge"
                        5. Recommending academic departments or majors, use only the department names listed in the “department” field.
                    
                    Please respond in Korean.
                    
                    ### Question
                    {instruction}
                    
                    ### Context
                    {context}'''

        answer = model.query_by_single_instruction(prompt)
        
        return answer 
    except Exception as e:
        print(f"데이터 조회 오류 : {e}", file=sys.stderr)
        return "데이터 조회 오류가 발생했습니다. 다시 시도해주세요. 오류 메시지: {e}"

def retreive(instruction: str, department: str = None) -> str:
    retreive_result = chroma_db.query(input = instruction, n_results=10)
    return retreive_result

print(f"MCP Server({mcp.name}) is running...")
mcp.run(transport="sse")