import threading
import uuid
import psutil
import socket
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stream_models import AiMessageChunkModel, ChunkMetadataModel

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

def get_process_info(port: int) -> dict:
    """
    주어진 포트에서 리스닝 중인 프로세스의 상태 정보를 반환합니다.
    프로세스가 없으면 status='not_running'을 반환합니다.
    """
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections', 'create_time']):
            try:
                conns = proc.connections(kind='inet')
                for conn in conns:
                    if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                        return {
                            "status": "running",
                            "pid": proc.pid,
                            "name": proc.name(),
                            "cmdline": proc.cmdline(),
                            "create_time": proc.create_time(),
                        }
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        return {"status": "not_running"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    
    
# 작업 시작 시간과 끝 시간을 출력하는 time_check 데코레이터입니다.
import time
import functools

def time_measurement(func):
    """
    함수의 실행 시작 시간과 끝 시간을 출력하는 데코레이터
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"⏱️ [{func.__name__}] 작업 시작 시간: {start_time:.2f}, 작업 끝 시간: {end_time:.2f}")
        print(f"⏱️ [{func.__name__}] 소요 시간: {end_time - start_time:.2f}초")
        return result
    return wrapper


def write_stream_log(ai_chunk: 'AiMessageChunkModel', meta: 'ChunkMetadataModel') -> None:
    """
    스트리밍 중 수신한 메시지 정보를 로그 파일로 기록합니다.

    파일명은 초 단위 타임스탬프를 포함하여, 동일 초 내 다중 호출에도 누적 기록됩니다.
    """
    try:
        now_str = datetime.now().strftime("%y%m%d-%H:%M:%S")
        log_filename = f"logs/chat_stream_{now_str}.log"

        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(
                f"langgraph_step: {meta.langgraph_step}, "
                f"langgraph_node: {meta.langgraph_node}, "
                f"chunk_content: {ai_chunk.content}, "
                f"langgraph_triggers: {meta.langgraph_triggers}, "
                f"langgraph_path: {meta.langgraph_path}, "
                f"langgraph_checkpoint_ns: {meta.langgraph_checkpoint_ns}, "
                f"checkpoint_ns: {meta.checkpoint_ns}, "
                f"ls_provider: {meta.ls_provider}, "
                f"ls_model_name: {meta.ls_model_name}, "
                f"ls_model_type: {meta.ls_model_type}, "
                f"ls_temperature: {meta.ls_temperature}, "
                f"chunk_id: {ai_chunk.id}, "
                f"chunk_additional_kwargs: {ai_chunk.additional_kwargs}, "
                f"chunk_response_metadata: {ai_chunk.response_metadata}\n"
            )
    except Exception as e:
        print(f"로그 파일 기록 중 오류 발생: {e}")
