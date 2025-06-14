from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import base64
import os
from model_utils import generate_answer

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64-encoded image

@app.post("/api/")
async def answer_question(payload: QuestionRequest):
    try:
        answer, links = generate_answer(payload.question, payload.image)
        return {
            "answer": answer,
            "links": links
        }
    except Exception as e:
        return {"error": str(e)}
