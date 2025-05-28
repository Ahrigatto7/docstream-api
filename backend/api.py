import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Get environment variables
MONGO_URI = os.getenv("MONGODB_URI")
PORT = int(os.getenv("PORT", 5000))

# ✅ Initialize Flask
app = Flask(__name__)
CORS(app)

# ✅ Connect to MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Force connection check
    db = client.get_database()
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
    data = request.json
    db.logs.insert_one(data)
    return jsonify({"status": "success", "data": data}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
