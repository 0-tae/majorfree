from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

import asyncio

async def main():
    model = ChatOpenAI(model="gpt-4o-mini", 
                       temperature=0,
    api_key="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"
                       )
    
    client = MultiServerMCPClient({
        "전공강의추천": {
            "url": "http://localhost:8000/sse",
            "transport": "sse"
        }
    })
    
    tools = await client.get_tools()
    
    agent = create_react_agent(model=model,
                               tools=tools)
    result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": "major courses에 대해 궁금한게 있어. 컴퓨터공학과 강의 목록 알려줘"}
    ]
})
    
    print(result)
if __name__ == "__main__":
    asyncio.run(main())
