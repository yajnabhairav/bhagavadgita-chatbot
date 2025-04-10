import streamlit as st
import requests
import json
st.set_page_config(page_title="📖 GitaGPT by Adarsh", page_icon="📿")
st.title("📖 GitaGPT - Wisdom from the Bhagavad Gita")
st.write("Ask anything, and receive answers inspired by the Bhagavad Gita 📜✨")

groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ Missing Groq API key. Please add it to .streamlit/secrets.toml.")
    st.stop()

model_catalog = {
    "🦙 LLaMA 3.3 70B (Versatile)": "llama-3.3-70b-versatile",
    "🦙 LLaMA 3 8B": "llama3-8b-8192",
    "🌠 Qwen QWQ 32B": "qwen-qwq-32b",
    "💡 DeepSeek (LLaMA 70B Distilled)": "deepseek-r1-distill-llama-70b"
}

with st.sidebar:
    st.header("⚙️ Settings")
    friendly_model = st.selectbox("Choose a model:", list(model_catalog.keys()))
    model = model_catalog[friendly_model]
    st.caption(f"Model ID: `{model}`")

    temperature = st.slider("🎲 Temperature", 0.0, 1.5, 0.7, 0.05)
    top_p = st.slider("📊 Top-p", 0.0, 1.0, 1.0, 0.05)
    max_tokens = st.slider("🧠 Max Tokens", 256, 8192, 1024, 64)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Krishna, the divine charioteer and teacher from the Bhagavad Gita. "
                "Answer all questions with spiritual insight, calm tone, and references to Gita's teachings. "
                "Offer philosophical wisdom, quotes (if relevant), and practical advice inspired by the Gita."
            )
        }
    ]

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your question to GitaGPT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": st.session_state.messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": True
    }

    assistant_response = ""
    with st.chat_message("assistant"):
        response_container = st.empty()
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True
        )

        for line in response.iter_lines():
            if line:
                if line.startswith(b"data: "):
                    line = line[6:]
                if line == b"[DONE]":
                    break
                try:
                    data = json.loads(line.decode("utf-8"))
                    delta = data["choices"][0]["delta"].get("content", "")
                    assistant_response += delta
                    response_container.markdown(assistant_response + "▌")
                except Exception:
                    continue
        response_container.markdown(assistant_response)

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
