from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from mcp_server_manager import mcp_manager

from models import (
    HttpResponse, McpServerUpdateRequest, DateRangeRequest,
)
from log_database.mcp_server_database import db as mcp_server_db
from log_database.mcp_server_log_database import db as mcp_log_db
from log_database.sql_agent_log_database import sql_agent_log_db

app = FastAPI(title="MCP Server API", version="1.0.0", port=8888)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/mcp-server-configs", response_model=HttpResponse)
async def get_mcp_server_configs(group_name: str = Query(..., description="MCP 서버 그룹 이름")):
    """MCP 서버 설정을 가져옵니다."""
    try:
        configs = mcp_manager.get_mcp_server_configs(group_name)
        
        # 설정 객체를 직렬화 가능한 형태로 변환
        serialized_configs = {}
        for server_name, config in configs.items():
            try:
                description = config.get_description()
            except AttributeError:
                description = f"{server_name} MCP Server"
            
            serialized_configs[server_name] = {
                "name": config.get_name(),
                "description": description,
                "port": config.get_port(),
                "transport": config.get_transport(),
                "server_name": server_name
            }
        
        return HttpResponse(
            status=200,
            message="MCP 서버 설정을 성공적으로 조회했습니다.",
            item={
                "group_name": group_name,
                "configs": serialized_configs
            }
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"설정 조회 실패: {str(e)}",
            item=None
        )

@app.post("/api/mcp-server/run", response_model=HttpResponse)
async def run_mcp_server(group_name: str, server_name: str):
    """MCP 서버를 실행합니다."""
    try:
        success = mcp_manager.run_mcp_server(group_name, server_name)
        
        if success:
            return HttpResponse(
                status=200,
                message=f"MCP 서버 '{server_name}'이 성공적으로 실행되었습니다.",
                item={
                    "success": True,
                    "message": f"MCP 서버 '{server_name}'이 성공적으로 실행되었습니다."
                }
            )
        else:
            return HttpResponse(
                status=400,
                message=f"MCP 서버 '{server_name}' 실행에 실패했습니다.",
                item={
                    "success": False,
                    "message": f"MCP 서버 '{server_name}' 실행에 실패했습니다."
                }
            )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"서버 실행 실패: {str(e)}",
            item=None
        )

@app.get("/api/multi-server-mcp-clients", response_model=HttpResponse)
async def get_multi_server_mcp_clients():
    """Multi Server MCP 클라이언트 설정을 가져옵니다."""
    try:
        client_config = mcp_manager.get_multi_server_mcp_clients()
        
        # 클라이언트 설정을 직렬화 가능한 형태로 변환
        serialized_config = {}
        for key, value in client_config.items():
            if hasattr(value, '__dict__'):
                # 객체인 경우 딕셔너리로 변환
                serialized_config[key] = vars(value)
            else:
                serialized_config[key] = value
        
        return HttpResponse(
            status=200,
            message="Multi Server MCP 클라이언트 설정을 성공적으로 조회했습니다.",
            item={
                "client_config": serialized_config
            }
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"클라이언트 설정 조회 실패: {str(e)}",
            item=None
        )

# MCP 서버 데이터베이스 관련 API들
@app.get("/api/mcp-server-db/{server_name}", response_model=HttpResponse)
async def get_mcp_server_from_db(server_name: str, name: str):
    """데이터베이스에서 MCP 서버 정보를 가져옵니다."""
    try:
        db_server = mcp_server_db.get_server_by_name(server_name, name)
        if db_server:
            server_info = {
                "id": db_server[0],
                "server_name": db_server[1],
                "name": db_server[2],
                "description": db_server[3],
                "prompt": db_server[4],
                "created_at": db_server[5],
                "updated_at": db_server[6]
            }
            return HttpResponse(
                status=200,
                message="MCP 서버 정보를 성공적으로 조회했습니다.",
                item=server_info
            )
        else:
            return HttpResponse(
                status=404,
                message="서버를 찾을 수 없습니다.",
                item=None
            )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"데이터베이스 조회 실패: {str(e)}",
            item=None
        )

