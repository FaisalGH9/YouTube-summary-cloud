# 🎮 Watch Less, Learn More — Multimodal AI Chatbot for YouTube Video QA

## 📌 Overview

**Watch Less, Learn More** is an advanced multimodal AI-powered web application that transforms YouTube videos into structured, searchable, and interactive knowledge. Designed with educators, researchers, and curious learners in mind, the system leverages state-of-the-art AI to transcribe, summarize, and answer questions about videos — all through a smart and intuitive interface.

✅ Built with **LangChain**, **OpenAI**, **Whisper**, **FAISS/ChromaDB**, and **LangSmith**
✅ Designed for **text, audio, and multilingual interaction**
✅ Evaluated with **LangSmith Tracing Dashboard** for performance, latency, and error analysis

---

## 🎯 Project Objectives

* Convert **YouTube video/audio** into text using speech-to-text (Whisper)
* Generate **structured summaries** with Table of Contents using OpenAI APIs
* Provide **real-time Q\&A interaction** via a chatbot powered by LangChain Agents
* Allow **multilingual translation** of summaries and transcripts
* Enable **comprehension quizzes** to evaluate user understanding
* Track performance and trace responses using **LangSmith**

---

## 🧠 Features

| Feature                 | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| 🎤 Speech Recognition   | Transcribe videos using Whisper (for accuracy over auto-captioning) |
| 🧞 Summary Generator    | 3-tier summaries (Detailed, Medium, Short) with Table of Contents   |
| 🤖 Chatbot (Q\&A)       | LangChain agent answers questions based on transcript context       |
| 🌍 Multilingual Support | Translate summaries/transcripts to Arabic, French, German, Spanish  |
| 🧪 LangSmith Evaluation | Monitor errors, latency, and feedback for continuous improvements   |
| 📚 Comprehension Quiz   | Auto-generated quiz to test user knowledge                          |
| 📅 Export Options       | Download summaries as PDF or TXT                                    |
| 🔗 Social Sharing       | Share summaries directly on LinkedIn, WhatsApp, or X                |

---

## 🧱 Tech Stack

| Category             | Tool/Library                      |
| -------------------- | --------------------------------- |
| 🧠 LLM               | OpenAI GPT-4 / GPT-3.5 Turbo      |
| 🗣️ Speech-to-Text   | OpenAI Whisper                    |
| 🔗 Framework         | LangChain (Agents, Tools, Chains) |
| 🔍 Vector DB         | ChromaDB or FAISS                 |
| 📦 Deployment        | Streamlit                         |
| 📊 Evaluation        | LangSmith                         |
| 🧪 Environment Mgmt  | Python 3.10, .env via dotenv      |
| 📚 Document Handling | FPDF, BeautifulSoup               |
| 🎥 Video Processing  | moviepy, yt\_dlp                  |

---

## 🚀 Project Structure

```
📁 my_project/
├── app.py               # Main Streamlit application
├── qa_agent.py          # LangChain Agent and QA logic
├── transcriber.py       # Whisper transcription handler
├── summarizer.py        # Summary generation with TOC
├── vector_store.py      # Chunking & vector DB storage
├── utils.py             # Helper functions (e.g., video ID extraction)
├── requirements.txt     # Dependencies list
├── .env                 # API keys and environment variables
├── README.md            # This file
└── 📁 downloads/uploads  # Uploaded/downloaded content
```

---

## 🛠️ Setup & Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set your environment variables**

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key
LANGCHAIN_API_KEY=your_langsmith_key
```

5. **Run the app**

```bash
streamlit run app.py
```

---

## ✅ Evaluation with LangSmith

LangSmith was integrated to trace agent behavior and evaluate:

| Metric        | Description                              |
| ------------- | ---------------------------------------- |
| 🧠 Accuracy   | Ensuring context-aware answers           |
| 🔁 Error Rate | Logged and traced failed agent responses |
| 🕓 Latency    | P50 and P99 latency recorded             |
| 🧪 Feedback   | Each run is traceable and debuggable     |

Access your dashboard: [LangSmith Traces](https://smith.langchain.com)

---

## 📦 Deployment Options

This app can be deployed using:

* ✅ Local Streamlit Deployment *(Recommended for demo)*
* ☁️ Cloud:

  * Streamlit Cloud
  * HuggingFace Spaces *(via Gradio wrapper)*
  * Docker *(via `Dockerfile`)*

---

## 📚 Future Improvements

* 🎤 Voice-in/voice-out conversational support
* 📷 Integration of thumbnails and visual grounding
* ⚕️ Domain-specific QA modules (e.g., healthcare, legal)
* 🔍 Use Pinecone for production-grade vector search
* 🧠 Fine-tuning summarization and QA for domain accuracy

---

## 🧪 Testing & Evaluation Plan

* ✅ Baseline QA and improved context retrieval
* ✅ Hallucination detection via LangSmith traces
* ✅ Human-AI translation quality comparison
* ✅ Latency and error tracking
* ✅ Memory usage profiling

---

> Developed by **Alhanoof Aljamaan** — Powered by OpenAI & LangChain


<!-- google drive video  -->
https://drive.google.com/drive/folders/1d-rrbEN6Yv4q7FJtcbKPeo73U6QdIZvo

<!-- presintion  -->
https://www.canva.com/design/DAGmpo-A99o/jLlnVNfaG3VJ7FRUDXU3wQ/edit?utm_content=DAGmpo-A99o&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton