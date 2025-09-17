from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any
import json, os

class ChatGPTModel:
    """
    ChatGPT API를 사용하기 위한 모델 클래스
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        base_dir = os.path.dirname(os.path.abspath(__file__))  # chat_gpt.py의 경로 기준
        config_path = os.path.join(base_dir, "llm_config.json")
        
        with open(config_path) as f:
            llm_config = json.load(f)
            
        self.model = ChatOpenAI(model=model, 
                            temperature=0,
                            api_key=llm_config["OPENAI_API_KEY"])
    
    def get_model(self):
        return self.model
    
    def query_by_single_instruction(self, instruction: str) -> str:
        """
        ChatGPT에 단순 질의를 수행합니다.
        """
        
        try:
            response = self.model.invoke([instruction])
            print("🤖 GPT RESPONSE(SINGLE_INSTRUCTION):",response.content)
            return response.content
        except Exception as e:
            raise Exception(f"ChatGPT API 호출 중 오류 발생: {str(e)}")
        
    def query_by_messages(self, messages: List[Dict[str, Any]]) -> str:
        """
        ChatGPT에 메시지 리스트로 질의를 수행합니다.
        """
        try:
            # Dict 형태의 메시지들을 LangChain Message 객체로 변환
            langchain_messages = []
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
            
            # 변환된 메시지 리스트를 invoke에 전달 (리스트로 감싸지 않음!)
            response = self.model.invoke(langchain_messages)
            
            print("🤖 GPT RESPONSE(MESSAGES):",response.content)
            
            return response.content
            
        except Exception as e:
            raise Exception(f"ChatGPT API 호출 중 오류 발생: {str(e)}")

    async def stream_query_by_messages(self, messages: List[Dict[str, Any]]) -> str:
        """
        ChatGPT에 메시지 리스트로 질의를 수행합니다.
        """
        try:
            # Dict 형태의 메시지들을 LangChain Message 객체로 변환
            langchain_messages = []
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
            
        
            async for chunk in self.model.astream(langchain_messages):
                # chunk는 AIMessageChunk이며 .content 또는 .text 사용 가능
                # 부분 토큰만 포함될 수 있으므로 누적은 호출자 측에서 수행
                yield chunk
            
        except Exception as e:
            raise Exception(f"ChatGPT API 스트리밍 중 오류 발생: {str(e)}")
        
model_instance = ChatGPTModel()