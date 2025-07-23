from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, List
from graphs.graph_status import GraphStatus
from graphs.nodes import init, conitnue_or_end, youtube_search, agent_question
import uuid

class AgentGraphApplication:
    def __init__(self):
        self.workflow = StateGraph(GraphStatus)
        
        # node
        self.workflow.add_node("init", init)
        self.workflow.add_node("agent_question", agent_question)
        self.workflow.add_node("youtube_search", youtube_search)
        
        # edge
        self.workflow.add_edge(START, "init")
        self.workflow.add_edge("init", "agent_question")
                        
        # conditional_edges
        # 1차 질문 이후 wrapping_answer를 수행할 지 결정
        self.workflow.add_conditional_edges(
            "agent_question",  # 분기할 노드
            conitnue_or_end,   # 분기 조건 함수
            {
                "additional_search": "youtube_search",
                "stop": END
            }
        )
        
        self.workflow.add_edge("youtube_search", END)

        memory = MemorySaver()

        self.app = self.workflow.compile(checkpointer=memory)
    
    async def run(self, question: str, existing_messages: List[Dict[str, Any]] = [], search_type: str = "common", optional_args: Dict[Any, Any] = {}):
        return await self.app.ainvoke({
                                "instruction": question,
                                "messages": existing_messages,
                                "search_type": search_type, 
                                "optional_args": optional_args},
                               config={"configurable": {"thread_id": uuid.uuid4()}})