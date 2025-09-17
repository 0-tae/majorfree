from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AiMessageChunkModel:
    content: Optional[str]
    additional_kwargs: Optional[Dict[str, Any]]
    response_metadata: Optional[Dict[str, Any]]
    id: Optional[str]

    @classmethod
    def from_langchain_chunk(cls, ai_message_chunk: Any) -> "AiMessageChunkModel":
        return cls(
            content=getattr(ai_message_chunk, "content", None),
            additional_kwargs=getattr(ai_message_chunk, "additional_kwargs", None),
            response_metadata=getattr(ai_message_chunk, "response_metadata", None),
            id=getattr(ai_message_chunk, "id", None),
        )


@dataclass
class ChunkMetadataModel:
    langgraph_step: Optional[Any]
    langgraph_node: Optional[Any]
    langgraph_triggers: Optional[Any]
    langgraph_path: Optional[Any]
    langgraph_checkpoint_ns: Optional[Any]
    checkpoint_ns: Optional[str]
    ls_provider: Optional[str]
    ls_model_name: Optional[str]
    ls_model_type: Optional[str]
    ls_temperature: Optional[Any]

    @property
    def node_name(self) -> str:
        if self.checkpoint_ns:
            return self.checkpoint_ns.split(":")[0]
        return "unknown"

    @staticmethod
    def get_error_payload(error_message: str) -> bool:
        return {
            "mode": "error",
            "metadata": {
                "message": error_message
            }
        }


    def to_client_payload(self) -> Dict[str, Any]:
        node_name = self.node_name
        return {
            "mode": "loading" if node_name != "merge_messages" else "answer",
            "metadata": {
                "node_name": node_name,
                "message": self.get_message_by_node_name(node_name)
            } if node_name != "merge_messages" else None,
        }
        
    @staticmethod
    def get_client_answer_payload() -> Dict[str, Any]:
        return {
            "mode": "answer",
            "metadata": None
        }

    def get_message_by_node_name(self, node_name: str) -> str:
        return {
            "agent_question": f"답변을 위해 챗봇이 필요한 작업을 선택하고 있어요.",
            "fast_forward_question": f"빠른 답변을 위해 작업을 진행하고 있어요.",
            "youtube_search": "답변을 위해 '유튜브 검색'을 진행하고 있어요.",
            "kocw_search": f"답변을 위해 'KOCW 강의 검색'을 진행하고 있어요.",
            "web_search": f"답변을 위해 '웹 검색'을 진행하고 있어요.",
            "department_search": f"답변을 위해 '학과 정보 검색'을 진행하고 있어요.",
        }.get(node_name, "답변을 위해 작업을 진행하고 있어요.")
        
    @classmethod
    def from_dict(cls, metadata: Optional[Dict[str, Any]]) -> "ChunkMetadataModel":
        data = metadata or {}
        return cls(
            langgraph_step=data.get("langgraph_step"),
            langgraph_node=data.get("langgraph_node"),
            langgraph_triggers=data.get("langgraph_triggers"),
            langgraph_path=data.get("langgraph_path"),
            langgraph_checkpoint_ns=data.get("langgraph_checkpoint_ns"),
            checkpoint_ns=data.get("checkpoint_ns"),
            ls_provider=data.get("ls_provider"),
            ls_model_name=data.get("ls_model_name"),
            ls_model_type=data.get("ls_model_type"),
            ls_temperature=data.get("ls_temperature"),
        )


