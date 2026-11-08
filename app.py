
import streamlit as st
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="PromptLab | AI Playground",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

if "response" not in st.session_state:
    st.session_state.response = ""

if "last_technique" not in st.session_state:
    st.session_state.last_technique = ""

if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""

# ==========================================
# 3. THEME-AWARE CSS
# ==========================================

st.markdown("""
<style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: var(
            --secondary-background-color,
            transparent
        );
        border: 1px solid var(
            --border-color,
            rgba(128,128,128,0.2)
        );
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 24px;
    }

    .eyebrow {
        color: var(--primary-color, #6366F1);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .hero-title {
        color: var(--text-color, inherit);
        font-size: 2.2rem;
        font-weight: 750;
        margin-bottom: 10px;
    }

    .hero-description {
        color: var(--text-color, inherit);
        opacity: 0.75;
        font-size: 15px;
        line-height: 1.7;
    }

    .section-heading {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 8px;
    }

    div[data-testid="stMetric"] {
        background: var(
            --secondary-background-color,
            transparent
        );
        border: 1px solid var(
            --border-color,
            rgba(128,128,128,0.2)
        );
        border-radius: 14px;
        padding: 18px;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 600;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 12px;
        font-size: 15px;
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        opacity: 0.65;
        font-size: 13px;
        padding-top: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

def build_demo_response(prompt, technique):
    """
    Create a demonstration explaining
    how the selected technique works.

    No AI API is called.
    """

    if technique == "Zero-shot":
        return (
            "### Zero-shot Prompting\n\n"
            "The AI receives your instruction "
            "without any examples.\n\n"
            f"**Your prompt:** {prompt}"
        )

    elif technique == "Few-shot":
        return (
            "### Few-shot Prompting\n\n"
            "The AI receives examples showing "
            "how to complete the task.\n\n"
            f"**Your prompt:** {prompt}"
        )

    else:
        return (
            "### Role-based Prompting\n\n"
            "The AI receives a role instruction "
            "such as 'You are a programming tutor'.\n\n"
            f"**Your prompt:** {prompt}"
        )


def clear_workspace():
    """
    Clear the prompt editor and response.

    Experiment history is preserved.
    """
    st.session_state.prompt_input = ""
    st.session_state.response = ""
    st.session_state.last_technique = ""


def load_example():
    """
    Load the selected example into
    the prompt editor.
    """
    selected = st.session_state.example_choice
    st.session_state.prompt_input = examples[selected]


def clear_history():
    """
    Remove all saved experiments
    from the current session.
    """
    st.session_state.history = []


# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🧠 PromptLab")
    st.caption("AI Prompt Engineering Playground")

    st.divider()

    st.subheader("⚙️ Configuration")

    technique = st.selectbox(
        "Prompt Technique",
        [
            "Zero-shot",
            "Few-shot",
            "Role-based"
        ]
    )

    model = st.selectbox(
        "AI Model",
        ["Demo Mode"]
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    st.caption(
        "Temperature will become active "
        "when we integrate an AI model."
    )

    st.divider()

    st.subheader("📚 Learn Prompting")

    with st.expander("Zero-shot"):
        st.write(
            "Give the AI a task without examples."
        )

    with st.expander("Few-shot"):
        st.write(
            "Provide examples of the expected "
            "input and output."
        )

    with st.expander("Role-based"):
        st.write(
            "Give the AI a role, such as a "
            "teacher or software engineer."
        )

    st.divider()

    st.caption(
        "🎨 Change the theme using "
        "Streamlit's top-right menu."
    )

    st.caption("PromptLab v0.2")


# ==========================================
# 6. HERO SECTION
# ==========================================

st.markdown(
    """
<div class="hero">
<div class="eyebrow">AI ENGINEERING WORKSPACE</div>
<div class="hero-title">🧠 AI Prompt Playground</div>
<div class="hero-description">
Design, test, and improve your prompts.
Explore different prompting techniques
in one interactive workspace.
</div>
</div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 7. DASHBOARD METRICS
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Experiments",
        len(st.session_state.history)
    )

