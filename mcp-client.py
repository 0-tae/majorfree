from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from tools.mcp.mcp_server_manager import mcp_manager
import asyncio

model = ChatOpenAI(model="gpt-4o-mini", 
                    temperature=0,
                    api_key="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"
                    )

# 클라이언트 연결
client_config = mcp_manager.get_multi_server_mcp_clients()
client = MultiServerMCPClient(client_config)

tools = asyncio.run(client.get_tools())

for tool in tools:
    print("-"*100)
    print(tool.name)
    print(tool.description)
    print(tool.args)
    print(tool.args_schema)
    
agent = create_react_agent(model=model,
                        tools=tools)

result = asyncio.run(agent.ainvoke({
    "messages": [
        {"role": "user", "content": "컴퓨터공학과 강의 목록 알려줘"}
    ]
}))

print(result)