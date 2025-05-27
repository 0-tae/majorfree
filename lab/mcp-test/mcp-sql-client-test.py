from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langgraph.prebuilt import create_react_agent

# 1. DB 연결 및 LLM 준비
db = SQLDatabase.from_uri("mysql+mysqlconnector://root:dydrkfl#7!@localhost:3306/cnu")
model = ChatOpenAI(model="gpt-4o-mini", 
                       temperature=0,
    api_key="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"
                       )
# 2. create_sql_agent로 SQL 에이전트 생성 (tool-calling 권장)
sql_agent = create_sql_agent(
    llm=model,
    db=db,
    agent_type="tool-calling",  # 최신 OpenAI 모델은 tool-calling 권장
    verbose=True
)

# 3. SQLDatabaseToolkit에서 도구 추출
# (create_sql_agent 내부적으로 toolkit을 생성하지만, 별도로 toolkit.get_tools()를 써도 무방)
from langchain_community.agent_toolkits import SQLDatabaseToolkit
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# 4. system prompt(스키마 정보 포함) 생성
schema_info = db.get_table_info()  # 테이블/컬럼 등 스키마 정보 문자열
system_prompt = f"""
You are an agent designed to interact with a SQL database.

Database schema:
{schema_info}

Given an input question, create a syntactically correct {db.dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples, always limit your query to at most 5 results.
Do NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
"""

# 5. langgraph.prebuilt의 create_react_agent로 그래프형 에이전트 생성
agent_graph = create_react_agent(
    model=model,
    tools=tools,
    prompt=system_prompt
)

# 6. 질의 실행
question = "컴퓨터공학과의 강의 목록을 알려줘"
result = agent_graph.invoke({
    "messages": [{"role": "user", "content": question}]
})
print(result)
