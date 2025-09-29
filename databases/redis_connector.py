import json
import os
from typing import Any, Dict, List, Optional

from redis.asyncio import Redis


def _get_redis_url() -> str:
    # 환경변수 REDIS_URL을 우선 사용, 없으면 로컬 기본값
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


def _get_session_key(session_id: str) -> str:
    return f"chat:{session_id}"


def _get_ttl_seconds() -> Optional[int]:
    ttl_str = os.getenv("REDIS_TTL_SECONDS", "1800")
    if not ttl_str:
        return None
    try:
        ttl_val = int(ttl_str)
        return ttl_val if ttl_val > 0 else None
    except ValueError:
        return None


class RedisClient:
    _instance: Optional[Redis] = None

    @classmethod
    def get_client(cls) -> Redis:
        if cls._instance is None:
            cls._instance = Redis.from_url(_get_redis_url(), decode_responses=True)
        return cls._instance


async def existsKey(session_id: str) -> bool:
    """세션 키가 Redis에 존재하는지 확인합니다."""
    client = RedisClient.get_client()
    key = _get_session_key(session_id)
    result = await client.exists(key)
    return result > 0


async def findBySessionId(session_id: str) -> List[Dict[str, Any]]:
    """세션의 전체 메시지 목록을 최신순이 아닌 입력 순서로 반환합니다."""
    client = RedisClient.get_client()
    key = _get_session_key(session_id)
    # 리스트에 저장된 각 요소는 JSON 문자열
    items = await client.lrange(key, 0, -1)
    result: List[Dict[str, Any]] = []
    for item in items:
        try:
            result.append(json.loads(item))
        except Exception:
            # 손상된 항목은 무시
            continue
    return result


async def save(session_id: str, messages: List[Dict[str, Any]]) -> None:
    """세션 메시지 목록을 통으로 저장(덮어쓰기)."""
    client = RedisClient.get_client()
    key = _get_session_key(session_id)
    pipe = client.pipeline(transaction=True)
    pipe.delete(key)
    if messages:
        # 입력 순서를 유지하기 위해 lpush 대신 rpush 사용
        pipe.rpush(key, *[json.dumps(m, ensure_ascii=False) for m in messages])
    ttl_seconds = _get_ttl_seconds()
    if ttl_seconds:
        pipe.expire(key, ttl_seconds)
    await pipe.execute()


async def appendMessage(session_id: str, message: Dict[str, Any]) -> None:
    """단일 메시지를 세션 리스트의 끝에 추가."""
    client = RedisClient.get_client()
    key = _get_session_key(session_id)
    await client.rpush(key, json.dumps(message, ensure_ascii=False))
    ttl_seconds = _get_ttl_seconds()
    if ttl_seconds:
        await client.expire(key, ttl_seconds)


async def clearBySessionId(session_id: str) -> None:
    """세션에 해당하는 Redis 키 삭제."""
    client = RedisClient.get_client()
    key = _get_session_key(session_id)
    await client.delete(key)


