
import streamlit as st

st.set_page_config(
    page_title="AI Prompt Playground",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Prompt Playground")
st.write("Experiment with different prompt techniques.")

technique = st.selectbox(
    "Choose a prompt technique",
    ["Zero-shot", "Few-shot", "Role-based"]
)

prompt = st.text_area(
    "Enter your prompt",
    placeholder="Explain what an API is...",
    height=150
)

if st.button("Generate Response"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        st.success("Prompt received!")
        st.write("**Selected technique:**", technique)
        st.write("**Your prompt:**", prompt)
        st.info("AI integration will be added next.")
