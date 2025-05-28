import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
coll = client["docstream"]["cases"]

st.set_page_config(page_title="DocStream 대시보드", layout="wide")
st.title("📚 저장된 사례 분석")

query = st.text_input("🔍 키워드 검색")
if query:
    results = coll.find({
        "$or": [
            {"source": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}}
        ]
    })
else:
    results = coll.find()

def summarize(text, max_sentences=3):
    sentences = re.split(r'[.!?\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    return " ".join(sentences[:max_sentences])

for doc in results:
    st.markdown(f"### 📄 {doc.get('source', '무제')}")
    st.markdown("**🏷 태그**: " + ", ".join(doc.get("tags", [])))
    st.markdown("**📝 요약**: " + summarize(doc.get("content", "")))
    with st.expander("📚 전체 보기"):
        st.markdown(doc.get("content", ""))
    st.markdown("---")