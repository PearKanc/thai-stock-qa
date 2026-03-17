# 1. สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. ใส่ OpenAI API Key ในไฟล์ .env
echo "OPENAI_API_KEY=sk-xxxxxxxxxx" > .env

# 4. นำเอกสารไปไว้ในโฟลเดอร์ data/ ตามโครงสร้าง
#thai-stock-qa/
├── data/                     # วางเอกสารทั้งหมด
│   ├── market_reports/
│   ├── stock_recommendations/
│   ├── regulations/
│   └── company_profiles/
├── src/
│   ├── __init__.py
│   ├── ingest.py            # อ่านเอกสาร สร้าง vector store
│   ├── retrieval.py         # ค้นหาและตอบคำถาม
│   ├── models.py            # ตั้งค่าโมเดล embeddings / LLM
│   └── utils.py             # ฟังก์ชันช่วยเหลือ
├── app.py                   # FastAPI (ถ้าทำ web)
├── cli.py                   # Command line interface
├── .env
├── requirements.txt
└── README.md

# 5. Ingest เอกสาร
python src/ingest.py

# 6. รันเว็บแอป
python flask_app.py

# 7. เปิดเบราว์เซอร์ไปที่ http://localhost:5001
