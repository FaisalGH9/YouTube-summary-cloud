from faster_whisper import WhisperModel  # Import the Whisper model from the faster-whisper package

# Function to transcribe a video/audio file using Whisper
def transcribe_video(video_path):
    # Load the tiny version of the Whisper model
    model = WhisperModel("tiny", device="cpu", compute_type="int8")  # Use CPU with 8-bit precision for better performance on low-resource devices

    # Perform transcription
    segments, info = model.transcribe(video_path)  # 'segments' contains list of transcribed parts; 'info' has metadata

    transcript = ""
    # Concatenate all segments into a single transcript string
    for segment in segments:
        transcript += segment.text + " "
    
    return transcript.strip()  # Return final transcript without trailing spaces
