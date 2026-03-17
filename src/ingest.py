import os
from pathlib import Path
from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ตั้งค่าโมเดล embeddings
embedding_model = SentenceTransformer('BAAI/bge-m3')

# ฟังก์ชันอ่านข้อความจาก PDF
def read_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # ป้องกัน None
        return text
    except Exception as e:
        print(f"⚠️ Error reading PDF {file_path}: {e}")
        return ""

# ฟังก์ชันอ่านไฟล์ทั้งหมดในโฟลเดอร์
def load_documents(data_dir: str = "data") -> List[dict]:
    docs = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # ใช้นามสกุลแบบ lowercase เพื่อป้องกัน case-sensitive
            ext = os.path.splitext(file)[1].lower()
            if ext == ".pdf":
                print(f"📄 Reading PDF: {file_path}")
                text = read_pdf(file_path)
            elif ext in (".txt", ".md"):
                print(f"📄 Reading text: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except UnicodeDecodeError:
                    # ลองใช้ encoding อื่น (เช่น tis-620 สำหรับภาษาไทย)
                    try:
                        with open(file_path, 'r', encoding='tis-620') as f:
                            text = f.read()
                        print(f"⚠️ Used TIS-620 encoding for {file_path}")
                    except Exception as e:
                        print(f"❌ Cannot read {file_path}: {e}")
                        continue
            else:
                continue  # ไม่สนใจไฟล์ประเภทอื่น

            if text.strip():  # มีเนื้อหา
                docs.append({
                    "text": text,
                    "source": file_path,
                    "category": os.path.basename(root)
                })
            else:
                print(f"⚠️ File {file_path} is empty or unreadable")
    return docs

# ตัดข้อความเป็น chunk
def split_documents(docs: List[dict], chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = []
    for doc in docs:
        texts = text_splitter.split_text(doc["text"])
        for i, text in enumerate(texts):
            if text.strip():  # เฉพาะ chunk ที่ไม่ว่าง
                chunks.append({
                    "text": text,
                    "source": doc["source"],
                    "category": doc["category"],
                    "chunk_id": i
                })
    return chunks

# สร้าง embeddings และเก็บลง Chroma
def create_vector_store(chunks: List[dict], persist_dir="./chroma_db"):
    if not chunks:
        print("❌ No chunks to store. Please check your documents.")
        return

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="stock_docs")

    # เตรียมข้อมูล
    ids = []
    documents = []
    metadatas = []
    embeddings_list = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i}")
        documents.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "category": chunk["category"]
        })
        # สร้าง embedding
        emb = embedding_model.encode(chunk["text"]).tolist()
        embeddings_list.append(emb)

    # เพิ่มลง collection
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings_list
    )
    print(f"✅ Saved {len(chunks)} chunks to ChromaDB at {persist_dir}")

if __name__ == "__main__":
    docs = load_documents()
    print(f"📊 Loaded {len(docs)} documents")
    if docs:
        chunks = split_documents(docs)
        print(f"🔪 Split into {len(chunks)} chunks")
        create_vector_store(chunks)
    else:
        print("❌ No documents loaded. Please add files to the data/ folder.")