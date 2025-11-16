import streamlit as st
from PIL import Image
import numpy as np
import io
from docx import Document
from fpdf import FPDF
import pytesseract
import time
from datetime import datetime

# ---------------------- PAGE SETUP ---------------------- #
st.set_page_config(page_title="Handwritten to Text", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#4CAF50; font-size:42px'>
        ✍️ Handwritten Notes → Digital Text <br> <span style='font-size:22px;'>Modern & Beautiful Converter</span>
    </h1>
""", unsafe_allow_html=True)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "email": "",
        "language": "eng"
    }

# ------------------ MAIN TABS ------------------ #
main_tab = st.tabs(["👤 Profile", "📝 Convert Notes", "📚 History"])


# -----------------------------------------------------------
#              TAB 1 : USER PROFILE
# -----------------------------------------------------------
with main_tab[0]:
    st.markdown("## 👤 Your Profile")

    st.session_state.profile["name"] = st.text_input(
        "Name", st.session_state.profile["name"]
    )
    st.session_state.profile["email"] = st.text_input(
        "Email", st.session_state.profile["email"]
    )

    st.session_state.profile["language"] = st.selectbox(
        "Preferred OCR Language",
        ["eng", "hin", "mar", "urd", "tam", "kan"],
        index=0
    )

    st.success("Profile Saved Automatically ✔")


# -----------------------------------------------------------
#               TAB 2 : CONVERT NOTES
# -----------------------------------------------------------
with main_tab[1]:

    st.sidebar.header("⚙️ Settings")
    st.sidebar.info("Upload or capture handwritten images. Tool extracts text & saves it.")

    tab1, tab2 = st.tabs(["📤 Upload Image(s)", "📸 Take Photo"])

    images = []

    # ---------- Upload Multiple Images ----------
    with tab1:
        uploaded = st.file_uploader("Upload handwritten image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if uploaded:
            for img in uploaded:
                pil_img = Image.open(img)
                images.append(pil_img)
                st.image(pil_img, caption=img.name, use_container_width=True)

    # ---------- Camera Capture ----------
    with tab2:
        picture = st.camera_input("Capture handwritten note")
        if picture:
            pil_img = Image.open(picture)
            images.append(pil_img)
            st.image(pil_img, caption="Captured Image", use_container_width=True)

    # ---------- PROCESSING ----------
    if len(images) > 0:
        st.markdown("<h3>🔍 Extracting Text from Images...</h3>", unsafe_allow_html=True)

        extracted_full_text = ""

        progress = st.progress(0)

        for i, img in enumerate(images):
            time.sleep(0.4)

            img_array = np.array(img)

            extracted_text = pytesseract.image_to_string(
                img_array,
                lang=st.session_state.profile["language"]
            )

            extracted_full_text += f"\n\n--- Image {i+1} ---\n"
            extracted_full_text += extracted_text

            progress.progress((i+1) / len(images))

        st.success("🎉 Text Extracted Successfully!")

        # Save in history
        st.session_state.history.append({
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "text": extracted_full_text
        })

        st.subheader("📝 Extracted Text")
        text_output = st.text_area("Editable Text:", extracted_full_text, height=250)

        st.subheader("💾 Save Your File")

        option = st.radio(
            "Choose format:",
            ["Text (.txt)", "Word (.docx)", "PDF (.pdf)"],
            horizontal=True
        )

        # ---------- TEXT DOWNLOAD ----------
        if option == "Text (.txt)":
            st.download_button(
                label="📥 Download TXT",
                data=text_output,
                file_name="notes.txt",
                mime="text/plain"
            )

        # ---------- DOCX DOWNLOAD ----------
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

        # ---------- PDF DOWNLOAD ----------
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
        st.info("📌 Upload or capture a handwritten note to begin.")


# -----------------------------------------------------------
#                  TAB 3 : HISTORY
# -----------------------------------------------------------
with main_tab[2]:
    st.markdown("## 📚 Conversion History")

    if len(st.session_state.history) == 0:
        st.info("No history yet. Convert some notes first!")
    else:
        for item in st.session_state.history:
            st.markdown(f"### 🕒 {item['timestamp']}")
            st.text_area("Saved text:", item["text"], height=200)

        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.warning("History cleared!")