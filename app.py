from fastapi import FastAPI
from pydantic import BaseModel
from src.retrieval import answer_question

app = FastAPI(title="Thai Stock Q&A")

class Query(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

@app.post("/ask", response_model=Answer)
def ask(query: Query):
    ans = answer_question(query.question)
    return {"answer": ans}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)