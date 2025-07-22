from typing import Optional, List
import httpx
from models import (
    McpServerUpdateRequest, DateRangeRequest
)

# MCP 서버 API 기본 URL
MCP_SERVER_API_BASE_URL = "http://localhost:8888"

import functools

async def _request_api(
    method: str,
    url: str,
    *,
    params: dict = None,
    json: dict = None,
    error_msg: str = "API 요청 실패",
    default=None,
    item_key: str = "item",
    get_item: callable = None,
):
    """
    공통 API 요청 함수
    """
    try:
        async with httpx.AsyncClient() as client:
            # GET 요청에는 json 파라미터를 전달하지 않음
            if method.lower() == "get":
                response = await getattr(client, method)(
                    url,
                    params=params
                )
            else:
                response = await getattr(client, method)(
                    url,
                    params=params,
                    json=json
                )
            response.raise_for_status()
            data = response.json()
            if get_item:
                return get_item(data)
            return data.get(item_key, default)
    except Exception as e:
        print(f"🚨 {error_msg}: {e}")
        return default

async def get_mcp_server_configs_from_api(group_name: str = "default") -> dict:
    """MCP 서버 API에서 설정을 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-server-configs",
        params={"group_name": group_name},
        error_msg="MCP 서버 설정 조회 실패",
        default={}
    )

async def run_mcp_server_via_api(group_name: str, server_name: str) -> bool:
    """MCP 서버 API를 통해 서버를 실행합니다."""
    return await _request_api(
        "post",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-server/run",
        params={"group_name": group_name, "server_name": server_name},
        error_msg="MCP 서버 실행 실패",
        default=False,
        get_item=lambda data: data.get("item", {}).get("success", False)
    )

async def get_multi_server_mcp_clients_from_api() -> dict:
    """MCP 서버 API에서 클라이언트 설정을 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/multi-server-mcp-clients",
        error_msg="MCP 클라이언트 설정 조회 실패",
        default={},
        get_item=lambda data: data.get("item", {}).get("client_config", {})
    )

async def get_mcp_server_from_db_api(server_name: str, name: str) -> dict:
    """MCP 서버 API에서 데이터베이스 서버 정보를 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-server-db/{server_name}",
        params={"name": name},
        error_msg="MCP 서버 DB 조회 실패",
        default=None
    )

async def update_mcp_server_in_db_api(request: McpServerUpdateRequest) -> dict:
    """MCP 서버 API를 통해 데이터베이스 서버 정보를 업데이트합니다."""
    return await _request_api(
        "post",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-server-db/update",
        json=request.dict(),
        error_msg="MCP 서버 DB 업데이트 실패",
        default={"message": "업데이트 실패"}
    )

async def get_mcp_logs_from_db_api(server_name: Optional[str] = None, limit: int = 100) -> List[dict]:
    """MCP 서버 API에서 데이터베이스 로그를 가져옵니다."""
    params = {"limit": limit}
    if server_name:
        params["server_name"] = server_name
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-logs-db",
        params=params,
        error_msg="MCP 로그 DB 조회 실패",
        default=[]
    )

async def get_mcp_logs_paginated_from_db_api(page: int = 1, per_page: int = 10, server_name: Optional[str] = None) -> dict:
    """MCP 서버 API에서 데이터베이스 로그를 페이지네이션으로 가져옵니다."""
    params = {"page": page, "per_page": per_page}
    if server_name:
        params["server_name"] = server_name
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-logs-db/paginated",
        params=params,
        error_msg="MCP 로그 페이지네이션 DB 조회 실패",
        default={"logs": [], "total": 0, "page": page, "per_page": per_page}
    )

async def get_mcp_logs_by_request_groups_from_db_api(page: int = 1, server_name: Optional[str] = None) -> dict:
    """MCP 서버 API에서 request_id로 그룹화된 로그를 가져옵니다."""
    params = {"page": page}
    if server_name:
        params["server_name"] = server_name
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-logs-db/request-groups",
        params=params,
        error_msg="MCP 로그 request 그룹 DB 조회 실패",
        default={"logs": [], "total": 0, "page": page, "per_page": 1}
    )

async def get_mcp_logs_latest_from_db_api(instruction: str, server_name: Optional[str] = None) -> List[dict]:
    """MCP 서버 API에서 최신 로그를 가져옵니다."""
    params = {"instruction": instruction}
    if server_name:
        params["server_name"] = server_name
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-logs-db/latest",
        params=params,
        error_msg="MCP 로그 최신 DB 조회 실패",
        default=[]
    )

async def get_mcp_logs_by_request_id_from_db_api(request_id: str) -> List[dict]:
    """MCP 서버 API에서 특정 request_id 로그를 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-logs-db/by-request/{request_id}",
        error_msg="MCP 로그 request ID DB 조회 실패",
        default=[]
    )

