from database.rag_log_db import db as rag_log_db
import threading
import uuid
from departments import Departments

# 스레드 로컬 변수를 사용하여 현재 request_id 저장
_thread_local = threading.local()
departments = Departments()

def set_current_request_id(request_id: str):
    """현재 스레드의 request_id를 설정합니다."""
    _thread_local.request_id = request_id

def get_current_request_id() -> str:
    """현재 스레드의 request_id를 가져옵니다."""
    return getattr(_thread_local, 'request_id', None)

def clear_current_request_id():
    """현재 스레드의 request_id를 삭제합니다."""
    if hasattr(_thread_local, 'request_id'):
        delattr(_thread_local, 'request_id')

def generate_request_id() -> str:
    """새로운 request_id를 생성합니다."""
    current_request_id = get_current_request_id()
    
    if current_request_id is None:
        current_request_id = str(uuid.uuid4())
        print(f"🔧 새로운 request_id 생성: {current_request_id}")
    
    return current_request_id


def write_rag_log(mcp_server: str, name: str, description: str, instruction: str, prompt: str, answer: str):
    """RAG 로그를 현재 request_id와 함께 저장합니다."""
    request_id = generate_request_id()
    
    rag_log_db.save(
        mcp_server=mcp_server,
        name=name,
        description=description,
        instruction=instruction,
        prompt=prompt,
        answer=answer,
        request_id=request_id
    )
    
    print(f"✅ RAG 로그 저장 완료 - request_id: {request_id}")
    print("WRITE PROMPT:",prompt)
    
def get_departments_info():
    """학과 정보를 반환합니다."""
    return departments.departments
     