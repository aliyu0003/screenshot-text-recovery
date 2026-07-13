import streamlit as st
import pytesseract
from PIL import Image
from pathlib import Path
from datetime import datetime
import json
import os


os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
st.set_page_config(
page_title="Screenshot OCR Organizer",
page_icon="📷",
layout="wide"
)
INDEX_FILE = "index.json"
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
CATEGORY_KEYWORDS = {
"receipt": [
"total",
"subtotal",
"tax",
"receipt",
"cash",
"change due",
"$"
],
"note": [
"todo",
"to do",
"note",
"idea",
"reminder"
],
"whiteboard": [
"diagram",
"flowchart",
"arrow",
"step 1"
],
"quote": [
"said",
"quote",
"“",
"”"
],
"code": [
"def ",
"class ",
"import ",
"function",
"{",
"}",
";"
]
}
def load_index():
    path = OUTPUT_DIR / INDEX_FILE
    if path.exists():
        with open(path, "r", encoding="utf8") as f:
            return json.load(f)
    return {}
def save_index(index):
    with open(OUTPUT_DIR / INDEX_FILE,"w",encoding="utf8") as f:
        json.dump(index,f,indent=2,ensure_ascii=False)
def guess_category(text):
    lower = text.lower()
    scores = {}
    for category, words in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for word in words if word in lower)
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "uncategorized"
        return best
def extract_text(image):
    return pytesseract.image_to_string(image)
index = load_index()
st.title("📷 Screenshot OCR Organizer")
st.write(
    'Upload screenshots or photos. '
    'The app extracts text, categorizes them, '
    'and lets you search later.'
    )
tab1, tab2, tab3 = st.tabs(
[
"Upload",
"Search",
"Categories"
]
)
with tab1:
    st.header("Upload Images")
uploaded_files = st.file_uploader(
"Choose screenshots or photos",
type=["png", "jpg", "jpeg", "bmp", "webp", "tiff"],
accept_multiple_files=True
)
if uploaded_files:
    if st.button("Start OCR"):
        progress = st.progress(0)
        status = st.empty()
        total = len(uploaded_files)
        for i, uploaded in enumerate(uploaded_files):
            status.write(f"Processing **{uploaded.name}**...")
            try:
                image = Image.open(uploaded)
                text = extract_text(image)
                category = guess_category(text)
                index[uploaded.name] = {
                "filename": uploaded.name,
                "category": category,
                "text": text.strip(),
                "processed_at": datetime.now().isoformat(
                timespec="seconds"
                )
                }
                txt_path = OUTPUT_DIR / f"{Path(uploaded.name).stem}.txt"
                with open(
                txt_path,
                "w",
                encoding="utf-8"
                ) as f:
                    f.write(text.strip())
            except Exception as e:
                st.error(f"Failed to process {uploaded.name}\n\n{e}")
            progress.progress((i + 1) / total)
        save_index(index)
        status.success("Finished!")
        st.success(
            f"Processed {len(uploaded_files)} image(s)."
    )
    if index:
        st.divider()
        st.subheader("Previously Processed Images")
        for name, item in index.items():
            with st.expander(name):
                st.write(
                f"**Category:** {item['category']}"
                )
                st.write(
                f"**Processed:** {item['processed_at']}"
                )
                st.text_area(
                "Extracted Text",
                item["text"],
                height=150,
                key=name
        )
# ===========================
# SEARCH TAB
# ===========================
with tab2:
    st.header("Search")
    query = st.text_input(
    "Search extracted text or category"
    )
    if query:
        query = query.lower()
        matches = []
        for name, item in index.items():
            if (
            query in item["text"].lower()
            or query in item["category"].lower()
            ):
                matches.append((name, item))
        if matches:
            st.success(
            f"{len(matches)} result(s) found."
            )
            for name, item in matches:
                with st.expander(name):
                    st.write(
                    f"**Category:** {item['category']}"
                    )
                    st.write(
                    f"**Processed:** {item['processed_at']}"
                    )
                    st.text_area(
                    "Text",
                    item["text"],
                    height=180,
                    key=f"search_{name}"
                    )
            else:
                st.warning("No matches found.")
    # ===========================
# CATEGORY TAB
# ===========================
with tab3:
    st.header("Categories")
    if not index:
        st.info("No images processed yet.")
    else:
        grouped = {}
        for name, item in index.items():
            grouped.setdefault(
                item["category"],
    []
        ).append(name)
        for category in sorted(grouped):
            with st.expander(
                f"{category} ({len(grouped[category])})"
            ):
                for filename in grouped[category]:
                    st.write("📄", filename)
    # ===========================
# DOWNLOAD SECTION
# ===========================
st.divider()
st.subheader("Downloads")
if (OUTPUT_DIR / INDEX_FILE).exists():
    with open(
        OUTPUT_DIR / INDEX_FILE,
        "rb"
    ) as f:
        st.download_button(
    label="⬇ Download index.json",
    data=f,
    file_name="index.json",
    mime="application/json"
    )
txt_files = list(OUTPUT_DIR.glob("*.txt"))
if txt_files:
    selected = st.selectbox(
        "Download extracted text",
        txt_files,
        format_func=lambda x: x.name
)
    with open(selected, "rb") as f:
        st.download_button(
            label="⬇ Download TXT",
            data=f,
            file_name=selected.name,
            mime="text/plain"
            )
# ===========================
# SIDEBAR
# ===========================
st.sidebar.title("OCR Organizer")
st.sidebar.metric(
    "Images Indexed" ,
     len(index))
categories = len(
    set(
        item["category"]
        for item in index.values()
    )
    )
st.sidebar.metric(
    "Categories",
    categories
)
st.sidebar.info(
    "Built with Streamlit + "
    "Pytesseract + Pillow"
)
# ===========================
# FOOTER
# ===========================
st.divider()
st.caption(
    "Screenshot OCR Organizer • Version 1.0"
)
