from fastapi import FastAPI, HTTPException
from typing import Optional
import uvicorn
from llm import ChatGPTModel
import os
from models import Question, Answer

app = FastAPI()
llm = ChatGPTModel(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/question", response_model=Answer)
async def handle_question(question: Question):
    try:
        answer = llm.query(question.text)
        
        return Answer(text=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
