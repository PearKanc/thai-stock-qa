import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()

# ตั้งค่า clients
embedding_model = SentenceTransformer('BAAI/bge-m3')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# เชื่อมต่อ Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("stock_docs")

def search_chunks(query: str, top_k: int = 5):
    # สร้าง embedding ของคำถาม
    query_emb = embedding_model.encode(query).tolist()
    # ค้นหา
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )
    # results มี documents, metadatas, distances
    return results

def build_prompt(query: str, context_chunks: list) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    prompt = f"""คุณคือผู้ช่วยตอบคำถามเกี่ยวกับข้อมูลตลาดหลักทรัพย์ไทย โดยใช้ข้อมูลจากเอกสารที่ให้มาเท่านั้น 
หากข้อมูลในเอกสารไม่เพียงพอให้ตอบว่า "ไม่พบข้อมูลในเอกสารที่มี"

เอกสารอ้างอิง:
{context}

คำถาม: {query}

คำตอบ (พร้อมระบุแหล่งที่มา เช่น ชื่อไฟล์):"""
    return prompt

def answer_question(query: str):
    # ค้นหา
    results = search_chunks(query)
    if not results or not results['documents']:
        return "ไม่พบข้อมูลที่เกี่ยวข้อง"

    # ดึงเอกสารและแหล่งที่มา
    chunks = results['documents'][0]  # list of texts
    metadatas = results['metadatas'][0]  # list of dicts

    # สร้าง prompt
    prompt = build_prompt(query, chunks)

    # เรียก OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",  # หรือ gpt-4-turbo
        messages=[
            {"role": "system", "content": "คุณคือผู้ช่วยตอบคำถามการลงทุน"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    answer = response.choices[0].message.content

    # เพิ่มแหล่งที่มาชัดเจน (ถ้า LLM ไม่ได้ใส่ให้)
    sources = list(set([m['source'] for m in metadatas]))
    source_text = "\n\n**แหล่งอ้างอิง:** " + ", ".join(sources)
    return answer + source_text