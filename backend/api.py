import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
PORT = int(os.getenv("PORT", 5000))
DB_NAME = os.getenv("MONGO_DB_NAME", "docstream")

app = Flask(__name__)
CORS(app)

# MongoDB 연결
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client[DB_NAME]
    print("✅ Connected to MongoDB")
except ConnectionFailure as e:
    print("❌ MongoDB connection failed:", e)
    db = None

@app.route("/")
def index():
    return "✅ API is running!"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/upload", methods=["POST"])
def upload():
    if not db:
        return jsonify({"error": "MongoDB not connected"}), 500
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400
    data = request.get_json()
    db.logs.insert_one(data)
    return jsonify({"status": "success", "data": data}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
