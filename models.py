from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SqlAgentLog(BaseModel):
    id: Optional[int] = None
    instruction: str
    tool_name: str
    tool_input: str
    tool_output: str
    step_order: int
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