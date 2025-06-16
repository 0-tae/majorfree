from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from tools.llm.chat_gpt import model_instance

class SQLAgent:
    def __init__(self, allowed_tables: list[str]):
        self.db = SQLDatabase.from_uri(
            "mysql+mysqlconnector://root:dydrkfl#7!@localhost:3306/cnu_data",
            include_tables = allowed_tables,
            sample_rows_in_table_info=2)

        self.model = model_instance
        
        self.sql_agent = create_sql_agent(
            llm=self.model,
            db=self.db,
            agent_type="tool-calling",
            verbose=True
        )
        
    def question(self, instruction: str) -> str:
        return self.sql_agent.invoke({
            "input":instruction
        })
    