from urllib.parse import urlparse, parse_qs  # Import URL parsing utilities

# Function to extract the video ID from various YouTube URL formats
def extract_video_id(url):
    """
    Extracts the YouTube video ID from a given URL.
    Supports URLs like:
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    parsed_url = urlparse(url)  # Parse the URL into components

    # Handle short URLs like https://youtu.be/VIDEO_ID
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]  # Strip the leading '/'

    # Handle standard YouTube domains
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        # Watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]

        # Embed URL: https://www.youtube.com/embed/VIDEO_ID
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]

        # Old-style /v/ URL: https://www.youtube.com/v/VIDEO_ID
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]

    # Return None if format is unsupported
    return None
