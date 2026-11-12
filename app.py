
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors


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
# 2. GEMINI API CONFIGURATION
# ==========================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key not found. "
        "Please check your .env file."
    )
    st.stop()


@st.cache_resource
def create_gemini_client(api_key):
    """
    Create and reuse the Gemini client.

    Timeout is in milliseconds.
    Automatic SDK retries are disabled.
    """

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=240000,
            retry_options=types.HttpRetryOptions(
                attempts=1
            )
        )
    )


client = create_gemini_client(GEMINI_API_KEY)


# ==========================================
# 3. SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

if "response" not in st.session_state:
    st.session_state.response = ""

if "last_technique" not in st.session_state:
    st.session_state.last_technique = ""

if "last_model" not in st.session_state:
    st.session_state.last_model = ""

if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""

if "token_usage" not in st.session_state:
    st.session_state.token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "thinking_tokens": 0,
        "total_tokens": 0
    }


# ==========================================
# 4. THEME-AWARE CSS
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
# 5. PROMPT ENGINEERING FUNCTIONS
# ==========================================

def build_prompt(prompt, technique):
    """
    Construct a prompt based on the
    selected prompting technique.
    """

    if technique == "Zero-shot":
        return prompt

    elif technique == "Few-shot":
        return f"""
You are a helpful AI assistant.

Here are examples of how to respond.

Example 1:
User: Explain what an API is.
Assistant: An API allows two software
applications to communicate with each other.

Example 2:
User: Explain what a database is.
Assistant: A database is an organized
collection of information.

Now respond to the following request
using a similarly clear, beginner-friendly style.

User: {prompt}
Assistant:
"""

    elif technique == "Role-based":
        return f"""
You are an experienced software engineering
instructor who explains technical concepts
clearly to beginners.

Provide accurate explanations, useful
examples, and well-organized answers.

User request:
{prompt}
"""

    return prompt


def generate_ai_response(prompt, technique, temperature):
    """
    Generate a response using the
    Gemini Interactions API.

    Returns:
        response_text
        token_usage dictionary
    """

    final_prompt = build_prompt(
        prompt,
        technique
    )

    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input=final_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": 1024
        }
    )

    if interaction.status != "completed":
        raise RuntimeError(
            "Gemini interaction did not complete. "
            f"Status: {interaction.status}"
        )

    response_text = interaction.output_text

    if not response_text:
        raise ValueError(
            "Gemini returned an empty response. "
            "Please try another prompt."
        )

    usage = interaction.usage

    token_usage = {
        "input_tokens": (
            getattr(usage, "total_input_tokens", 0) or 0
        ),
        "output_tokens": (
            getattr(usage, "total_output_tokens", 0) or 0
        ),
        "thinking_tokens": (
            getattr(usage, "total_thought_tokens", 0) or 0
        ),
        "total_tokens": (
            getattr(usage, "total_tokens", 0) or 0
        )
    }

    return response_text, token_usage


# ==========================================
# 6. WORKSPACE HELPER FUNCTIONS
# ==========================================

def clear_workspace():
    """
    Clear the current prompt, response,
    and token usage.

    Experiment history is preserved.
    """

    st.session_state.prompt_input = ""
    st.session_state.response = ""
    st.session_state.last_technique = ""
    st.session_state.last_model = ""

    st.session_state.token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "thinking_tokens": 0,
        "total_tokens": 0
    }


def load_example():
    """
    Load the selected example prompt.
    """

    selected = st.session_state.example_choice

    st.session_state.prompt_input = examples[selected]


def clear_history():
    """
    Clear saved experiments from
    the current Streamlit session.
    """

    st.session_state.history = []