@app.post("/api/mcp-server-db/update", response_model=HttpResponse)
async def update_mcp_server_in_db(request: McpServerUpdateRequest):
    """데이터베이스에서 MCP 서버 정보를 업데이트합니다."""
    try:
        db_server = mcp_server_db.get_server_by_name(request.server_name, request.name)
        
        if db_server:
            # 기존 데이터 업데이트
            mcp_server_db.update(
                server_name=request.server_name,
                name=request.name,
                description=request.description,
                prompt=request.prompt or "None"
            )
        else:
            # 새 데이터 삽입
            mcp_server_db.save(
                server_name=request.server_name,
                name=request.name,
                description=request.description,
                prompt=request.prompt or "None"
            )
        
        return HttpResponse(
            status=200,
            message="MCP 서버 정보가 성공적으로 업데이트되었습니다.",
            item={"message": "MCP 서버 정보가 성공적으로 업데이트되었습니다."}
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"데이터베이스 업데이트 실패: {str(e)}",
            item=None
        )

# MCP 로그 관련 API들
@app.get("/api/mcp-logs-db", response_model=HttpResponse)
async def get_mcp_logs_from_db(server_name: Optional[str] = None, limit: int = 100):
    """데이터베이스에서 MCP 서버 로그를 가져옵니다."""
    try:
        if server_name:
            logs = mcp_log_db.get_logs_by_mcp_server(server_name)
        else:
            logs = mcp_log_db.get_all_logs(limit)
        
        log_list = [
            {
                "id": log[0], "mcp_server": log[1], "name": log[2], "description": log[3],
                "instruction": log[4], "prompt": log[5], "answer": log[6],
                "created_at": log[7], "updated_at": log[8]
            } for log in logs
        ]
        
        return HttpResponse(
            status=200,
            message="MCP 서버 로그를 성공적으로 조회했습니다.",
            item=log_list
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs-db/paginated", response_model=HttpResponse)
async def get_mcp_logs_paginated_from_db(page: int = 1, per_page: int = 10, server_name: Optional[str] = None):
    """데이터베이스에서 MCP 서버 로그를 페이지네이션으로 가져옵니다."""
    try:
        data = mcp_log_db.get_logs_paginated(page, per_page, server_name)
        return HttpResponse(
            status=200,
            message="페이지네이션된 MCP 서버 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"페이지네이션 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs-db/request-groups", response_model=HttpResponse)
async def get_mcp_logs_by_request_groups_from_db(page: int = 1, server_name: Optional[str] = None):
    """데이터베이스에서 MCP 서버 로그를 request_id로 그룹화하여 페이지네이션으로 가져옵니다."""
    try:
        data = mcp_log_db.get_logs_by_request_id_paginated(page, per_page=1, server_name=server_name)
        return HttpResponse(
            status=200,
            message="request_id로 그룹화된 MCP 서버 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"request 그룹 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs-db/latest", response_model=HttpResponse)
async def get_mcp_logs_latest_from_db(instruction: str, server_name: Optional[str] = None):
    """데이터베이스에서 특정 instruction에 대한 최신 MCP 로그를 가져옵니다."""
    try:
        logs = mcp_log_db.get_latest_logs_by_instruction(instruction, server_name)
        return HttpResponse(
            status=200,
            message="최신 MCP 서버 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"최신 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/mcp-logs-db/by-request/{request_id}", response_model=HttpResponse)
async def get_mcp_logs_by_request_id_from_db(request_id: str):
    """데이터베이스에서 특정 request_id에 해당하는 MCP 로그를 가져옵니다."""
    try:
        logs = mcp_log_db.get_logs_by_request_id(request_id)
        return HttpResponse(
            status=200,
            message="특정 request_id에 해당하는 MCP 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"request ID 로그 조회 실패: {str(e)}",
            item=None
        )

@app.post("/api/mcp-logs-db/save", response_model=HttpResponse)
async def save_mcp_log_to_db(mcp_server: str, name: str, description: str, instruction: str, prompt: str, answer: str, request_id: str):
    """데이터베이스에 MCP 로그를 저장합니다."""
    try:
        mcp_log_db.save(
            mcp_server=mcp_server,
            name=name,
            description=description,
            instruction=instruction,
            prompt=prompt,
            answer=answer,
            request_id=request_id
        )
        return HttpResponse(
            status=200,
            message="MCP 로그가 성공적으로 저장되었습니다.",
            item={"message": "MCP 로그가 성공적으로 저장되었습니다."}
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"로그 저장 실패: {str(e)}",
            item=None
        )

# SQL Agent 로그 관련 API들
@app.get("/api/sql-agent-logs-db", response_model=HttpResponse)
async def get_sql_agent_logs_from_db(instruction: Optional[str] = None, limit: int = 100):
    """데이터베이스에서 SQL Agent 로그를 가져옵니다."""
    try:
        if instruction:
            logs = sql_agent_log_db.get_logs_by_instruction(instruction)
        else:
            logs = sql_agent_log_db.get_all_logs(limit)
        
        log_list = [
            {
                "id": log[0], "instruction": log[1], "tool_name": log[2],
                "tool_input": log[3], "tool_output": log[4], "step_order": log[5],
                "execution_time": log[6], "created_at": log[7]
            } for log in logs
        ]
        
        return HttpResponse(
            status=200,
            message="SQL Agent 로그를 성공적으로 조회했습니다.",
            item=log_list
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent-logs-db/paginated", response_model=HttpResponse)
async def get_sql_agent_logs_paginated_from_db(page: int = 1, per_page: int = 10):
    """데이터베이스에서 SQL Agent 로그를 페이지네이션으로 가져옵니다."""
    try:
        data = sql_agent_log_db.get_logs_paginated(page, per_page)
        return HttpResponse(
            status=200,
            message="페이지네이션된 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent 페이지네이션 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent-logs-db/request-groups", response_model=HttpResponse)
async def get_sql_agent_logs_by_request_groups_from_db(page: int = 1):
    """데이터베이스에서 SQL Agent 로그를 request_id로 그룹화하여 페이지네이션으로 가져옵니다."""
    try:
        data = sql_agent_log_db.get_logs_by_request_id_paginated(page, per_page=1)
        return HttpResponse(
            status=200,
            message="request_id로 그룹화된 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=data
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent request 그룹 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent-logs-db/latest", response_model=HttpResponse)
async def get_sql_agent_logs_latest_from_db(instruction: str):
    """데이터베이스에서 특정 instruction에 대한 최신 SQL Agent 로그를 가져옵니다."""
    try:
        logs = sql_agent_log_db.get_latest_logs_by_instruction(instruction)
        return HttpResponse(
            status=200,
            message="특정 instruction에 대한 최신 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent 최신 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/api/sql-agent-logs-db/latest-by-request-id", response_model=HttpResponse)
async def get_sql_agent_logs_latest_by_request_id_from_db():
    """데이터베이스에서 가장 최근의 created_at 값을 가진 request_id를 포함하는 SQL Agent 로그 데이터를 가져옵니다."""
    try:
        logs = sql_agent_log_db.get_latest_logs_by_latest_request_id()
        return HttpResponse(
            status=200,
            message="최신 request_id에 해당하는 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=logs
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent 최신 request ID 로그 조회 실패: {str(e)}",
            item=None
        )

@app.post("/api/sql-agent-logs-db/date-range", response_model=HttpResponse)
async def get_sql_agent_logs_by_date_range_from_db(request: DateRangeRequest):
    """데이터베이스에서 날짜 범위로 SQL Agent 로그를 가져옵니다."""
    try:
        logs = sql_agent_log_db.get_logs_by_date_range(request.start_date, request.end_date)
        log_list = [
            {
                "id": log[0], "instruction": log[1], "tool_name": log[2],
                "tool_input": log[3], "tool_output": log[4], "step_order": log[5],
                "execution_time": log[6], "created_at": log[7]
            } for log in logs
        ]
        
        return HttpResponse(
            status=200,
            message="날짜 범위에 해당하는 SQL Agent 로그를 성공적으로 조회했습니다.",
            item=log_list
        )
    except Exception as e:
        return HttpResponse(
            status=500,
            message=f"SQL Agent 날짜 범위 로그 조회 실패: {str(e)}",
            item=None
        )

@app.get("/health", response_model=HttpResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    return HttpResponse(
        status=200,
        message="서비스가 정상적으로 작동 중입니다.",
        item={"status": "healthy", "service": "MCP Server API"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888) 