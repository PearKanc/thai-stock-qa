from flask import Flask, render_template, request, jsonify
from src.retrieval import answer_question

app = Flask(__name__)

@app.route('/')
def index():
    """แสดงหน้าแชท"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """รับคำถามจากผู้ใช้ (JSON) และคืนคำตอบ"""
    data = request.get_json()
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'กรุณาระบุคำถาม'}), 400

    try:
        answer = answer_question(question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)