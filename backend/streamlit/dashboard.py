import os
import streamlit as st
from pymongo import MongoClient
from urllib.parse import urlparse
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ MongoDB 연결
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

# ✅ URI에서 DB 이름 자동 추출
parsed = urlparse(uri)
db_name = parsed.path[1:] or "test"
db = client[db_name]

# ✅ Streamlit 설정
st.set_page_config(page_title="📊 MongoDB Log Viewer", layout="wide")
st.title("📊 Uploaded Data Log")

# ✅ logs 컬렉션에서 데이터 불러오기
collection = db.get_collection("logs")
docs = list(collection.find().sort("_id", -1))

if docs:
    st.subheader("총 데이터 수: {}".format(len(docs)))
    for doc in docs:
        st.json(doc)
else:
    st.info("아직 업로드된 데이터가 없습니다.")
