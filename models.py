from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

# HTTP Response 표준 구조
class HttpResponse(BaseModel):
    status: int
    message: str
    item: Optional[Union[Dict[str, Any], List[Any], Any]] = None

class ChatRequest(BaseModel):
    memberId: int
    sessionId: str
    question: str
    chatType: Optional[str] = None
    additionalData: Optional[Dict[str, str]] = None
    
class StatelessChatRequest(BaseModel):
    question: str
    chatType: Optional[str] = None
    additionalData: Optional[Dict[str, str]] = None

class ChatType(str, Enum):
    YOUTUBE_SEARCH = 'YOUTUBE_SEARCH'
    KOCW_SEARCH = 'KOCW_SEARCH'
    WEB_SEARCH = 'WEB_SEARCH'
    DEPARTMENT_SEARCH = 'DEPARTMENT_SEARCH'
    COMMON = 'COMMON'
    FAST_FORWARD = 'FAST_FORWARD'

class ChatSession(BaseModel):
    id: Optional[int] = None
    created_at: datetime
    is_deleted: bool
    modified_at: datetime
    session_id: Optional[str] = None
    member_id: int

class Chat(BaseModel):
    id: Optional[int] = None
    created_at: datetime
    is_deleted: bool
    modified_at: datetime
    chat_type: Optional[ChatType] = None
    content: Optional[str] = None
    is_bot: bool
    chat_session_id: Optional[int] = None
    member_id: int


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