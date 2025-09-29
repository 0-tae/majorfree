from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from graphs.main_graph import graph_agent_instance as agent
from models import ChatRequest, StatelessChatRequest, HttpResponse
from databases.chat_database import get_chats_by_session_id
import uvicorn, json
from fastapi.websockets import WebSocketDisconnect
from stream_models import AiMessageChunkModel, ChunkMetadataModel
from utils import write_stream_log
from databases.chat_database import get_chats_by_session_id
from databases.redis_connector import existsKey, findBySessionId, save as save_to_redis

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.post("/api/v1/llm/chat", response_model=HttpResponse)
async def chat(request: ChatRequest):
    
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
    result = await agent.run(
              thread_id=request.sessionId,
              question=request.question,
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
    
@app.websocket("/api/v1/llm/chat/stream")
async def chat_stream(websocket: WebSocket):
    try:
        await websocket.accept()
        print("WebSocket 연결 수락됨")
        
        while True:
            try:
                data = await websocket.receive_json()
                session_id = data.get("session_id")
                
                # 1) Redis에 session_id에 대한 채팅목록이 존재하면 로드
                messages = []
                
                if session_id:
                    # Redis에서 채팅 기록 확인
                    redis_exists = await existsKey(session_id)
                    
                    if redis_exists:
                        # Redis에서 메시지 로드
                        messages = await findBySessionId(session_id)
                        print(f"Redis에서 {len(messages)}개의 메시지를 로드했습니다.")
                    else:
                        # 2) Redis에 없다면 MySQL 통해 채팅내역 모두 로드
                        chats = get_chats_by_session_id(session_id)
                        for chat in chats:
                            messages.append({
                                "role": "assistant" if chat.is_bot else "user",
                                "content": chat.content
                            })
                        print(f"MySQL에서 {len(messages)}개의 메시지를 로드했습니다.")
                        
                        # MySQL에서 로드한 메시지를 Redis에 저장
                        if messages:
                            await save_to_redis(session_id, messages)
                
                current_node_name = None
                
                await websocket.send_json({
                    "mode": "loading",
                    "metadata": {
                        "message": "챗봇에게 질문을 전달하고 있어요. 잠시만 기다려주세요."
                    }
                })
                
                async for chunk in agent.run_astream(thread_id=session_id, 
                                                    question=data.get("question"),
                                                    existing_messages=messages,
                                                    search_type=data.get("search_type"),
                                                    optional_args=data.get("optional_args")):
                    
                    if current_node_name is None:
                        init_payload = ChunkMetadataModel.get_client_answer_payload()
                        await websocket.send_json(init_payload)
                    
                    # 스트림 결과를 모델로 매핑
                    raw_ai_message_chunk, raw_chunk_metadata = chunk
                    ai_chunk = AiMessageChunkModel.from_langchain_chunk(raw_ai_message_chunk)
                    meta = ChunkMetadataModel.from_dict(raw_chunk_metadata)

                    # 클라이언트 노티용 페이로드 구성 및 전송
                    payload = meta.to_client_payload()

                    # 노드 이름이 변경되거나 노드 이름이 처음 설정 되었을 때 메타데이터 전송
                    if meta.node_name == "unknown":
                        continue
                    
                    if ((current_node_name != meta.node_name) or (current_node_name is None)):
                        await websocket.send_json(payload)

                    # 최종 메시지 생성 단계(merge_messages) 일 때 메시지 전송
                    if meta.node_name == "merge_messages":
                        await websocket.send_text(ai_chunk.content)

                    current_node_name = meta.node_name

                    # 로그 기록 유틸 호출
                    write_stream_log(ai_chunk, meta, session_id)
                
                await websocket.send_json(
                    {
                        "mode": "end",
                        "metadata": {
                            "message":"답변이 완료되었습니다."
                        }
                    }
                )   
                   
            except WebSocketDisconnect:
                client_host, client_port = websocket.client if hasattr(websocket, "client") else ("알 수 없음", "알 수 없음")
                print(f"클라이언트 연결 종료 - IP: {client_host}, PORT: {client_port}")
                break
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                error_response = ChunkMetadataModel.get_error_payload("[⛔ 오류]: 잘못된 데이터 형식입니다.")
                await websocket.send_json(error_response)
            except Exception as e:
                print(f"WebSocket 처리 중 오류: {e}")
                error_response = ChunkMetadataModel.get_error_payload(f"[⛔ 오류]: 서버에 문제가 발생했습니다. 다시 시도해주세요.")
                await websocket.send_json(error_response)
                break
                
    except WebSocketDisconnect:
        print("WebSocket 연결이 끊어졌습니다.")
    except Exception as e:
        print(f"WebSocket 초기화 중 오류: {e}")
    finally:
        print("WebSocket 연결 종료")
        
@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)