# ==========================================
# 7. SIDEBAR
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
        [GEMINI_MODEL]
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    st.caption(
        "Lower temperature gives more "
        "consistent responses. Higher "
        "temperature allows more variation."
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

    st.caption("PromptLab v0.3")


# ==========================================
# 8. HERO SECTION
# ==========================================

st.markdown(
    """
<div class="hero">
<div class="eyebrow">AI ENGINEERING WORKSPACE</div>
<div class="hero-title">🧠 AI Prompt Playground</div>
<div class="hero-description">
Design, test, and improve your prompts.
Explore different prompting techniques
using real AI-generated responses.
</div>
</div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 9. DASHBOARD METRICS
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
        "Gemini API"
    )

st.write("")


# ==========================================
# 10. MAIN WORKSPACE
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
# 11. RESPONSE GENERATION
# ==========================================

if generate:

    if not prompt.strip():
        st.warning("Please enter a prompt.")

    else:
        try:

            with st.spinner(
                "Gemini is generating your response..."
            ):

                response, token_usage = generate_ai_response(
                    prompt,
                    technique,
                    temperature
                )

            # Save response to session state
            st.session_state.response = response
            st.session_state.last_technique = technique
            st.session_state.last_model = GEMINI_MODEL

            # Save token usage
            st.session_state.token_usage = token_usage

            # Save experiment
            experiment = {
                "prompt": prompt,
                "technique": technique,
                "response": response,
                "temperature": temperature,
                "model": GEMINI_MODEL,
                "time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "token_usage": token_usage
            }

            st.session_state.history.append(
                experiment
            )

        except errors.ClientError as error:

            if error.code == 429:
                st.error(
                    "Gemini's request limit has been "
                    "reached. Please wait and try again."
                )

            elif error.code in (400, 404):
                st.error(
                    "Gemini rejected the request. "
                    "Check your model ID and prompt."
                )

            else:
                st.error(
                    "Gemini API request failed."
                )

            st.caption(str(error))

        except errors.ServerError as error:

            if error.code in (503, 504):
                st.error(
                    "Gemini is currently busy or "
                    "taking too long to respond. "
                    "Please try again later."
                )

            else:
                st.error(
                    "Gemini experienced a server error."
                )

            st.caption(str(error))

        except Exception as error:

            st.error(
                "Failed to generate an AI response."
            )

            st.caption(str(error))


# ==========================================
# 12. RESPONSE WORKSPACE
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
            "AI response generated successfully!"
        )

        st.caption(
            "Generated using "
            + st.session_state.last_model
        )

        # Display the generated response
        st.markdown(
            st.session_state.response
        )

        st.divider()

        st.subheader("📊 Token Usage")

        usage = st.session_state.token_usage

        token_col1, token_col2, token_col3, token_col4 = (
            st.columns(4)
        )

        with token_col1:
            st.metric(
                "Input Tokens",
                usage["input_tokens"]
            )

        with token_col2:
            st.metric(
                "Output Tokens",
                usage["output_tokens"]
            )

        with token_col3:
            st.metric(
                "Thinking Tokens",
                usage["thinking_tokens"]
            )

        with token_col4:
            st.metric(
                "Total Tokens",
                usage["total_tokens"]
            )

        st.caption(
            "Total tokens may include thinking "
            "tokens used internally by Gemini."
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
# 13. EXPERIMENT HISTORY
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

            st.markdown("**Model**")
            st.write(
                item.get("model", GEMINI_MODEL)
            )

            st.markdown("**Temperature**")
            st.write(item["temperature"])

            st.markdown("**AI Response**")
            st.markdown(item["response"])

            st.markdown("**Token Usage**")

            usage = item.get("token_usage")

            if usage:
                st.write(
                    f"Input: {usage.get('input_tokens', 0)} | "
                    f"Output: {usage.get('output_tokens', 0)} | "
                    f"Thinking: {usage.get('thinking_tokens', 0)} | "
                    f"Total: {usage.get('total_tokens', 0)}"
                )
            else:
                st.caption(
                    "Token usage was not recorded "
                    "for this experiment."
                )

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
# 14. FOOTER
# ==========================================

st.divider()

st.markdown("""
<div class="footer">
Developed by Dhanusha Hasheel
| PromptLab v0.3
| AI Prompt Engineering Project
</div>
""", unsafe_allow_html=True)