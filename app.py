import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
from groq import Groq
import json
import requests
from streamlit_lottie import st_lottie

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

dark_theme = """
    <style>
        body {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stTextInput > div > div > input {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        .stFileUploader > div {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #ff6347;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 18px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #ff4500;
        }
    </style>
"""
st.markdown(dark_theme, unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align: center; color: #ff6347;'>📜 Research Paper Summarizer 🤖</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size:18px;'>Upload a PDF research paper, and I'll generate a short summary for you! 🚀</p>",
    unsafe_allow_html=True,
)

st_lottie(upload_animation, height=150, key="upload")

uploaded_file = st.file_uploader("📂 Upload a Research Paper (PDF)", type="pdf")

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read()) as doc:
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

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    pdf_text = extract_text_from_pdf(uploaded_file)

    if not pdf_text.strip():
        st.error("❌ No text found in the PDF! Please upload another file.")
        st.stop()

    if st.button("✨ Summarize Now!", use_container_width=True):
        with st.spinner("⏳ Summarizing... please wait!"):
            chunks = split_text(pdf_text)
            summary = "\n".join([summarize_with_groq(chunk) for chunk in chunks])

        st.subheader("🔍 Research Paper Summary")
        st.write(summary)

        st.download_button(
            label="📥 Download Summary",
            data=summary,
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True,
        )
