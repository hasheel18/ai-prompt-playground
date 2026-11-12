
# 🧠 PromptLab — AI Prompt Playground

An interactive AI prompt engineering playground built using **Python, Streamlit, and Google's Gemini API**.

## About the Project

PromptLab is a beginner-friendly application designed to explore different AI prompting techniques through an interactive interface.

The application allows users to experiment with prompts, generate real AI responses, adjust model settings, and analyze token usage.

This project is being developed step by step as part of my AI engineering learning journey.

## Features

- Modern Streamlit interface
- Light and Dark theme support
- Zero-shot prompting
- Few-shot prompting
- Role-based prompting
- Real AI response generation using Google Gemini
- Temperature adjustment
- Example prompt templates
- Input, output, thinking, and total token tracking
- Experiment history
- Download AI-generated responses
- Clear workspace functionality
- Gemini API error handling

## Technologies Used

- **Python** — Application logic
- **Streamlit** — Interactive web interface
- **Google Gemini API** — AI response generation
- **Google GenAI SDK** — Gemini Interactions API integration
- **Python-dotenv** — Environment variable management
- **HTML and CSS** — Interface customization
- **Git and GitHub** — Version control

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hasheel8/ai-prompt-playground.git
```

### 2. Navigate to the Project

```bash
cd ai-prompt-playground
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Environment (Windows PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Configure the Gemini API

Create a `.env` file in the project directory and add:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

You can obtain your API key from [Google AI Studio](https://aistudio.google.com/).

> **Important:** Keep your `.env` file private. Never commit your Gemini API key to GitHub.

### 7. Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## How It Works

1. Enter a custom prompt or select an example.
2. Choose a prompting technique.
3. Adjust the temperature setting.
4. Click **Generate Response**.
5. Gemini generates a real AI response.
6. View the response and token usage.
7. Review previous experiments in the Experiment History section.

## Important Note

PromptLab generates **real AI responses** using Google's Gemini API.

The application currently uses **Gemini 3.5 Flash Lite** as its default model.

An active internet connection and a valid Gemini API key are required.

Experiment history is stored in the current Streamlit session and is not permanently saved.

## Developer

**Dhanusha Hasheel**

GitHub: [hasheel8](https://github.com/hasheel8)

---

*Built as part of my AI engineering learning journey.*
