import threading
import uuid

# 스레드 로컬 변수를 사용하여 현재 request_id 저장
_thread_local = threading.local()

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