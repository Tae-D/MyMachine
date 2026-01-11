from flask import Flask, request, jsonify
from flask_cors import CORS
from AIrecipe import main

app = Flask(__name__)
CORS(app)
@app.route('/process', methods=['post'])
def process_data():
    data = request.json
    user_text = data.get('text', '')
    print(f"Přijato od uživatele: {user_text}")
    user_text=main(user_text, "http://localhost:8080", "Admin","123456")
    return jsonify(user_text)

if __name__ == '__main__':
    app.run(port=5000)