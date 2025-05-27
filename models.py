from pydantic import BaseModel

class Question(BaseModel):
    # TODO: 질문과 학과 입력 등의 추가적인 정보 기입
    instruction: str
    user_id: Optional[str] = None

class Answer(BaseModel):
    text: str