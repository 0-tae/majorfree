from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from llm_models.chat_gpt import model_instance
import json
import uuid

class SQLAgent:
    def __init__(self, allowed_tables: list[str]):
        self.db = SQLDatabase.from_uri(
            "mysql+mysqlconnector://root:dydrkfl#7!@localhost:3306/cnu_data",
            include_tables = allowed_tables,
            sample_rows_in_table_info=1
            )

        self.model = model_instance.get_model()
        
        self.sql_agent = create_sql_agent(
            llm=self.model,
            db=self.db,
            agent_type="tool-calling",
            verbose=True,
            agent_executor_kwargs={"return_intermediate_steps": True}
        )
    
    def question(self, prompt: str, instruction: str):

        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": instruction}
        ]
        
        result = self.sql_agent.invoke({
            "input": messages
        })
        
        # 중간 단계 출력을 데이터베이스에 저장(미구현)
        if "intermediate_steps" in result:
            for step_order, (action, observation) in enumerate(result["intermediate_steps"]):
                tool_name = action.tool if hasattr(action, 'tool') else "unknown"
                tool_input = action.tool_input if hasattr(action, 'tool_input') else str(action)
                tool_output = str(observation) if observation else ""
                
                if isinstance(tool_input, dict):
                    tool_input = json.dumps(tool_input)
                if isinstance(tool_output, dict):
                    tool_output = json.dumps(tool_output)
        
        return result
    