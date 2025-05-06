import cv2  # OpenCV library for video processing

# Function to extract all frames from a video file
def extract_key_frames(video_path):
    cap = cv2.VideoCapture(video_path)  # Open the video file
    frames = []  # List to store extracted frames

    # Read frames one by one
    while cap.isOpened():
        ret, frame = cap.read()  # 'ret' indicates if the frame was read successfully
        if not ret:
            break  # Exit loop if no more frames

        frames.append(frame)  # Store the frame in the list

    cap.release()  # Release the video capture object
    return frames  # Return the list of all frames
