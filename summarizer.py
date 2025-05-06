from openai import OpenAI  # Import OpenAI client

# Function to split text into smaller chunks for summarization
def split_text_for_summary(text, max_chunks=8):
    words = text.split()
    chunk_size = max(1, len(words) // max_chunks)  # Determine size of each chunk
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks[:max_chunks]  # Return only the desired number of chunks

# Main function to generate summary with table of contents (TOC)
def summarize_text_with_toc_2000(text, api_key, language="العربية", topic="Detailed Summary", placeholder=None, video_duration_min=7):
    client = OpenAI(api_key=api_key)  # Initialize OpenAI client with API key
    chunks = split_text_for_summary(text, max_chunks=5)  # Split text into 5 parts

    # Define system prompt based on the language
    system_prompt = (
        "أنت مساعد ذكي يلخص مقاطع فيديو طويلة بشكل احترافي باللغة العربية."
        if language == "العربية"
        else "You are a smart assistant that summarizes long videos professionally in English."
    )

    # Choose prompt instructions based on summary type and language
    if topic == "Detailed Summary":
        instruction_ar = """تلخص هذا الجزء من الفيديو بتفصيل:
- قدم عنوانًا قصيرًا مناسبًا.
- ثم أضف ملخصًا يغطي جميع الأفكار المهمة.
- لا تتجاوز  كلمات النص المستخرج 
النص:
{chunk}
"""
        instruction_en = """Summarize this part of the video in detail:
- Provide a short appropriate title.
- Then add a detailed summary covering all key points.
- Do not exceed 300 words.
Text:
{chunk}
"""
    elif topic == "Medium Summary":
        instruction_ar = """تلخص هذا الجزء من الفيديو بشكل متوسط:
- قدم عنوانًا قصيرًا مناسبًا.
- ثم أضف ملخصًا متوسطًا يغطي النقاط الرئيسية فقط.
- لا تتجاوز 150 كلمة.
النص:
{chunk}
"""
        instruction_en = """Summarize this part of the video moderately:
- Provide a short appropriate title.
- Then add a medium summary covering the main points only.
- Do not exceed 150 words.
Text:
{chunk}
"""
    else:  # Short Summary
        instruction_ar = """تلخص هذا الجزء من الفيديو باختصار شديد:
- قدم عنوانًا قصيرًا مناسبًا.
- ثم أضف ملخصًا مختصرًا جدًا يغطي أهم فكرة فقط.
- لا تتجاوز 80 كلمة.
النص:
{chunk}
"""
        instruction_en = """Summarize this part of the video very briefly:
- Provide a short appropriate title.
- Then add a very brief summary covering the main idea only.
- Do not exceed 80 words.
Text:
{chunk}
"""

    # Select prompt based on language
    user_prompt_template = instruction_ar if language == "العربية" else instruction_en

    # Initialize summary and table of contents
    full_summary = ""
    table_of_contents = "📋 **Table of Contents**\n\n"
    timestamp_interval = max(1, video_duration_min // len(chunks))  # Estimate time for chapters

    # Loop through each text chunk and summarize
    for i, chunk in enumerate(chunks):
        timestamp = f"[{int(i * timestamp_interval):02d}:00]"  # e.g., [00:00], [01:00], ...
        chapter_number = i + 1

        # Request summary from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_template.format(chunk=chunk)}
            ],
            temperature=0.4,
            max_tokens=300
        )

        result = response.choices[0].message.content  # Extract response text

        # Extract title from the first line of the result
        title_line = result.split("\n")[0].strip()
        title = title_line.replace("عنوان:", "").strip(" :-–").capitalize()

        # Add entry to TOC and full summary
        table_of_contents += f"✅ Chapter {chapter_number}: {title} ({timestamp})\n"
        full_summary += f"{timestamp}\n📌 **{title}**\n{result}\n\n"

        # Optionally update placeholder (e.g., real-time progress display)
        if placeholder is not None:
            placeholder.markdown(table_of_contents + "\n---\n\n" + full_summary)

    # Return final result: TOC + complete summary
    return table_of_contents + "\n---\n\n" + full_summary
