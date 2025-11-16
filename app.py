import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import easyocr
import io
from docx import Document
from fpdf import FPDF
import time

# ---------------------- PAGE SETTINGS ---------------------- #
st.set_page_config(page_title="Handwritten to Text", layout="wide")

st.markdown("""
<h1 style='text-align:center; color:#4CAF50; font-size:42px'>
✍️ Handwritten Notes → Digital Text  
<br><span style='font-size:22px;'>AI-Powered Multi-Language Converter</span>
</h1>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Settings")

# ----------------- MULTI-LANGUAGE SUPPORT ----------------- #
languages = st.sidebar.multiselect(
    "Select OCR Languages",
    ["en", "hi", "mr", "ta", "te", "bn"],
    default=["en"]
)

reader = easyocr.Reader(languages)

# ---------------------- IMAGE INPUT ---------------------- #
tab1, tab2 = st.tabs(["📤 Upload Image(s)", "📸 Take Photo"])

images = []

with tab1:
    uploaded_imgs = st.file_uploader(
        "Upload handwritten notes",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )
    if uploaded_imgs:
        for img in uploaded_imgs:
            pil_img = Image.open(img)
            images.append(pil_img)
            st.image(pil_img, use_container_width=True, caption=img.name)

with tab2:
    picture = st.camera_input("Capture handwritten note")
    if picture:
        pil_img = Image.open(picture)
        images.append(pil_img)
        st.image(pil_img, caption="Captured Image", use_container_width=True)

# --------------- AUTO ENHANCEMENT ---------------- #
def enhance_image(img):
    img = img.convert("L")  # grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    return img

# --------------------- PROCESSING ------------------------ #
if len(images) > 0:

    st.markdown("<h3>🔍 Extracting Text...</h3>", unsafe_allow_html=True)
    progress = st.progress(0)
    extracted_text_all = ""

    for i, img in enumerate(images):

        time.sleep(0.3)

        enhanced = enhance_image(img)

        # RUN OCR
        results = reader.readtext(np.array(enhanced), detail=0)
        extracted_text = "\n".join(results)

        extracted_text_all += f"\n\n--- Image {i+1} ---\n{extracted_text}"

        progress.progress((i + 1) / len(images))

    st.success("🎉 Extraction Complete!")

    # Show final editable text
    st.subheader("📝 Extracted Text")
    text_output = st.text_area("Editable text:", extracted_text_all, height=300)

    # ---------------- DOWNLOAD SECTION ---------------- #
    st.subheader("💾 Save Your File")

    option = st.radio(
        "Choose format:",
        ["Text (.txt)", "Word (.docx)", "PDF (.pdf)"],
        horizontal=True
    )

    # ---- TXT ---- #
    if option == "Text (.txt)":
        st.download_button(
            label="📥 Download TXT",
            data=text_output,
            file_name="notes.txt",
            mime="text/plain"
        )

    # ---- DOCX ---- #
    elif option == "Word (.docx)":
        doc = Document()
        doc.add_paragraph(text_output)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="📥 Download DOCX",
            data=buffer,
            file_name="notes.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # ---- PDF ---- #
    elif option == "PDF (.pdf)":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in text_output.split("\n"):
            pdf.multi_cell(0, 10, line)

        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)

        st.download_button(
            label="📥 Download PDF",
            data=buffer,
            file_name="notes.pdf",
            mime="application/pdf"
        )

else:
    st.info("📌 Upload or Capture an image to get started.")