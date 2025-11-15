import streamlit as st
from PIL import Image
import numpy as np
import io
from docx import Document
from fpdf import FPDF
import pytesseract
import time

# ---------------------- PAGE SETUP ---------------------- #
st.set_page_config(page_title="Handwritten to Text", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#4CAF50; font-size:42px'>
        ✍️ Handwritten Notes → Digital Text <br> <span style='font-size:22px;'>Modern & Beautiful Converter</span>
    </h1>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------- SIDEBAR ----------------- #
st.sidebar.header("⚙️ Settings")
st.sidebar.info("Upload one or multiple handwritten images or capture using camera. The tool will extract handwritten text and let you download it.")

# --------------- INPUT TABS ----------------- #
tab1, tab2 = st.tabs(["📤 Upload Image(s)", "📸 Take Photo"])

images = []

with tab1:
    uploaded = st.file_uploader("Upload handwritten image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded:
        for img in uploaded:
            pil_img = Image.open(img)
            images.append(pil_img)
            st.image(pil_img, caption=img.name, use_container_width=True)

with tab2:
    picture = st.camera_input("Capture handwritten note")
    if picture:
        pil_img = Image.open(picture)
        images.append(pil_img)
        st.image(pil_img, caption="Captured Image", use_container_width=True)

# -------------- PROCESSING ----------------- #

if len(images) > 0:
    st.markdown("<h3>🔍 Extracting Text from Images...</h3>", unsafe_allow_html=True)

    extracted_full_text = ""

    progress = st.progress(0)
    for i, img in enumerate(images):
        time.sleep(0.4)  # animation delay

        img_array = np.array(img)
        extracted_text = pytesseract.image_to_string(img_array)

        extracted_full_text += f"\n\n--- Image {i+1} ---\n"
        extracted_full_text += extracted_text

        progress.progress((i+1)/len(images))

    st.success("🎉 Text Extracted Successfully!")

    # Display text
    st.subheader("📝 Extracted Text")
    text_output = st.text_area("Editable Text:", extracted_full_text, height=250)

    st.subheader("💾 Save Your File")

    option = st.radio(
        "Choose format:",
        ["Text (.txt)", "Word (.docx)", "PDF (.pdf)"],
        horizontal=True
    )

    # ---------------- TXT ---------------- #
    if option == "Text (.txt)":
        st.download_button(
            label="📥 Download TXT",
            data=text_output,
            file_name="notes.txt",
            mime="text/plain"
        )

    # ---------------- DOCX ---------------- #
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

    # ---------------- PDF ---------------- #
    elif option == "PDF (.pdf)":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in text_output.split("\n"):
            pdf.multi_cell(0, 10, line)

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name="notes.pdf",
            mime="application/pdf"
        )

else:
    st.info("📌 Please upload or capture a handwritten note to begin.")
