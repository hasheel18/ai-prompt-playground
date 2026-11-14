
import os
import time
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

def get_config_value(key, default=None):
    """
    Read configuration from environment variables
    or Streamlit Cloud secrets.
    """

    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets.get(key, default)
    except (FileNotFoundError, KeyError):
        return default

GEMINI_API_KEY = get_config_value("GEMINI_API_KEY")

GEMINI_MODEL = get_config_value(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

AVAILABLE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
]

if GEMINI_MODEL not in AVAILABLE_MODELS:
    AVAILABLE_MODELS.insert(0, GEMINI_MODEL)

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key not found. "
        "Please configure GEMINI_API_KEY in your "
        ".env file or Streamlit secrets."
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

if "response_time" not in st.session_state:
    st.session_state.response_time = 0.0

if "comparison_results" not in st.session_state:
    st.session_state.comparison_results = []

if "generation_mode" not in st.session_state:
    st.session_state.generation_mode = "Single Model"

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

def generate_ai_response(prompt, technique, temperature, model):
    """
    Generate a response using the selected Gemini model.

    Returns:
        response_text
        token_usage dictionary
        response_time in seconds
    """

    final_prompt = build_prompt(prompt, technique)

    start_time = time.perf_counter()

    interaction = client.interactions.create(
        model=model,
        input=final_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": 4096
        }
    )

    response_time = time.perf_counter() - start_time

    if interaction.status != "completed":
        raise RuntimeError(
        f"Gemini interaction did not complete. "
        f"Status: {interaction.status}. "
        f"Details: {getattr(interaction, 'error', None)}"
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
    return response_text, token_usage, response_time

# ==========================================
# 6. WORKSPACE HELPER FUNCTIONS
# ==========================================

def clear_workspace():
    """
    Clear the current workspace while
    preserving experiment history.
    """

    st.session_state.prompt_input = ""
    st.session_state.response = ""
    st.session_state.last_technique = ""
    st.session_state.last_model = ""
    st.session_state.response_time = 0.0
    st.session_state.comparison_results = []

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

    generation_mode = st.radio(
        "Generation Mode",
        ["Single Model", "Compare Models"],
        key="generation_mode"
    )

    if generation_mode == "Single Model":

        model = st.selectbox(
            "AI Model",
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(GEMINI_MODEL)
        )

        comparison_models = []

    else:

        model = None

        comparison_models = st.multiselect(
            "Select Two Models",
            AVAILABLE_MODELS,
            default=AVAILABLE_MODELS[:2],
            max_selections=2
        )

        st.caption(
            "Compare two models using the same "
            "prompt, technique, and temperature."
        )

    # Available in BOTH generation modes
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

    st.caption("PromptLab v0.4")

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

    elif (
        generation_mode == "Compare Models"
        and len(comparison_models) != 2
    ):
        st.warning("Please select exactly two models.")

    else:

        try:

            if generation_mode == "Single Model":

                with st.spinner(
                    f"{model} is generating your response..."
                ):

                    response, token_usage, response_time = (
                        generate_ai_response(
                            prompt,
                            technique,
                            temperature,
                            model
                        )
                    )

                st.session_state.response = response
                st.session_state.last_technique = technique
                st.session_state.last_model = model
                st.session_state.token_usage = token_usage
                st.session_state.response_time = response_time
                st.session_state.comparison_results = []

                st.session_state.history.append({
                    "mode": "Single Model",
                    "prompt": prompt,
                    "technique": technique,
                    "response": response,
                    "temperature": temperature,
                    "model": model,
                    "response_time": response_time,
                    "time": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "token_usage": token_usage
                })

            else:

                results = []

                # Reset previous results before comparison
                st.session_state.response = ""
                st.session_state.comparison_results = []

                for selected_model in comparison_models:

                    with st.spinner(
                        f"Generating with {selected_model}..."
                    ):

                        try:

                            response, usage, elapsed = (
                                generate_ai_response(
                                    prompt,
                                    technique,
                                    temperature,
                                    selected_model
                                )
                            )

                            results.append({
                                "model": selected_model,
                                "response": response,
                                "token_usage": usage,
                                "response_time": elapsed,
                                "error": None
                            })

                        except Exception as model_error:

                            results.append({
                                "model": selected_model,
                                "response": "",
                                "token_usage": None,
                                "response_time": None,
                                "error": str(model_error)
                            })

                st.session_state.comparison_results = results

                st.session_state.history.append({
                    "mode": "Compare Models",
                    "prompt": prompt,
                    "technique": technique,
                    "temperature": temperature,
                    "time": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "results": results
                })

        except errors.ClientError as error:

            if error.code == 429:
                st.error(
                    "Gemini's request limit has been reached."
                )

            elif error.code in (400, 404):
                st.error(
                    "Gemini rejected the request. "
                    "Check your model ID and prompt."
                )

            else:
                st.error("Gemini API request failed.")

            st.caption(str(error))

        except errors.ServerError as error:

            if error.code in (503, 504):
                st.error(
                    "Gemini is busy or taking too long. "
                    "Please try again later."
                )

            else:
                st.error("Gemini experienced a server error.")

            st.caption(str(error))

        except Exception as error:

            st.error("Failed to generate an AI response.")
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

        st.metric(
            "Response Time",
            f"{st.session_state.response_time:.2f} seconds"
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
# MODEL COMPARISON WORKSPACE
# ==========================================

if st.session_state.comparison_results:

    st.write("")

    st.markdown(
        '<div class="section-heading">'
        '⚖️ AI Model Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Compare AI responses, generation times, "
        "and token usage side by side."
    )

    results = st.session_state.comparison_results

    columns = st.columns(2)

    for column, result in zip(columns, results):

        with column:

            with st.container(border=True):

                st.subheader(result["model"])

                if result["error"]:

                    st.error("Model request failed.")
                    st.caption(result["error"])

                else:

                    st.success("Response generated!")

                    st.markdown(result["response"])

                    st.divider()

                    st.metric(
                        "Response Time",
                        f"{result['response_time']:.2f} s"
                    )

                    usage = result["token_usage"]

                    metric1, metric2 = st.columns(2)

                    with metric1:

                        st.metric(
                            "Input Tokens",
                            usage["input_tokens"]
                        )

                        st.metric(
                            "Thinking Tokens",
                            usage["thinking_tokens"]
                        )

                    with metric2:

                        st.metric(
                            "Output Tokens",
                            usage["output_tokens"]
                        )

                        st.metric(
                            "Total Tokens",
                            usage["total_tokens"]
                        )

                    st.download_button(
                        "⬇️ Download Response",
                        data=result["response"],
                        file_name=(
                            f"{result['model']}_response.md"
                        ),
                        mime="text/markdown",
                        key=f"download_{result['model']}"
                    )

    # Performance comparison table

    st.subheader("📊 Performance Comparison")

    comparison_data = []

    for result in results:

        if result["error"]:
            continue

        usage = result["token_usage"]

        comparison_data.append({
            "Model": result["model"],
            "Response Time (s)": round(
                result["response_time"], 2
            ),
            "Input Tokens": usage["input_tokens"],
            "Output Tokens": usage["output_tokens"],
            "Thinking Tokens": usage["thinking_tokens"],
            "Total Tokens": usage["total_tokens"]
        })

    if comparison_data:

        st.dataframe(
            comparison_data,
            use_container_width=True,
            hide_index=True
        )

    if len(comparison_data) == 2:

        first, second = comparison_data

        if (
            first["Response Time (s)"]
            < second["Response Time (s)"]
        ):
            faster_model = first["Model"]

        elif (
            second["Response Time (s)"]
            < first["Response Time (s)"]
        ):
            faster_model = second["Model"]

        else:
            faster_model = "Both models were equally fast"

        st.info(
            f"⚡ Faster in this test: {faster_model}"
        )

    st.caption(
        "Results reflect individual API requests. "
        "Network conditions, server load, and output "
        "length can affect response times."
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
    "Review experiments completed during this session."
)

if st.session_state.history:

    total = len(st.session_state.history)

    for index, item in enumerate(
        reversed(st.session_state.history)
    ):

        experiment_number = total - index

        mode = item.get("mode", "Single Model")

        title = (
            f"Experiment {experiment_number} | "
            f"{mode} | "
            f"{item['time']}"
        )

        with st.expander(title):

            st.markdown("**Prompt**")
            st.write(item["prompt"])

            st.markdown("**Technique**")
            st.write(item["technique"])

            st.markdown("**Temperature**")
            st.write(item["temperature"])

            if mode == "Single Model":

                st.markdown("**Model**")
                st.write(item.get("model", GEMINI_MODEL))

                st.markdown("**AI Response**")
                st.markdown(item["response"])

                response_time = item.get("response_time")

                if response_time is not None:

                    st.write(
                        f"Response Time: "
                        f"{response_time:.2f} seconds"
                    )

                usage = item.get("token_usage")

                if usage:

                    st.markdown("**Token Usage**")

                    st.write(
                        f"Input: {usage.get('input_tokens', 0)} | "
                        f"Output: {usage.get('output_tokens', 0)} | "
                        f"Thinking: {usage.get('thinking_tokens', 0)} | "
                        f"Total: {usage.get('total_tokens', 0)}"
                    )

            else:

                for result in item.get("results", []):

                    st.markdown(
                        f"### {result['model']}"
                    )

                    if result["error"]:

                        st.error(result["error"])

                    else:

                        st.markdown(result["response"])

                        st.write(
                            "Response Time: "
                            f"{result['response_time']:.2f} seconds"
                        )

                        usage = result["token_usage"]

                        st.write(
                            f"Input: {usage['input_tokens']} | "
                            f"Output: {usage['output_tokens']} | "
                            f"Thinking: {usage['thinking_tokens']} | "
                            f"Total: {usage['total_tokens']}"
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
| PromptLab v0.4
| AI Prompt Engineering Project
</div>
""", unsafe_allow_html=True)