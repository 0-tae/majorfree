import openai
from typing import Optional

class ChatGPTModel:
    """
    ChatGPT API를 사용하기 위한 모델 클래스
    """
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        ChatGPTModel 초기화
        
        Args:
            api_key (str): OpenAI API 키
            model (str): 사용할 GPT 모델명 (기본값: gpt-3.5-turbo)
        """
        openai.api_key = api_key
        self.model = model
        
    def query(self, instruction: str) -> str:
        """
        ChatGPT에 단순 질의를 수행합니다.
        
        Args:
            instruction (str): 사용자의 질의/지시사항
            
        Returns:
            str: ChatGPT의 응답
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": instruction}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"ChatGPT API 호출 중 오류 발생: {str(e)}")
            
    def query4rag(self, instruction: str, context: str) -> str:
        """
        RAG(Retrieval-Augmented Generation)를 위한 ChatGPT 질의를 수행합니다.
        
        Args:
            instruction (str): 사용자의 질의/지시사항
            context (str): 검색된 문맥 정보
            
        Returns:
            str: ChatGPT의 응답
        """
        try:
            system_prompt = "주어진 문맥 정보를 바탕으로 사용자의 질문에 답변해주세요."
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"문맥: {context}\n\n질문: {instruction}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"ChatGPT API 호출 중 오류 발생: {str(e)}")