with col2:
    st.metric(
        "Active Technique",
        technique
    )

with col3:
    st.metric(
        "Model Status",
        "Demo Mode"
    )

st.write("")

# ==========================================
# 8. MAIN WORKSPACE
# ==========================================

st.markdown(
    '<div class="section-heading">'
    '✍️ Prompt Workspace'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Write your own prompt or load "
    "an example to experiment."
)

examples = {
    "Custom Prompt": "",

    "Explain an API": (
        "Explain what an API is using "
        "a simple real-world example."
    ),

    "Machine Learning": (
        "Explain machine learning to a "
        "beginner with three examples."
    ),

    "Python Functions": (
        "Explain Python functions with "
        "a simple code example."
    )
}

with st.container(border=True):

    example = st.selectbox(
        "Example Prompts",
        list(examples.keys()),
        key="example_choice"
    )

    st.button(
        "📋 Load Example",
        on_click=load_example
    )

    prompt = st.text_area(
        "Your Prompt",
        placeholder="Type your instructions here...",
        height=180,
        key="prompt_input"
    )

    st.caption(
        f"Characters: {len(prompt)} | "
        f"Technique: {technique}"
    )

    col_generate, col_clear = st.columns([3, 1])

    with col_generate:
        generate = st.button(
            "✨ Generate Response",
            type="primary",
            use_container_width=True
        )

    with col_clear:
        st.button(
            "🗑️ Clear Workspace",
            use_container_width=True,
            on_click=clear_workspace
        )

# ==========================================
# 9. RESPONSE GENERATION
# ==========================================

if generate:

    if not prompt.strip():
        st.warning("Please enter a prompt.")

    else:
        response = build_demo_response(
            prompt,
            technique
        )

        st.session_state.response = response
        st.session_state.last_technique = technique

        experiment = {
            "prompt": prompt,
            "technique": technique,
            "response": response,
            "temperature": temperature,
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        st.session_state.history.append(
            experiment
        )

# ==========================================
# 10. RESPONSE WORKSPACE
# ==========================================

st.write("")

st.markdown(
    '<div class="section-heading">'
    '🤖 Response Workspace'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    if st.session_state.response:

        st.success(
            "Demonstration generated successfully."
        )

        st.caption(
            "Demo Mode: No real AI model was called."
        )

        st.markdown(
            st.session_state.response
        )

        st.divider()

        st.caption(
            "Technique used: "
            + st.session_state.last_technique
        )

        st.download_button(
            "⬇️ Download Response",
            data=st.session_state.response,
            file_name="prompt_response.md",
            mime="text/markdown"
        )

    else:
        st.info(
            "Your response will appear here "
            "after generating a prompt."
        )

# ==========================================
# 11. EXPERIMENT HISTORY
# ==========================================

st.write("")

st.markdown(
    '<div class="section-heading">'
    '🕘 Experiment History'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Review the experiments completed "
    "during this session."
)

if st.session_state.history:

    total = len(st.session_state.history)

    for index, item in enumerate(
        reversed(st.session_state.history)
    ):

        experiment_number = total - index

        title = (
            f"Experiment {experiment_number} | "
            f"{item['technique']} | "
            f"{item['time']}"
        )

        with st.expander(title):

            st.markdown("**Prompt**")
            st.write(item["prompt"])

            st.markdown("**Technique**")
            st.write(item["technique"])

            st.markdown("**Temperature**")
            st.write(item["temperature"])

            st.markdown("**Demo Response**")
            st.markdown(item["response"])

    st.button(
        "🗑️ Clear History",
        on_click=clear_history
    )

else:

    with st.container(border=True):
        st.caption(
            "No experiments yet. "
            "Your history will appear here."
        )

# ==========================================
# 12. FOOTER
# ==========================================

st.divider()

st.markdown("""
<div class="footer">
Developed by Dhanusha Hasheel
| PromptLab v0.2
| AI Prompt Engineering Project
</div>
""", unsafe_allow_html=True)