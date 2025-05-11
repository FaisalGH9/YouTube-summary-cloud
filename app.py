# -------------------------- Importing Required Libraries -----------------------------
import os  # File system and environment variable management
import re  # Regular expressions for cleaning text (e.g., removing emojis)
import uuid  # Generate unique IDs (not used directly here)
import streamlit as st  # Streamlit library for web app UI
import urllib.parse  # Encode URL query parameters for sharing
from dotenv import load_dotenv  # Load environment variables from .env file
import yt_dlp  # Library for downloading YouTube videos
from bs4 import BeautifulSoup  # Clean HTML from summaries
from fpdf import FPDF  # Generate PDF files from text
from transcriber import transcribe_video  # Custom transcription function
from summarizer import summarize_text_with_toc_2000  # Summarization function with TOC
from splitter import split_text  # Utility to split transcript into smaller parts
from vector_store import store_chunks_persistent  # Store transcript chunks into vector DB
from langchain_openai import ChatOpenAI  # OpenAI interface for LangChain
from utils import extract_video_id  # Extracts video ID from YouTube URLs
from moviepy.video.io.VideoFileClip import VideoFileClip  # Retrieve video duration
import moviepy.editor as mp  # General video handling
from qa_agent import build_agent, set_transcript  # Custom Q&A agent tools
from langsmith import traceable  # Tool for tracing LangChain runs



# ---------------------- Environment Setup & OpenAI API Initialization -----------------------
os.environ["PATH"] += os.pathsep + r"C:\Users\HUAWEI\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"  # Add FFmpeg path to environment
load_dotenv()  # Load .env variables
openai_api_key = os.getenv("OPENAI_API_KEY")  # Fetch OpenAI API key

# ---------------------- Streamlit App Configuration -------------------------
st.set_page_config(page_title="🎮 Video Analyzer", layout="wide")  # Configure page title and layout
st.title("Skillify")  # App main title
st.markdown('<div style="font-size:16px; color:gray;">Summarize, translate, and interact with YouTube videos using AI</div>', unsafe_allow_html=True)



# ---------------------- Session State Initialization -------------------------
for key in ["video_path", "transcript", "summary", "raw_summary", "chat_history", "show_quiz", "keywords"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------------------- Emoji and Symbol Cleaning Function -------------------------
def clean_text_for_pdf(text):
    emoji_pattern = re.compile("["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]", flags=re.UNICODE)

    clean_text = emoji_pattern.sub(r'', text)

    symbol_replacements = {
        "📋": "[Table of Contents]",
        "✅": "[Done]",
        "🌍": "[Globe]",
        "📌": "[Pin]",
        "🌐": "[Translate]",
        "🔍": "[Search]",
        "📄": "[Document]",
        "📝": "[Notes]",
        "📁": "[Folder]",
        "💬": "[Chat]",
        "🔗": "[Link]",
        "⚠️": "[Warning]",
        "🔄": "[Refresh]",
        "🤖": "[Bot]",
        "🎮": "[Game]",
        "🎬": "[Film]",
        "📂": "[Folder]",
        "❌": "[Error]"
    }
    for symbol, replacement in symbol_replacements.items():
        clean_text = clean_text.replace(symbol, replacement)

    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    return clean_text

# ---------------------- Summary Cleaner: Removes Icons & Structure ----------------------
def extract_and_clean_summary(summary_html):
    soup = BeautifulSoup(summary_html, "html.parser")
    text = soup.get_text(separator="\n")
    lines = text.splitlines()
    cleaned_lines = []
    toc_mode = False

    for line in lines:
        if "📋" in line or "Table of Contents" in line:
            toc_mode = True
            continue
        if toc_mode:
            if line.strip().startswith("✅") or line.strip() == "":
                continue
            else:
                toc_mode = False
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

# ---------------------- YouTube Downloader using yt_dlp ----------------------
def download_youtube_video(url, output_path="downloads/"):
    os.makedirs(output_path, exist_ok=True)

    PROXY_URL = os.getenv("PROXY_URL")
    if not PROXY_URL:
        st.error("❌ Missing PROXY_URL environment variable.")
        return None

    
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'quiet': True,
        'ignoreerrors': True,
        'proxy': PROXY_URL
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return os.path.join(output_path, f"{info['id']}.mp4")
    except Exception as e:
        st.error(f"Failed to download video: {str(e)}")
        return None

# ---------------------- PDF Generator from Cleaned Text ----------------------
def create_pdf(text, filename):
    try:
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'Video Summary Report', 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()

        try:
            pdf.add_font('ArialUnicode', '', 'arial-unicode-ms.ttf', uni=True)
            pdf.set_font('ArialUnicode', '', 12)
        except:
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 12)

        clean_text = clean_text_for_pdf(text)
        pdf.multi_cell(0, 10, clean_text)
        pdf.output(filename)
        return True

    except Exception as e:
        st.error(f"Failed to create PDF: {str(e)}")
        return False

