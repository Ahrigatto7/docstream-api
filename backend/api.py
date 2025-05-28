from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from parser import extract_text_from_pdf, extract_tags, extract_links
import os, datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGODB_URI"))
coll = client["docstream"]["cases"]

@app.route("/api/upload", methods=["POST"])
def upload_pdf():
    file = request.files["file"]
    path = f"/tmp/{file.filename}"
    file.save(path)
    text = extract_text_from_pdf(path)
    tags = extract_tags(text)
    links = extract_links(text)
    doc_id = f"upload_{file.filename}"
    doc = {
        "_id": doc_id,
        "source": file.filename,
        "content": text,
        "tags": tags,
        "linked_ids": links,
        "favorited": False,
        "version": 1,
        "history": [],
        "created_at": datetime.datetime.now().isoformat()
    }
    coll.update_one({"_id": doc_id}, {"$set": doc}, upsert=True)
    return jsonify({"status": "saved", "id": doc_id})

@app.route("/api/cases", methods=["GET"])
def search_cases():
    q = request.args.get("q", "")
    query = {"$or": [
        {"title": {"$regex": q, "$options": "i"}},
        {"content": {"$regex": q, "$options": "i"}},
        {"tags": {"$regex": q, "$options": "i"}}
    ]} if q else {}
    docs = list(coll.find(query))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return jsonify(docs)

@app.route("/api/cases/<id>", methods=["GET"])
def get_case(id):
    doc = coll.find_one({"_id": id})
    if doc:
        doc["_id"] = str(doc["_id"])
        return jsonify(doc)
    return jsonify({"error": "not found"}), 404

@app.route("/api/cases/<id>/update", methods=["POST"])
def update_case(id):
    data = request.json
    doc = coll.find_one({"_id": id})
    if not doc:
        return jsonify({"error": "not found"}), 404
    version = doc.get("version", 1) + 1
    history = doc.get("history", [])
    history.append({
        "version": version - 1,
        "content": doc["content"],
        "updated": datetime.datetime.now().isoformat()
    })
    coll.update_one({"_id": id}, {
        "$set": {
            "content": data["content"],
            "version": version,
            "history": history
        }
    })
    return jsonify({"_id": id, "version": version})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
