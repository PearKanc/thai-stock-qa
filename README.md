# 1. สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. ใส่ OpenAI API Key ในไฟล์ .env
echo "OPENAI_API_KEY=sk-xxxxxxxxxx" > .env

# 4. นำเอกสารไปไว้ในโฟลเดอร์ data/ ตามโครงสร้าง
# (ถ้ายังไม่มี ให้สร้างไฟล์ตัวอย่าง เช่น data/stock_recommendations/bbl.md)

# 5. Ingest เอกสาร
python src/ingest.py

# 6. รันเว็บแอป
python flask_app.py

# 7. เปิดเบราว์เซอร์ไปที่ http://localhost:5001
