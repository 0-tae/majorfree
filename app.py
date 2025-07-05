from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Optional, List
import uvicorn
import subprocess
import psutil
import uuid
from models import (
    McpServerInfo, McpServerLog, SqlAgentLog,
    McpServerUpdateRequest, McpServerExecuteRequest, SqlAgentRequest, DateRangeRequest
)
from mcp_server_database import db as mcp_server_db
from mcp_server_log_database import db as mcp_log_db
from sql_agent_log_database import sql_agent_log_db
from tools.mcp.mcp_server_manager import mcp_manager
from utils import set_current_request_id, clear_current_request_id, get_current_request_id

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
from langchain_core.prompts import PromptTemplate
import asyncio

def check_process_status(port: int) -> bool:
    """특정 포트를 사용하는 프로세스가 실행 중인지 확인합니다."""
    try:
        # lsof 명령어로 포트 사용 프로세스 확인
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True, check=False)
        return result.returncode == 0 and result.stdout.strip() != ''
    except Exception:
        return False

def get_process_info(port: int) -> dict:
    """포트를 사용하는 프로세스 정보를 가져옵니다."""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            pid = result.stdout.strip()
            # psutil로 프로세스 정보 가져오기
            try:
                process = psutil.Process(int(pid))
                return {
                    "pid": pid,
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "create_time": process.create_time()
                }
            except (psutil.NoSuchProcess, ValueError):
                return {"pid": pid, "status": "unknown"}
    except Exception:
        pass
    return {"status": "not_running"}

# MCP 서버 관련 API
@app.get("/api/mcp-servers", response_model=List[McpServerInfo])
async def get_mcp_servers():
    """MCP 서버 목록을 가져옵니다."""
    try:
        # MCP Manager에서 서버 설정 가져오기
        configs = mcp_manager.get_mcp_server_configs("default")
        
        servers = []
        for server_name, config in configs.items():
            # 데이터베이스에서 서버 정보 가져오기
            db_server = mcp_server_db.get_server_by_name(server_name, config.get_name())
            
            # 프로세스 상태 확인
            port = config.get_port()
            process_info = get_process_info(port)
            is_running = process_info["status"] != "not_running"
            
            # 안전하게 description 가져오기
            try:
                description = config.get_description()
            except AttributeError:
                description = f"{server_name} MCP Server"
            
            server_info = McpServerInfo(
                id=db_server[0] if db_server else None,
                server_name=server_name,
                name=config.get_name(),
                description=db_server[3] if db_server else description,
                prompt=db_server[4] if db_server else None,
                created_at=db_server[5] if db_server else None,
                updated_at=db_server[6] if db_server else None
            )
            
            # 프로세스 상태 정보 추가
            server_info.process_status = process_info
            server_info.is_running = is_running
            
            servers.append(server_info)
        
        return servers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp-servers/{server_name}")
