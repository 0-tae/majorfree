
# TODO: LLM 서버에 채팅 전송 / 답변 응답하는 API 개발
# LLM 채팅 저장 / 로드 로직 개발
# 추가적인 prompt, args, search_type 입력을 고려하도록 개발

from fastapi import FastAPI, Request
from graphs.main_graph import AgentGraphApplication
from models import ChatRequest, StatelessChatRequest, HttpResponse
from databases.chat_database import get_chats_by_session_id
import uvicorn

app = FastAPI()

@app.post("/api/v1/llm/chat", response_model=HttpResponse)
async def chat(request: ChatRequest):
    agent = AgentGraphApplication()
    
    chats = sorted(get_chats_by_session_id(request.sessionId), key=lambda chat: chat.created_at)
    messages = []
    
    for idx, chat in enumerate(chats):
        role = "assistant" if chat.is_bot else "user"
        
        print(f"chat {idx}: {chat.content}")
        
        messages.append({
            "role": role,
            "content": chat.content
        })
    
    result = await agent.run(question=request.question,
              existing_messages=messages,
              search_type=request.chatType,
              optional_args=request.additionalData
              )
    
    answer = result.get("answer")
    
    print(f"answer: {answer}")
    
    return HttpResponse(
        status=200,
        message="답변이 생성되었습니다.",
        item={"answer":answer}
    )
    
@app.post("/api/v1/llm/query", response_model=HttpResponse)
async def query(request: StatelessChatRequest):
    agent = AgentGraphApplication()
    
    result = await agent.run(question=request.question,
              search_type=request.chatType,
              optional_args=request.additionalData
              )
    
    answer = result.get("answer")
    
    print(f"answer: {answer}")
    
    return HttpResponse(
        status=200,
        message="답변이 생성되었습니다.",
        item={"answer":answer}
    )   
    
@app.post("/api/v1/llm/chat/test", response_model=HttpResponse)
async def chat_test(request: ChatRequest):
    """
    LLM 채팅 테스트용 더미 API입니다. 실제 LLM 호출 없이 더미 데이터를 반환합니다.
    """
    # 기존 chat API와 동일한 응답 구조 사용
    dummy_answer = {
        "role": "assistant",
        "content": "이것은 테스트용 더미 답변입니다."
    }
    return HttpResponse(
        status=200,
        message="답변이 생성되었습니다.",
        item=dummy_answer
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)