# ----------------------------------- Streamlit Tabs -----------------------------------
tab1, tab2, tab3 = st.tabs(["Upload & Summarize", "💬 Chatbot", "🔗 Share"])

# ---------------------------- Continue Tab Logic Below ----------------------------
# Tab 1: Upload or Paste YouTube Link
with tab1:
    st.markdown('<div style="font-size:20px; font-weight:600;"> Upload Video or Paste YouTube Link</div>', unsafe_allow_html=True)


    # User chooses input method
    method = st.radio("Choose Input Method", ["Upload File", "Paste YouTube Link"], horizontal=True)

    # If user uploads a file
    if method == "Upload File":
        file = st.file_uploader("Upload video/audio", type=["mp4", "mp3", "mkv", "webm", "m4a"])
        if file:
            try:
                os.makedirs("uploads", exist_ok=True)
                path = os.path.join("uploads", file.name)
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                st.session_state.video_path = path
                st.session_state.retriever = None
                st.session_state.qa_tool = None
                st.success("File uploaded successfully!")
            except Exception as e:
                st.error(f"Upload failed: {str(e)}")

    # If user pastes a YouTube link
    elif method == "Paste YouTube Link":
        url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
        if url:
            vid = extract_video_id(url)
            if vid:
                video_url = f"https://www.youtube.com/embed/{vid}"
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; padding: 20px;">
                        <div style="
                            border-radius: 16px;
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                            background-color: #1e1e1e;
                            max-width: 100%;
                            width: 800px;
                        ">
                            <iframe 
                                src="{video_url}" 
                                width="100%" 
                                height="450" 
                                style="border: none; border-radius: 12px;"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                allowfullscreen>
                            </iframe>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                with st.spinner("Downloading video..."):
                    path = download_youtube_video(url)
                    if path:
                        st.session_state.video_path = path
                        st.session_state.retriever = None
                        st.session_state.qa_tool = None
                        st.markdown('<div style="color: #28a745; font-size: 14px;"> Video downloaded successfully!</div>', unsafe_allow_html=True)

            else:
                st.error("❌ Invalid YouTube link. Please enter a valid URL.")

    # Transcribe video if not already done
    if st.session_state.video_path and st.session_state.transcript is None:
        with st.spinner("Transcribing video content..."):
            try:
                st.session_state.transcript = transcribe_video(st.session_state.video_path)
                st.markdown('<div style="color: #28a745; font-size: 14px;"> Transcription completed!</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Transcription failed: {str(e)}")

    # Display transcript and allow summarization
    if st.session_state.transcript:
        st.subheader("📝 Transcript")
        st.text_area("Transcript:", st.session_state.transcript, height=200)

        language = "Arabic"
        topic = st.selectbox("Summary Type", ["Detailed Summary", "Medium Summary", "Short Summary"])

        if st.button("🔍 Generate Summary", type="primary"):
            with st.spinner("Generating summary..."):
                try:
                    limited_text = st.session_state.transcript[:4000]
                    video_clip = mp.VideoFileClip(st.session_state.video_path)
                    duration_minutes = video_clip.duration / 60

                    summary_text = summarize_text_with_toc_2000(
                        text=limited_text,
                        api_key=openai_api_key,
                        language=language,
                        topic=topic,
                        video_duration_min=duration_minutes
                    )
                    st.session_state.summary = summary_text
                    st.session_state.raw_summary = extract_and_clean_summary(summary_text)
                    st.markdown('<div style="color: #28a745; font-size: 14px;">✅ Summary generated successfully!</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Summary generation failed: {str(e)}")

    # Display summary and allow download
    if st.session_state.summary:
        st.subheader("Summary")
        with st.expander("View Full Summary"):
            for line in st.session_state.raw_summary.splitlines():
                st.markdown(line)

        # Two-column layout for download buttons
        col1, col2 = st.columns(2)
        with col1:
            pdf_path = "video_summary.pdf"
            if st.button("📥 Generate PDF Summary"):
                with st.spinner("Creating PDF file..."):
                    if create_pdf(st.session_state.raw_summary, pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=f,
                                file_name=pdf_path,
                                mime="application/pdf",
                                key="pdf_download"
                            )
                    else:
                        st.error("Failed to generate PDF file")
        with col2:
            st.download_button(
                label="📝 Download Text Summary",
                data=st.session_state.raw_summary,
                file_name="video_summary.txt",
                mime="text/plain"
            )

        # Translation section
        st.subheader(" Translation")
        selected_lang = st.selectbox("Choose target language:", ["العربية", "French", "Spanish", "German"])
        translate_source = st.radio("Content to translate:", ["Summary", "Transcript"], horizontal=True)

        if st.button("🌐 Translate", type="primary"):
            with st.spinner("Translating content..."):
                try:
                    source_text = st.session_state.raw_summary if translate_source == "Summary" else st.session_state.transcript
                    paragraphs = [source_text[i:i+2000] for i in range(0, len(source_text), 2000)]
                    llm = ChatOpenAI(
                        temperature=0,
                        model="gpt-3.5-turbo",
                        openai_api_key=openai_api_key,
                        streaming=True
                    )

                    st.markdown(f'<div style="font-size:16px; font-weight:600;">📘 {selected_lang} Translation</div>', unsafe_allow_html=True)
                    translation_placeholder = st.empty()
                    streamed_translation = ""
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, para in enumerate(paragraphs):
                        status_text.text(f"Translating part {i+1}/{len(paragraphs)}...")
                        progress_bar.progress((i + 1) / len(paragraphs))

                        streamed_chunk = ""
                        prompt = (
                            f"Translate the following text to {selected_lang} "
                            f"while preserving all formatting and structure:\n\n{para}"
                        )

                        for chunk in llm.stream(prompt):
                            streamed_chunk += chunk.content or ""
                            translation_placeholder.markdown( streamed_translation + streamed_chunk
    )

                        streamed_translation += streamed_chunk + "\n\n"

                    status_text.markdown('<div style="color: #28a745; font-size: 14px;">✅ Translation completed!</div>', unsafe_allow_html=True)
                    progress_bar.empty()

                    st.download_button(
                        "📥 Download Translation",
                        streamed_translation.strip(),
                        file_name=f"translation_{selected_lang}.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Translation failed: {str(e)}")
# Tab 2: Interactive Chatbot
# Tab 2: Interactive Chatbot + Dynamic Quiz
with tab2:
    st.markdown('<div style="font-size:20px; font-weight:600;">💬 Chatbot</div>', unsafe_allow_html=True)


    # Check if transcript is available
    if not st.session_state.transcript:
        st.warning("🔄 Please upload and transcribe a video first.")
    else:
        # Set global transcript for the agent
        set_transcript(st.session_state.transcript)

        # Build the agent (QA model)
        agent = build_agent(openai_api_key)

        # Initialize chat history if not present
        if st.session_state.chat_history is None:
            st.session_state.chat_history = []

        chat_history = st.session_state.chat_history

        # Text input for user's question
        question = st.text_input("Ask your question about the video:")
        if question:
            with st.spinner("🤖 Thinking..."):
                try:
                    transcript = st.session_state.transcript
                    prompt = f"""
                    Answer the following question based ONLY on the transcript content.
                    Transcript:
                    {transcript[:2000]}

                    Question:
                    {question}

                    If the question is unrelated to the transcript, say: 'This question is outside the scope of the video.'
                    """
                    answer = agent.run(prompt)
                    chat_history.append(("User", question))
                    chat_history.append(("Agent", answer))
                    st.session_state.chat_history = chat_history
                except Exception as e:
                    chat_history.append(("Agent", f"❌ Agent error: {e}"))

        # Display last 4 chat messages
        for speaker, msg in chat_history[-4:]:
            icon = "👤" if speaker == "User" else "🤖"
            st.markdown(f"{icon} **{speaker}**: {msg}")

        # Divider before quiz
        st.divider()
        st.markdown("---")
        st.markdown('<div style="font-size:16px; font-weight:600;"> Did you pay attention? Try this challenge</div>', unsafe_allow_html=True)


        # Start dynamic quiz generation
        if st.button("🎯 Start Quiz"):
            st.session_state.show_quiz = True

            with st.spinner("Generating quiz based on the video..."):
                try:
                    # Use summary if available, otherwise use part of the transcript
                    source_text = st.session_state.raw_summary or st.session_state.transcript[:3000]

                    # Use LLM to generate multiple-choice questions
                    llm = ChatOpenAI(
                        temperature=0,
                        model="gpt-3.5-turbo",
                        openai_api_key=openai_api_key
                    )

                    prompt = f"""
                    Based on the following content, generate 5 multiple choice comprehension questions with 4 options each (A, B, C, D) 
                    and indicate the correct answer letter. Format the output in JSON like this:
                    
                    [
                        {{
                            "q": "What is the topic of the video?",
                            "options": ["A. Topic A", "B. Topic B", "C. Topic C", "D. Topic D"],
                            "answer": "B"
                        }},
                        ...
                    ]

                    Content:
                    {source_text}
                    """

                    response = llm.invoke(prompt)
                    st.session_state.dynamic_quiz = eval(response.content)  # NOTE: use json.loads if safer

                except Exception as e:
                    st.error(f"Failed to generate quiz: {e}")
                    st.session_state.dynamic_quiz = []

        # Display quiz questions if available
        if st.session_state.get("show_quiz") and st.session_state.get("dynamic_quiz"):
            st.markdown('<div style="font-size:16px; font-weight:600;">Comprehension Quiz:</div>', unsafe_allow_html=True)


            user_answers = []
            for i, q in enumerate(st.session_state.dynamic_quiz):
                st.markdown(f"**{q['q']}**")
                selected = st.radio("", q["options"], key=f"quiz_q{i}")
                user_answers.append(selected)

            if st.button("📊 Analyze Performance"):
                score = 0
                for i, q in enumerate(st.session_state.dynamic_quiz):
                    correct_option = q["options"][ord(q["answer"]) - ord("A")]
                    if user_answers[i] == correct_option:
                        score += 1

                percent = int((score / len(st.session_state.dynamic_quiz)) * 100)
                st.markdown(
    f'<div style="font-size:16px; font-weight:600; color:#28a745;"> Your Score: {score} out of {len(st.session_state.dynamic_quiz)} ({percent}%)</div>',
    unsafe_allow_html=True
)


                if percent >= 80:
                    st.success("🎉 Excellent! You understood the topic very well.")
                elif percent >= 50:
                    st.info("🟡 Good, but you should review some parts.")
                else:
                    st.markdown('<div style="color: #d39e00; font-size: 14px;">🔁 You need to review the video again for better understanding.</div>', unsafe_allow_html=True)


# Tab 3: Share summary to social media
with tab3:
    # Medium-sized heading
    st.markdown('<div style="font-size:20px; font-weight:600;">🔗 Share Summary</div>', unsafe_allow_html=True)

    if not st.session_state.summary:
        st.warning("⚠️ Generate a summary first.")
    else:
        short = st.session_state.raw_summary[:280]
        encoded = urllib.parse.quote(short)

        # Elegant social sharing buttons
        st.markdown(f"""
        <div style="display: flex; gap: 20px; justify-content: center; padding: 10px;">
            <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://example.com&summary={encoded}" target="_blank" style="text-decoration: none;">
                <button style="padding: 8px 16px; border-radius: 8px; background-color: #0077b5; color: white; border: none;">
                    🔗 LinkedIn
                </button>
            </a>
            <a href="https://wa.me/?text={encoded}" target="_blank" style="text-decoration: none;">
                <button style="padding: 8px 16px; border-radius: 8px; background-color: #25d366; color: white; border: none;">
                    📱 WhatsApp
                </button>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded}" target="_blank" style="text-decoration: none;">
                <button style="padding: 8px 16px; border-radius: 8px; background-color: #1da1f2; color: white; border: none;">
                    🐦 X
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# Extract keywords after summary generation
if st.session_state.get("raw_summary"):
    if "keywords" not in st.session_state:
        with st.spinner("Extracting keywords..."):
            def extract_keywords(text, api_key, language="English"):
                llm = ChatOpenAI(
                    temperature=0.3,
                    model="gpt-3.5-turbo",
                    openai_api_key=api_key
                )
                prompt = (
                    f"Extract 10-15 concise and important keywords or phrases from the following summary in {language}. "
                    f"Return them as a comma-separated list:\n\n{text[:2000]}"
                )
                return llm.invoke(prompt).content

            st.session_state.keywords = extract_keywords(
                st.session_state.raw_summary, openai_api_key, language="English"
            )

    if st.session_state.keywords:
        st.subheader("🔑 Video Keywords")
        st.markdown(f"`{st.session_state.keywords}`")