async def get_mcp_server_detail(server_name: str):
    """특정 MCP 서버의 상세 정보를 가져옵니다."""
    try:
        configs = mcp_manager.get_mcp_server_configs("default")
        if server_name not in configs:
            raise HTTPException(status_code=404, detail="서버를 찾을 수 없습니다.")
        
        config = configs[server_name]
        db_server = mcp_server_db.get_server_by_name(server_name, config.get_name())
        
        # 프로세스 상태 확인
        port = config.get_port()
        process_info = get_process_info(port)
        is_running = process_info["status"] != "not_running"
        
        # 안전하게 description 가져오기
        try:
            description = config.get_description()
        except AttributeError:
            description = f"{server_name} MCP Server"
        
        return {
            "server_name": server_name,
            "name": config.get_name(),
            "description": db_server[3] if db_server else description,
            "prompt": db_server[4] if db_server else None,
            "port": port,
            "transport": config.get_transport(),
            "is_running": is_running,
            "process_info": process_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp-logs", response_model=List[McpServerLog])
async def get_mcp_logs(server_name: Optional[str] = None, limit: int = 100):
    """MCP 서버 로그를 가져옵니다."""
    try:
        if server_name:
            logs = mcp_log_db.get_logs_by_mcp_server(server_name)
        else:
            logs = mcp_log_db.get_all_logs(limit)
        
        return [
            McpServerLog(
                id=log[0], mcp_server=log[1], name=log[2], description=log[3],
                instruction=log[4], prompt=log[5], answer=log[6],
                created_at=log[7], updated_at=log[8]
            ) for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 페이지네이션 API 추가
@app.get("/api/mcp-logs/paginated")
async def get_mcp_logs_paginated(page: int = 1, per_page: int = 10, server_name: Optional[str] = None):
    """MCP 서버 로그를 페이지네이션으로 가져옵니다."""
    try:
        data = mcp_log_db.get_logs_paginated(page, per_page, server_name)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp-logs/request-groups")
async def get_mcp_logs_by_request_groups(page: int = 1, server_name: Optional[str] = None):
    """MCP 서버 로그를 request_id로 그룹화하여 페이지네이션으로 가져옵니다."""
    try:
        print(f"🔍 MCP request-groups called with page={page}, server_name={server_name}")
        data = mcp_log_db.get_logs_by_request_id_paginated(page, per_page=1, server_name=server_name)
        print(f"🔍 MCP request-groups result: {data}")
        return data
    except Exception as e:
        print(f"🚨 Error in get_mcp_logs_by_request_groups: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp-logs/latest")
async def get_mcp_logs_latest(instruction: str, server_name: Optional[str] = None):
    """특정 instruction에 대한 최신 MCP 로그를 가져옵니다."""
    try:
        logs = mcp_log_db.get_latest_logs_by_instruction(instruction, server_name)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp-logs/by-request/{request_id}")
async def get_mcp_logs_by_request_id(request_id: str):
    """특정 request_id에 해당하는 MCP 로그를 가져옵니다."""
    try:
        logs = mcp_log_db.get_logs_by_request_id(request_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp-servers/update")
async def update_mcp_server(request: McpServerUpdateRequest):
    """MCP 서버 정보를 업데이트합니다."""
    try:
        # 데이터베이스에 서버 정보가 있는지 확인
        configs = mcp_manager.get_mcp_server_configs("default")
        if request.server_name not in configs:
            raise HTTPException(status_code=404, detail="서버를 찾을 수 없습니다.")
        
        config = configs[request.server_name]
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
        
        # 서버 재시작
        success = mcp_manager.run_mcp_server("default", request.server_name)
        
        if success:
            return {"message": "MCP 서버가 성공적으로 업데이트되고 재시작되었습니다."}
        else:
            return {"message": "서버 정보는 업데이트되었지만 재시작에 실패했습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp-servers/execute")
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
        client_config = mcp_manager.get_multi_server_mcp_clients()
        client = MultiServerMCPClient(client_config)

        tools = await client.get_tools()
            
        agent = create_react_agent(model=model,
                                tools=tools)

        
        result = await agent.ainvoke({
            "messages": [
                {"role": "user", "content":request.instruction}
            ]
        })
        
        print(f"🔍 Agent result: {result}")
        
        # 응답 메시지 로그 저장 (메인 실행 로그)
        final_answer = result.get("messages")[-1].content if result.get("messages") else "No response"
        
        
        for message in result.get("messages"):   
            mcp_log_db.save(
                mcp_server=request.server_name,
                name=request.name,
                description=request.description,
                instruction=request.instruction,
                prompt=request.prompt or "None",
                answer=message.content,
                request_id=request_id
            )

        
        return {
            "answer": final_answer,
            "request_id": request_id
        }
    except Exception as e:
        print(f"🚨 Error in execute_mcp_server: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 실행 완료 후 request_id 정리
        print(f"🔍 Clearing request_id: {get_current_request_id()}")
        clear_current_request_id()

# SQL Agent 관련 API
@app.post("/api/sql-agent/execute")
async def execute_sql_agent(request: SqlAgentRequest):
    """SQL Agent를 실행합니다."""
    model = ChatOpenAI(model="gpt-4o-mini", 
                    temperature=0,
                    api_key="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"
                    )

    # 클라이언트 연결
    client_config = mcp_manager.get_multi_server_mcp_clients()
    client = MultiServerMCPClient(client_config)

    tools = asyncio.run(client.get_tools())
        
    agent = create_react_agent(model=model,
                            tools=tools)

    
    try:
        result = asyncio.run(agent.ainvoke({
            "messages": [
                {"role": "user", "content":request.instruction}
            ]
        }))

        print(result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sql-agent/logs", response_model=List[SqlAgentLog])
async def get_sql_agent_logs(instruction: Optional[str] = None, limit: int = 100):
    """SQL Agent 로그를 가져옵니다."""
    try:
        if instruction:
            logs = sql_agent_log_db.get_logs_by_instruction(instruction)
        else:
            logs = sql_agent_log_db.get_all_logs(limit)
        
        return [
            SqlAgentLog(
                id=log[0], instruction=log[1], tool_name=log[2],
                tool_input=log[3], tool_output=log[4], step_order=log[5],
                execution_time=log[6], created_at=log[7]
            ) for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SQL Agent 페이지네이션 API 추가
@app.get("/api/sql-agent/logs/paginated")
async def get_sql_agent_logs_paginated(page: int = 1, per_page: int = 10):
    """SQL Agent 로그를 페이지네이션으로 가져옵니다."""
    try:
        data = sql_agent_log_db.get_logs_paginated(page, per_page)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sql-agent/logs/request-groups")
async def get_sql_agent_logs_by_request_groups(page: int = 1):
    """SQL Agent 로그를 request_id로 그룹화하여 페이지네이션으로 가져옵니다."""
    try:
        data = sql_agent_log_db.get_logs_by_request_id_paginated(page, per_page=1)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sql-agent/logs/latest")
async def get_sql_agent_logs_latest(instruction: str):
    """특정 instruction에 대한 최신 SQL Agent 로그를 가져옵니다."""
    try:
        logs = sql_agent_log_db.get_latest_logs_by_instruction(instruction)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sql-agent/logs/latest-by-request-id")
async def get_sql_agent_logs_latest_by_request_id():
    """가장 최근의 created_at 값을 가진 request_id를 포함하는 SQL Agent 로그 데이터를 가져옵니다."""
    try:
        logs = sql_agent_log_db.get_latest_logs_by_latest_request_id()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sql-agent/logs/date-range")
async def get_sql_agent_logs_by_date_range(request: DateRangeRequest):
    """날짜 범위로 SQL Agent 로그를 가져옵니다."""
    try:
        logs = sql_agent_log_db.get_logs_by_date_range(request.start_date, request.end_date)
        return [
            SqlAgentLog(
                id=log[0], instruction=log[1], tool_name=log[2],
                tool_input=log[3], tool_output=log[4], step_order=log[5],
                execution_time=log[6], created_at=log[7]
            ) for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
