from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import json

class ChatGPTModel:
    """
    ChatGPT API를 사용하기 위한 모델 클래스
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        with open('tools/llm/llm_config.json') as f:
            llm_config = json.loads(f.read())
            
        self.model = ChatOpenAI(model=model, 
                            temperature=0,
                            api_key=llm_config["OPENAI_API_KEY"])
    
    def get_model(self):
        return self.model
    
    def query(self, instruction: str) -> str:
        """
        ChatGPT에 단순 질의를 수행합니다.
        
        Args:
            instruction (str): 사용자의 질의/지시사항
            
        Returns:
            str: ChatGPT의 응답
        """
        try:
            message = HumanMessage(content=instruction)
            response = self.model.invoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"ChatGPT API 호출 중 오류 발생: {str(e)}")


model_instance = ChatGPTModel()