async def save_mcp_log_to_db_api(mcp_server: str, name: str, description: str, instruction: str, prompt: str, answer: str, request_id: str) -> dict:
    """MCP 서버 API를 통해 로그를 저장합니다."""
    params = {
        "mcp_server": mcp_server,
        "name": name,
        "description": description,
        "instruction": instruction,
        "prompt": prompt,
        "answer": answer,
        "request_id": request_id
    }
    return await _request_api(
        "post",
        f"{MCP_SERVER_API_BASE_URL}/api/mcp-logs-db/save",
        params=params,
        error_msg="MCP 로그 저장 실패",
        default={"message": "저장 실패"}
    )

async def get_sql_agent_logs_from_db_api(instruction: Optional[str] = None, limit: int = 100) -> List[dict]:
    """MCP 서버 API에서 SQL Agent 로그를 가져옵니다."""
    params = {"limit": limit}
    if instruction:
        params["instruction"] = instruction
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/sql-agent-logs-db",
        params=params,
        error_msg="SQL Agent 로그 DB 조회 실패",
        default=[]
    )

async def get_sql_agent_logs_paginated_from_db_api(page: int = 1, per_page: int = 10) -> dict:
    """MCP 서버 API에서 SQL Agent 로그를 페이지네이션으로 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/sql-agent-logs-db/paginated",
        params={"page": page, "per_page": per_page},
        error_msg="SQL Agent 로그 페이지네이션 DB 조회 실패",
        default={"logs": [], "total": 0, "page": page, "per_page": per_page}
    )

async def get_sql_agent_logs_by_request_groups_from_db_api(page: int = 1) -> dict:
    """MCP 서버 API에서 SQL Agent 로그를 request_id로 그룹화하여 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/sql-agent-logs-db/request-groups",
        params={"page": page},
        error_msg="SQL Agent 로그 request 그룹 DB 조회 실패",
        default={"logs": [], "total": 0, "page": page, "per_page": 1}
    )

async def get_sql_agent_logs_latest_from_db_api(instruction: str) -> List[dict]:
    """MCP 서버 API에서 SQL Agent 최신 로그를 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/sql-agent-logs-db/latest",
        params={"instruction": instruction},
        error_msg="SQL Agent 로그 최신 DB 조회 실패",
        default=[]
    )

async def get_sql_agent_logs_latest_by_request_id_from_db_api() -> List[dict]:
    """MCP 서버 API에서 SQL Agent 최신 request_id 로그를 가져옵니다."""
    return await _request_api(
        "get",
        f"{MCP_SERVER_API_BASE_URL}/api/sql-agent-logs-db/latest-by-request-id",
        error_msg="SQL Agent 로그 최신 request ID DB 조회 실패",
        default=[]
    )

async def get_sql_agent_logs_by_date_range_from_db_api(request: 'DateRangeRequest') -> List[dict]:
    """MCP 서버 API에서 SQL Agent 로그를 날짜 범위로 가져옵니다."""
    return await _request_api(
        "post",
        f"{MCP_SERVER_API_BASE_URL}/api/sql-agent-logs-db/date-range",
        json=request.dict(),
        error_msg="SQL Agent 로그 날짜 범위 DB 조회 실패",
        default=[]
    )