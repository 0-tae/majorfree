from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# HTTP Response 표준 구조
class HttpResponse(BaseModel):
    status: int
    message: str
    item: Optional[Union[Dict[str, Any], List[Any], Any]] = None

# MCP 서버 설정 응답 모델들
class McpServerConfigInfo(BaseModel):
    name: str
    description: str
    port: int
    transport: str
    server_name: str

class McpServerConfigsResponse(BaseModel):
    group_name: str
    configs: Dict[str, McpServerConfigInfo]

class McpServerRunResponse(BaseModel):
    success: bool
    message: str

class MultiServerMcpClientsResponse(BaseModel):
    client_config: Dict[str, Any]

# 데이터베이스 응답 모델들
class McpServerDbInfo(BaseModel):
    id: Optional[int] = None
    server_name: str
    name: str
    description: str
    prompt: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class McpServerUpdateResponse(BaseModel):
    message: str

# 페이지네이션 응답 모델
class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    per_page: int
    total: int
    has_prev: bool
    has_next: bool

class McpLogsPaginatedResponse(BaseModel):
    logs: List[Dict[str, Any]]
    current_page: int
    total_pages: int
    per_page: int
    total: int
    has_prev: bool
    has_next: bool

class McpLogsRequestGroupsResponse(BaseModel):
    logs: List[Dict[str, Any]]
    request_id: Optional[str] = None
    current_page: int
    total_pages: int
    per_page: int
    total: int
    has_prev: bool
    has_next: bool

class SqlAgentLogsPaginatedResponse(BaseModel):
    logs: List[Dict[str, Any]]
    current_page: int
    total_pages: int
    per_page: int
    total: int
    has_prev: bool
    has_next: bool

class SqlAgentLogsRequestGroupsResponse(BaseModel):
    logs: List[Dict[str, Any]]
    request_id: Optional[str] = None
    current_page: int
    total_pages: int
    per_page: int
    total: int
    has_prev: bool
    has_next: bool

class McpServerInfo(BaseModel):
    id: Optional[int] = None
    server_name: str
    name: str
    description: str
    prompt: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    process_status: Optional[Dict[str, Any]] = None
    is_running: Optional[bool] = None

class McpServerLog(BaseModel):
    id: Optional[int] = None
    mcp_server: str
    name: str
    description: str
    instruction: str
    prompt: str
    answer: str
    request_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SqlAgentLog(BaseModel):
    id: Optional[int] = None
    instruction: str
    tool_name: str
    tool_input: str
    tool_output: str
    step_order: int
    request_id: Optional[str] = None
    execution_time: Optional[datetime] = None
    created_at: Optional[datetime] = None

class McpServerUpdateRequest(BaseModel):
    server_name: str
    name: str
    description: str
    prompt: Optional[str] = None

class McpServerExecuteRequest(BaseModel):
    server_name: str
    name: str
    description: str
    instruction: str
    prompt: Optional[str] = None

class SqlAgentRequest(BaseModel):
    instruction: str
    allowed_tables: List[str] = []

class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str 