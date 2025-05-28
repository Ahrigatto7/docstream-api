import fitz
import re

KEYWORDS = ["혼인관계", "부모관계", "세력", "응기", "자녀", "자식관계", "대상", "록"]

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])

def extract_tags(text):
    return [kw for kw in KEYWORDS if kw in text]

def extract_links(text):
    return re.findall(r"(suam_\d+)", text)