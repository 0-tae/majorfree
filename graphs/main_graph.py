from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, List
from graphs.graph_status import GraphStatus

from graphs.nodes.agent_question import agent_question
from graphs.nodes.department_search import department_search
from graphs.nodes.fast_forward_question import fast_forward_question
from graphs.nodes.init import init
from graphs.nodes.kocw_search import kocw_search
from graphs.nodes.merge_messages import merge_messages
from graphs.nodes.route import route
from graphs.nodes.web_search import web_search
from graphs.nodes.youtube_search import youtube_search
from graphs.nodes.none_action import none_action

import uuid
from utils import time_measurement

class AgentGraphApplication:
    
    @time_measurement
    def __init__(self):
        self.workflow = StateGraph(GraphStatus)
        
        # node - initialize
        self.workflow.add_node("init", init)
        
        # node - main logic
        self.workflow.add_node("youtube_search", youtube_search)
        self.workflow.add_node("kocw_search", kocw_search)
        self.workflow.add_node("web_search", web_search)
        self.workflow.add_node("department_search", department_search)
        self.workflow.add_node("agent_question", agent_question)
        self.workflow.add_node("fast_forward_question", fast_forward_question)
        
        # node - search all
        self.workflow.add_node("search_all_start", none_action)
        self.workflow.add_node("search_all_youtube",youtube_search)
        self.workflow.add_node("search_all_kocw",kocw_search)
        self.workflow.add_node("search_all_web",web_search)
        self.workflow.add_node("search_all_end", none_action)
        
        # node - summarize & evaluate
        self.workflow.add_node("merge_messages", merge_messages)
        
        # edge - depth 1
        self.workflow.add_edge(START, "init")
        
        # edge - depth 2
        self.workflow.add_conditional_edges(
            "init",  # 분기할 노드
            route,   # 분기 조건 함수
            {
                "YOUTUBE_SEARCH": "youtube_search",
                "KOCW_SEARCH": "kocw_search",
                "WEB_SEARCH": "web_search",
                "DEPARTMENT_SEARCH": "department_search",
                "COMMON": "agent_question",
                "FAST_FORWARD": "fast_forward_question",
                "SEARCH_ALL": "search_all_start"
            }
        )
        
        # edge - depth 3
        self.workflow.add_edge("youtube_search", "merge_messages")
        self.workflow.add_edge("kocw_search", "merge_messages")
        self.workflow.add_edge("web_search", "merge_messages")
        self.workflow.add_edge("department_search", "merge_messages")
        self.workflow.add_edge("agent_question", "merge_messages")
        
         # edge - search all
        self.workflow.add_edge("search_all_start", "search_all_youtube")
        self.workflow.add_edge("search_all_youtube", "search_all_kocw")
        self.workflow.add_edge("search_all_kocw", "search_all_web")
        self.workflow.add_edge("search_all_web", "search_all_end")
        self.workflow.add_edge("search_all_end", "merge_messages")
        
        # edge - depth final
        self.workflow.add_edge("fast_forward_question", END)
        self.workflow.add_edge("merge_messages", END)
        
        memory = MemorySaver()

        self.app = self.workflow.compile(checkpointer=memory)
        
    @time_measurement
    async def run(self, question: str, existing_messages: List[Dict[str, Any]] = [], search_type: str = "COMMON", optional_args: Dict[Any, Any] = {}):
        return await self.app.ainvoke({
                                "instruction": question,
                                "messages": existing_messages,
                                "search_type": search_type.upper(), 
                                "optional_args": optional_args},
                               config={"configurable": {"thread_id": uuid.uuid4()}})
        
        
graph_agent_instance = AgentGraphApplication()