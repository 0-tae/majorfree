from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Optional
import uvicorn
import uuid
from models import (
    HttpResponse, McpServerUpdateRequest, McpServerExecuteRequest, DateRangeRequest
)
from utils import set_current_request_id, clear_current_request_id, get_current_request_id, get_process_info

app = FastAPI(title="MCP Server & SQL Agent Dashboard", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from mcp_server_api import (
    get_mcp_server_configs_from_api,
    get_mcp_server_from_db_api,
    get_mcp_logs_from_db_api,
    get_mcp_logs_paginated_from_db_api,
    get_mcp_logs_by_request_groups_from_db_api,
    get_sql_agent_logs_from_db_api,
    get_mcp_logs_by_request_id_from_db_api,
    save_mcp_log_to_db_api,
    get_sql_agent_logs_from_db_api,
    get_sql_agent_logs_paginated_from_db_api,
    get_sql_agent_logs_by_request_groups_from_db_api,
    get_sql_agent_logs_latest_from_db_api,
    get_sql_agent_logs_latest_by_request_id_from_db_api,
    get_sql_agent_logs_by_date_range_from_db_api,
    update_mcp_server_in_db_api,
    run_mcp_server_via_api,
    get_mcp_logs_latest_from_db_api,
    get_multi_server_mcp_clients_from_api
)

# MCP 서버 관련 API
@app.get("/api/mcp-servers", response_model=HttpResponse)
async def get_mcp_servers():
    """MCP 서버 목록을 가져옵니다."""
    try:
        # MCP 서버 API에서 서버 설정 가져오기
        response = await get_mcp_server_configs_from_api("default")
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "configs" in response:
            configs = response["configs"]
        else:
            # 기존 API 호출 방식
            configs = response
        
        servers = []
        for server_name, config in configs.items():
            # 데이터베이스에서 서버 정보 가져오기 (API 호출)
            db_response = await get_mcp_server_from_db_api(server_name, config.get("name"))
            db_server = db_response if db_response and not isinstance(db_response, dict) else (db_response.get("item") if db_response else None)
            
            # 프로세스 상태 확인
            port = config.get("port")
            process_info = get_process_info(port)
            is_running = process_info["status"] != "not_running"
            
            # description 가져오기
            description = config.get("description", f"{server_name} MCP Server")
            
            server_info = {
                "id": db_server.get("id") if db_server else None,
                "server_name": server_name,
                "name": config.get("name"),
                "description": db_server.get("description") if db_server else description,
                "prompt": db_server.get("prompt") if db_server else None,
                "created_at": db_server.get("created_at") if db_server else None,
                "updated_at": db_server.get("updated_at") if db_server else None,
                "process_status": process_info,
                "is_running": is_running
            }
            
            servers.append(server_info)
        
        return HttpResponse(
            status=200,
            message="MCP 서버 목록을 성공적으로 조회했습니다.",
            item=servers
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"MCP 서버 목록 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-servers/{server_name}", response_model=HttpResponse)
async def get_mcp_server_detail(server_name: str):
    """특정 MCP 서버의 상세 정보를 가져옵니다."""
    try:
        response = await get_mcp_server_configs_from_api("default")
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "configs" in response:
            configs = response["configs"]
        else:
            configs = response
            
        if server_name not in configs:
            return HttpResponse(
                status=404,
                message="서버를 찾을 수 없습니다.",
                item=None
            )
        
        config = configs[server_name]
        db_response = await get_mcp_server_from_db_api(server_name, config.get("name"))
        db_server = db_response if db_response and not isinstance(db_response, dict) else (db_response.get("item") if db_response else None)
        
        # 프로세스 상태 확인
        port = config.get("port")
        process_info = get_process_info(port)
        is_running = process_info["status"] != "not_running"
        
        # description 가져오기
        description = config.get("description", f"{server_name} MCP Server")
        
        server_detail = {
            "server_name": server_name,
            "name": config.get("name"),
            "description": db_server.get("description") if db_server else description,
            "prompt": db_server.get("prompt") if db_server else None,
            "port": port,
            "transport": config.get("transport"),
            "is_running": is_running,
            "process_info": process_info
        }
        
        return HttpResponse(
            status=200,
            message="MCP 서버 상세 정보를 성공적으로 조회했습니다.",
            item=server_detail
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"MCP 서버 상세 정보 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs", response_model=HttpResponse)
async def get_mcp_logs(server_name: Optional[str] = None, limit: int = 100):
    """MCP 서버 로그를 가져옵니다."""
    try:
        response = await get_mcp_logs_from_db_api(server_name, limit)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
        
        return HttpResponse(
            status=200,
            message="MCP 서버 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"MCP 서버 로그 조회 실패: {str(e)}",
            item=None
        )

# 페이지네이션 API 추가
@app.get("/api/mcp-logs/paginated", response_model=HttpResponse)
async def get_mcp_logs_paginated(page: int = 1, per_page: int = 10, server_name: Optional[str] = None):
    """MCP 서버 로그를 페이지네이션으로 가져옵니다."""
    try:
        response = await get_mcp_logs_paginated_from_db_api(page, per_page, server_name)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            data = response["item"]
        else:
            data = response
            
        return HttpResponse(
            status=200,
            message="페이지네이션된 MCP 서버 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"페이지네이션된 MCP 서버 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs/request-groups", response_model=HttpResponse)
async def get_mcp_logs_by_request_groups(page: int = 1, server_name: Optional[str] = None):
    """MCP 서버 로그를 request_id로 그룹화하여 페이지네이션으로 가져옵니다."""
    try:
        print(f"🔍 MCP request-groups called with page={page}, server_name={server_name}")
        response = await get_mcp_logs_by_request_groups_from_db_api(page, server_name)
        print(f"🔍 MCP request-groups result: {response}")
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            data = response["item"]
        else:
            data = response
            
        return HttpResponse(
            status=200,
            message="request_id로 그룹화된 MCP 서버 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        print(f"🚨 Error in get_mcp_logs_by_request_groups: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(
            status=500,
            message=f"request_id로 그룹화된 MCP 서버 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs/latest", response_model=HttpResponse)
async def get_mcp_logs_latest(instruction: str, server_name: Optional[str] = None):
    """특정 instruction에 대한 최신 MCP 로그를 가져옵니다."""
    try:
        response = await get_mcp_logs_latest_from_db_api(instruction, server_name)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
            
        return HttpResponse(
            status=200,
            message="특정 instruction에 대한 최신 MCP 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"최신 MCP 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs/by-request/{request_id}", response_model=HttpResponse)
async def get_mcp_logs_by_request_id(request_id: str):
    """특정 request_id에 해당하는 MCP 로그를 가져옵니다."""
    try:
        response = await get_mcp_logs_by_request_id_from_db_api(request_id)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
            
        return HttpResponse(
            status=200,
            message="특정 request_id에 해당하는 MCP 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"특정 request_id MCP 로그 조회 실패: {str(e)}",
            item=None
        )

@app.post("/api/mcp-servers/update", response_model=HttpResponse)
async def update_mcp_server(request: McpServerUpdateRequest):
    """MCP 서버 정보를 업데이트합니다."""
    try:
        # 데이터베이스에 서버 정보가 있는지 확인
        response = await get_mcp_server_configs_from_api("default")
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "configs" in response:
            configs = response["configs"]
        else:
            configs = response
            
        if request.server_name not in configs:
            return HttpResponse(
                status=404,
                message="서버를 찾을 수 없습니다.",
                item=None
            )
        
        config = configs[request.server_name]
        
        # 데이터베이스 업데이트 (API 호출)
        db_result = await update_mcp_server_in_db_api(request)
        
        # 서버 재시작
        run_response = await run_mcp_server_via_api("default", request.server_name)
        
        # run_response가 HttpResponse 형식인지 확인
        if isinstance(run_response, dict) and "item" in run_response:
            success = run_response["item"].get("success", False)
        else:
            success = run_response
        
        if success:
            return HttpResponse(
                status=200,
                message="MCP 서버가 성공적으로 업데이트되고 재시작되었습니다.",
                item={"message": "MCP 서버가 성공적으로 업데이트되고 재시작되었습니다."}
            )
        else:
            return HttpResponse(
                status=200,
                message="서버 정보는 업데이트되었지만 재시작에 실패했습니다.",
                item={"message": "서버 정보는 업데이트되었지만 재시작에 실패했습니다."}
            )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"MCP 서버 업데이트 실패: {str(e)}",
            item=None
        )

@app.post("/api/mcp-servers/execute", response_model=HttpResponse)
async def execute_mcp_server(request: McpServerExecuteRequest):
    """MCP 서버를 실행하고 결과를 저장합니다."""
    # 고유한 request_id 생성
    request_id = str(uuid.uuid4())
    
    # 현재 스레드에 request_id 설정 (MCP tools에서 사용할 수 있도록)
    set_current_request_id(request_id)
    print(f"🔍 Set current request_id in thread: {get_current_request_id()}")
    
    try:
        model = ChatOpenAI(model="gpt-4o-mini", 
                        temperature=0,
                        api_key="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"
                        )

        # 클라이언트 연결
        response =  await get_multi_server_mcp_clients_from_api()
        
        client_config = response
        
        client = MultiServerMCPClient(client_config)

        tools = await client.get_tools()

        print(f"🔍 Tools: {tools}")
            
        agent = create_react_agent(model=model,
                                tools=tools,
                                debug=True)

        
        result = await agent.ainvoke({
            "messages": [
                {"role": "user", "content":request.instruction}
            ]
        })
        
        print(f"🔍 Agent result: {result}")
        
        # 응답 메시지 로그 저장 (메인 실행 로그)
        final_answer = result.get("messages")[-1].content if result.get("messages") else "No response"
        
        
        for message in result.get("messages"):   
            save_mcp_log_to_db_api(
                mcp_server=request.server_name,
                name=request.name,
                description=request.description,
                instruction=request.instruction,
                prompt=request.prompt or "None",
                answer=message.content,
                request_id=request_id
            )

        
        return HttpResponse(
            status=200,
            message="MCP 서버 실행이 성공적으로 완료되었습니다.",
            item={
                "answer": final_answer,
                "request_id": request_id
            }
        )
    except Exception as e:
        print(f"🚨 Error in execute_mcp_server: {e}")
        return HttpResponse(
            status=500,
            message=f"MCP 서버 실행 실패: {str(e)}",
            item=None
        )
    finally:
        # 실행 완료 후 request_id 정리
        print(f"🔍 Clearing request_id: {get_current_request_id()}")
        clear_current_request_id()

@app.get("/api/sql-agent/logs", response_model=HttpResponse)
async def get_sql_agent_logs(instruction: Optional[str] = None, limit: int = 100):
    """SQL Agent 로그를 가져옵니다."""
    try:
        response = await get_sql_agent_logs_from_db_api(instruction, limit)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
        
        return HttpResponse(
            status=200,
            message="SQL Agent 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

# SQL Agent 페이지네이션 API 추가
@app.get("/api/sql-agent/logs/paginated", response_model=HttpResponse)
async def get_sql_agent_logs_paginated(page: int = 1, per_page: int = 10):
    """SQL Agent 로그를 페이지네이션으로 가져옵니다."""
    try:
        response = await get_sql_agent_logs_paginated_from_db_api(page, per_page)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            data = response["item"]
        else:
            data = response
            
        return HttpResponse(
            status=200,
            message="페이지네이션된 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"페이지네이션된 SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent/logs/request-groups", response_model=HttpResponse)
async def get_sql_agent_logs_by_request_groups(page: int = 1):
    """SQL Agent 로그를 request_id로 그룹화하여 페이지네이션으로 가져옵니다."""
    try:
        response = await get_sql_agent_logs_by_request_groups_from_db_api(page)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            data = response["item"]
        else:
            data = response
            
        return HttpResponse(
            status=200,
            message="request_id로 그룹화된 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"request_id로 그룹화된 SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent/logs/latest", response_model=HttpResponse)
async def get_sql_agent_logs_latest(instruction: str):
    """특정 instruction에 대한 최신 SQL Agent 로그를 가져옵니다."""
    try:
        response = await get_sql_agent_logs_latest_from_db_api(instruction)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
            
        return HttpResponse(
            status=200,
            message="특정 instruction에 대한 최신 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"최신 SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent/logs/latest-by-request-id", response_model=HttpResponse)
async def get_sql_agent_logs_latest_by_request_id():
    """가장 최근의 created_at 값을 가진 request_id를 포함하는 SQL Agent 로그 데이터를 가져옵니다."""
    try:
        response = await get_sql_agent_logs_latest_by_request_id_from_db_api()
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
            
        return HttpResponse(
            status=200,
            message="최신 request_id에 해당하는 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"최신 request_id SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

@app.post("/api/sql-agent/logs/date-range", response_model=HttpResponse)
async def get_sql_agent_logs_by_date_range(request: DateRangeRequest):
    """날짜 범위로 SQL Agent 로그를 가져옵니다."""
    try:
        response = await get_sql_agent_logs_by_date_range_from_db_api(request)
        
        # response가 HttpResponse 형식인지 확인
        if isinstance(response, dict) and "item" in response:
            logs = response["item"]
        else:
            logs = response
            
        return HttpResponse(
            status=200,
            message="날짜 범위에 해당하는 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"날짜 범위 SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

# 웹 페이지 라우트 (템플릿 사용)
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """메인 대시보드 페이지"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/mcp/{server_name}", response_class=HTMLResponse)
async def mcp_server_page(request: Request, server_name: str):
    """개별 MCP 서버 페이지"""
    return templates.TemplateResponse("mcp_server.html", {
        "request": request, 
        "server_name": server_name
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
