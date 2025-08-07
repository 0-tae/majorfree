from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from mcp_server_manager import mcp_manager

from models import (
    HttpResponse
)

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