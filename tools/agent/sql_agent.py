from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from tools.llm.chat_gpt import model_instance
import sys
import os
import json
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sql_agent_log_database import sql_agent_log_db
from utils import get_current_request_id

class SQLAgent:
    def __init__(self, allowed_tables: list[str]):
        self.db = SQLDatabase.from_uri(
            "mysql+mysqlconnector://root:dydrkfl#7!@localhost:3306/cnu_data",
            include_tables = allowed_tables,
            sample_rows_in_table_info=2)

        self.model = model_instance.get_model()
        
        self.sql_agent = create_sql_agent(
            llm=self.model,
            db=self.db,
            agent_type="tool-calling",
            verbose=True,
            agent_executor_kwargs={"return_intermediate_steps": True}
        )
    
    def question(self, instruction: str):
        # 현재 스레드의 request_id를 가져오거나 새로 생성
        current_request_id = get_current_request_id()
        if not current_request_id:
            current_request_id = str(uuid.uuid4())
        
        result = self.sql_agent.invoke({
            "input": instruction
        })
        
        # 중간 단계 출력을 데이터베이스에 저장
        if "intermediate_steps" in result:
            for step_order, (action, observation) in enumerate(result["intermediate_steps"]):
                tool_name = action.tool if hasattr(action, 'tool') else "unknown"
                tool_input = action.tool_input if hasattr(action, 'tool_input') else str(action)
                tool_output = str(observation) if observation else ""
                
                if isinstance(tool_input, dict):
                    tool_input = json.dumps(tool_input)
                if isinstance(tool_output, dict):
                    tool_output = json.dumps(tool_output)
                
                sql_agent_log_db.save_intermediate_step(
                    instruction=instruction,
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_output=tool_output,
                    step_order=step_order,
                    request_id=current_request_id
                )
        
        return result
    
    def question_with_streaming(self, instruction: str):
        """
        스트리밍 방식으로 SQL Agent를 실행하고 중간 출력을 실시간으로 저장합니다.
        """
        # 현재 스레드의 request_id를 가져오거나 새로 생성
        current_request_id = get_current_request_id()
        if not current_request_id:
            current_request_id = str(uuid.uuid4())
        
        step_order = 0
        
        for step in self.sql_agent.iter({"input": instruction}):
            if "intermediate_step" in step:
                action, observation = step["intermediate_step"]
                tool_name = action.tool if hasattr(action, 'tool') else "unknown"
                tool_input = action.tool_input if hasattr(action, 'tool_input') else str(action)
                tool_output = str(observation) if observation else ""
                
                sql_agent_log_db.save_intermediate_step(
                    instruction=instruction,
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_output=tool_output,
                    step_order=step_order,
                    request_id=current_request_id
                )
                step_order += 1
                
                yield {
                    "step": step_order,
                    "tool": tool_name,
                    "input": tool_input,
                    "output": tool_output,
                    "request_id": current_request_id
                }
            elif "output" in step:
                yield {
                    "final_output": step["output"],
                    "request_id": current_request_id
                }
    