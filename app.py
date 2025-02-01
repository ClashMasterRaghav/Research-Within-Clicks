import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
from groq import Groq
import json
import requests
from streamlit_lottie import st_lottie
import pyttsx3
import pptx
from pptx.util import Inches
import tempfile

# Groq API Key
GROQ_API_KEY = "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"
if not GROQ_API_KEY or GROQ_API_KEY == "your-api-key-here":
    st.error("❌ API Key Missing! Please update the API key in the code.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="📜 Research Paper Summarizer", layout="wide")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

upload_animation = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_s4tubmwg.json")

st.markdown(
    "<h1 style='text-align: center; color: #ff6347;'>📜 Research Paper Summarizer 🤖</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size:18px;'>Upload a PDF research paper, and I'll generate a short summary, audio narration, and a PowerPoint presentation! 🚀</p>",
    unsafe_allow_html=True,
)

st_lottie(upload_animation, height=150, key="upload")

uploaded_file = st.file_uploader("📂 Upload a Research Paper (PDF)", type="pdf")

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

def split_text(text, max_length=4000):
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]

def summarize_with_groq(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI research assistant. Summarize the given research paper concisely. Provide a very short, plain-text summary in simple words.",
                },
                {"role": "user", "content": text},
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        engine.save_to_file(text, tmp_audio.name)
        engine.runAndWait()
        return tmp_audio.name

def create_ppt(summary):
    presentation = pptx.Presentation()
    slide_layout = presentation.slide_layouts[5]  # Title Only layout
    
    for i, chunk in enumerate(summary.split('\n')):
        if chunk.strip():
            slide = presentation.slides.add_slide(slide_layout)
            title = slide.shapes.title
            title.text = f"Slide {i + 1}"
            
            textbox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(5))
            text_frame = textbox.text_frame
            text_frame.word_wrap = True
            p = text_frame.add_paragraph()
            p.text = chunk

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_ppt:
        presentation.save(tmp_ppt.name)
        return tmp_ppt.name

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    pdf_text = extract_text_from_pdf(uploaded_file)

    if not pdf_text.strip():
        st.error("❌ No text found in the PDF! Please upload another file.")
        st.stop()

    if st.button("✨ Generate Summary, Audio & PPT!", use_container_width=True):
        with st.spinner("⏳ Processing... please wait!"):
            chunks = split_text(pdf_text)
            summary = "\n".join([summarize_with_groq(chunk) for chunk in chunks])
            audio_path = text_to_speech(summary)
            ppt_path = create_ppt(summary)

        st.subheader("🔍 Research Paper Summary")
        st.write(summary)

        st.download_button("📥 Download Summary", data=summary, file_name="summary.txt", mime="text/plain")
        st.audio(audio_path, format="audio/mp3")
        with open(ppt_path, "rb") as ppt_file:
            st.download_button("📊 Download PowerPoint", ppt_file, file_name="summary_presentation.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
