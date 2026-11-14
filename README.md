
# 🧠 PromptLab — AI Prompt Playground

An interactive AI prompt engineering playground built with **Python, Streamlit, and Google's Gemini API**.

Experiment with prompting techniques, compare AI models, and analyze their responses and performance.

## 🚀 About the Project

PromptLab is an interactive application designed to explore how different prompting techniques and AI models affect generated responses.

Users can create prompts, experiment with model settings, compare AI-generated outputs, and analyze response times and token usage through a beginner-friendly interface.

This project was developed as part of my AI engineering learning journey, with a focus on understanding prompt engineering, AI model integration, and performance evaluation.

## ✨ Features

### 🧠 Prompt Engineering
- Zero-shot prompting
- Few-shot prompting
- Role-based prompting
- Custom prompts and example templates
- Adjustable temperature settings

### 🤖 AI Model Integration
- Real AI response generation using Google's Gemini API
- Single Model generation mode
- Support for multiple Gemini models
- Gemini 3.5 Flash Lite and Gemini 3.5 Flash
- Gemini API error handling

### ⚖️ AI Model Comparison
- Compare two AI models using the same prompt
- Side-by-side AI-generated responses
- Response time measurement
- Input token tracking
- Output token tracking
- Thinking token tracking
- Total token tracking
- Performance comparison table

### 🎨 User Interface
- Modern Streamlit interface
- Light and dark theme support
- Interactive configuration sidebar
- Download AI-generated responses
- Clear workspace functionality
- Session-based experiment history

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Application logic |
| Streamlit | Interactive web interface |
| Google Gemini API | AI response generation |
| Google GenAI SDK | Gemini Interactions API integration |
| Python-dotenv | Environment variable management |
| HTML & CSS | Interface customization |
| Git & GitHub | Version control |

## 🌐 Live Demo

**Coming Soon — Streamlit Community Cloud Deployment**

The application currently runs locally. A publicly accessible live demo will be added after deployment.

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hasheel18/ai-prompt-playground.git
```

### 2. Navigate to the Project

```bash
cd ai-prompt-playground
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Configure the Gemini API

Create a `.env` file in the project directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Get your API key from [Google AI Studio](https://aistudio.google.com/).

> **Important:** Never commit your `.env` file or expose your Gemini API key publicly.

### 7. Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

http://localhost:8501

## 💡 How It Works

### Single Model Mode

1. Enter a custom prompt or select an example.
2. Choose a prompting technique.
3. Select a Gemini model.
4. Adjust the temperature.
5. Click **Generate Response**.
6. View the AI-generated response, response time, and token usage.
7. Download the response or review it in Experiment History.

### Compare Models Mode

1. Select **Compare Models** in the sidebar.
2. Choose two Gemini models.
3. Enter a prompt and select a prompting technique.
4. Adjust the temperature setting.
5. Click **Generate Response**.
6. View both AI-generated responses side by side.
7. Compare response times and token usage in the performance table.
8. Review the comparison in Experiment History.

Both models receive the same constructed prompt and temperature setting, allowing users to explore differences in their responses and performance.

## 📊 Model Comparison

PromptLab supports comparing Gemini models using response time and token usage metrics.

For example:

| Metric | Gemini 3.5 Flash | Gemini 3.5 Flash Lite |
|--------|------------------|----------------------|
| Response Time | Measured in seconds | Measured in seconds |
| Input Tokens | Tracked | Tracked |
| Output Tokens | Tracked | Tracked |
| Thinking Tokens | Tracked | Tracked |
| Total Tokens | Tracked | Tracked |

Performance results vary depending on the prompt, model behavior, network conditions, and server availability.

Individual comparisons are experiments, not standardized model benchmarks.


## 🧩 Project Milestones

- [x] **Milestone 1 — Project Setup and Interface**
  - Streamlit application setup
  - Modern user interface
  - Prompt input workspace

- [x] **Milestone 2 — Prompt Engineering**
  - Zero-shot prompting
  - Few-shot prompting
  - Role-based prompting
  - Example prompt templates

- [x] **Milestone 3 — Gemini API Integration**
  - Real AI response generation
  - Temperature configuration
  - Token usage tracking
  - Experiment history
  - Response downloads

- [x] **Milestone 4 — AI Model Comparison**
  - Multiple Gemini model selection
  - Side-by-side response comparison
  - Response time tracking
  - Token usage comparison
  - Performance analysis
  

## 📌 Important Notes

- PromptLab generates **real AI responses** using Google's Gemini API.
- The default model is **Gemini 3.5 Flash Lite**.
- Model availability depends on Gemini API access and server conditions.
- An internet connection and a valid Gemini API key are required.
- Experiment history is stored only in the current Streamlit session.
- Model comparisons generate separate API requests and may consume additional API quota.
- Public deployment requires securely configured API credentials and appropriate usage limits.

## 👨‍💻 Developer

**Dhanusha Hasheel**

GitHub: [hasheel18](https://github.com/hasheel18)

Project Repository: [PromptLab — AI Prompt Playground](https://github.com/hasheel18/ai-prompt-playground)

---

*Built as part of my AI engineering learning journey.*
