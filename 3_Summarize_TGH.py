# summarize.py
import openai
import json
import streamlit as st
import re
from DBpostgresql import initialize_db, insert_data
import os

st.title("Together AI")

# Set Together AI API Key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Override OpenAI’s API Base URL
openai.api_base = "https://api.together.xyz/v1"
openai.api_key = TOGETHER_API_KEY

# Initialize Database
initialize_db()

# Model selection dropdown
model_options = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "Qwen/QwQ-32B-Preview",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    "scb10x/scb10x-llama3-typhoon-v1-5x-4f316",
    "mistralai/Mistral-Small-24B-Instruct-2501"
]

st.markdown("""
    <style>
    div[data-baseweb="select"]:focus-within > div {
        border: 2px solid #333dff !important; /* Change border on click */
    }
    </style>
""", unsafe_allow_html=True)

selected_model = st.selectbox("Choose a model:", model_options, index=0, key="model_select", format_func=str)

# Summarize Text using Together AI
def summarize_text(text, model):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Anda adalah AI yang merangkum percakapan dalam bahasa Indonesia."},
                {"role": "user", "content": f"Buat ringkasan singkat dari percakapan berikut dalam bahasa Indonesia:\n\n{text}"}
            ],
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API Error: {str(e)}"

# Convert VTT to JSON
def convert_vtt_to_json(vtt_content):
    data = []
    current_speaker = "Unknown"
    entry = {}
    lines = vtt_content.split("\n")

    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(r"^[\w-]+/\d+-\d+$", line):
            continue
        elif "-->" in line:
            entry = {"speaker": current_speaker, "text": ""}
        elif match := re.match(r"<v\s+([^>]+)>(.+)</v>", line):
            current_speaker, text = match.groups()
            entry["speaker"] = current_speaker
            entry["text"] = text
            data.append(entry)
        elif line and entry:
            entry["text"] += " " + line.strip()

    return json.dumps(data, indent=2, ensure_ascii=False)

# File Upload
uploaded_file = st.file_uploader("Upload a JSON or VTT file", type=["json", "vtt"])

json_text = None
if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1]

    try:
        if file_type == "json":
            json_data = json.load(uploaded_file)
            json_text = json.dumps(json_data, indent=2)
        elif file_type == "vtt":
            vtt_content = uploaded_file.read().decode("utf-8")
            json_text = convert_vtt_to_json(vtt_content)

        with st.expander("View JSON Data", expanded=False):
            st.json(json.loads(json_text))
    except Exception as e:
        st.error(f"Error processing file: {e}")

# Summarize and Store in Database
if json_text is not None:
    if st.button("Summarize"):
        summary = summarize_text(json_text, selected_model)
        st.subheader("Summary")
        st.write(summary)

        # Save to Database
        serial = insert_data(json_text, summary)
        st.success(f"✅ Summary saved with serial number: {serial}")
