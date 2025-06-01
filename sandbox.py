import os
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from moviepy import ImageClip, concatenate_videoclips, ColorClip, AudioFileClip
import numpy as np # Import numpy
from addAudio import fish_audio

# --- Configuration (rest remains the same) ---
OUTPUT_FOLDER = "instagram_fish_videos"
BACKGROUND_IMAGE_PATH = "indianoceanarea.jpg"
FONT_PATH = "/Library/Fonts/Arial.ttf" # Update this to your font file path
MUSIC_FILE_PATH = "music.mp3"
SIZE_LARGE = 70
TEXT_COLOR = (255, 255, 255) # White
STROKE_COLOR = (0, 0, 0) # Black
VIDEO_WIDTH = 1080 # Instagram Post Width (1:1 aspect ratio)
VIDEO_HEIGHT = 1920 # Instagram Post Height
FPS = 30 # Frames per second

GUESS_SEGMENT_DURATION = 5 # seconds
LOSE_SEGMENT_DURATION = 4 # seconds

# --- Simplified Fish Database (rest remains the same) ---
FISH_DATABASE = {
    "Abalistes Stellatus": "https://www.fishi-pedia.com/wp-content/uploads/2025/01/Abalistes-stellatus-e1736937646832-725x483.jpg",
}

# --- Helper Functions (remain the same) ---
def download_image(url):
    """Downloads an image from a URL and returns it as a PIL Image object."""
    try:
        response = requests.get(url, timeout=10) # Added timeout for robustness
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        img = Image.open(BytesIO(response.content))
        return img.convert("RGBA") # Ensure RGBA for proper pasting with alpha
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {url}: {e}")
        return None
    except IOError as e:
        print(f"Error opening image data from {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while processing image from {url}: {e}")
        return None

def create_frame_image(text, font, text_position_y_ratio, fish_img=None, background_img=None):
    """
    Creates a single PIL Image frame with background, text, and optional fish image.
    """

    frame = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color = (0, 0, 0)) # Fallback to black
    draw = ImageDraw.Draw(frame)

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    # text_height = bbox[3] - bbox[1] # Not directly used for Y as we use ratio

    text_x = (VIDEO_WIDTH - text_width) / 2
    text_y = int(VIDEO_HEIGHT * text_position_y_ratio - 300)

    draw.text((text_x, text_y), text, font=font, fill=TEXT_COLOR, stroke_width=2, stroke_fill=STROKE_COLOR)

    # Overlay fish image if provided
    if fish_img:
        # Resize fish image to fit within the frame, maintaining aspect ratio
        max_fish_width = int(VIDEO_WIDTH * 0.9) # 90% of video width
        max_fish_height = int(VIDEO_HEIGHT * 0.8) # 70% of video height (leaving room for text)

        # Create a mutable copy and resize
        fish_img_copy = fish_img.copy()
        fish_img_copy.thumbnail((max_fish_width, max_fish_height), Image.Resampling.LANCZOS)
        fish_width, fish_height = fish_img_copy.size

        # Position fish image (e.g., centered horizontally, below top text)
        print(fish_width)
        fish_x = (VIDEO_WIDTH - fish_width) // 2
        fish_y = int(VIDEO_HEIGHT * 0.35) # Adjust as needed to position below top text

        # Paste with mask for transparency if fish_img has alpha channel
        frame.paste(fish_img_copy, (fish_x, fish_y), fish_img_copy if fish_img_copy.mode == 'RGBA' else None)

    return frame

# --- Main Video Generation Logic ---

def generate_instagram_video():
    # Create output folder if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Load background image
    try:
        background_img = Image.open(BACKGROUND_IMAGE_PATH).resize((VIDEO_WIDTH, VIDEO_HEIGHT)).convert("RGB")
    except FileNotFoundError:
        print(f"Error: Background image not found at {BACKGROUND_IMAGE_PATH}. Using a solid black background as fallback.")
        background_img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color = (0, 0, 0)) # Fallback to black

    # Try to load fonts
    try:
        font_large = ImageFont.truetype(FONT_PATH, SIZE_LARGE)

    except IOError:
        print("running")
        print(f"Warning: Font file not found at {FONT_PATH}. Using default PIL font. Text might look different.")
        font_large = ImageFont.load_default()

    # Randomly select a fish
    selected_fish_name = random.choice(list(FISH_DATABASE.keys()))
    fish_image_url = FISH_DATABASE[selected_fish_name]

    print(f"Selected fish for this video: {selected_fish_name}")
    print(f"Attempting to download image from: {fish_image_url}")

    fish_img = download_image(fish_image_url)

    if not fish_img:
        print("Failed to download fish image. Cannot proceed with video generation.")
        return

    video_clips = []

    # --- Create "Guess the fish" segment ---
    print("Creating 'Guess the fish' segment...")
    guess_text = "Pick a fish in the Indian Ocean"
    guess_frame_pil = create_frame_image(guess_text, font_large, 0.4, background_img) # Text at 10% from top
    # Convert PIL Image to NumPy array for moviepy
    guess_frame_np = np.array(guess_frame_pil)
    guess_clip = ImageClip(guess_frame_np, duration=GUESS_SEGMENT_DURATION).with_fps(FPS) # Removed 'size' keyword
    video_clips.append(guess_clip)

    # --- Create "If you guessed BLANK you lose" segment ---
    print("Creating 'You lose' segment...")
    lose_text = f"If you picked {selected_fish_name}\nyou lose"
    lose_frame_pil = create_frame_image(lose_text, font_large, 0.4, fish_img) # Text centered (roughly 40% from top)
    # Convert PIL Image to NumPy array for moviepy
    lose_frame_np = np.array(lose_frame_pil)
    lose_clip = ImageClip(lose_frame_np, duration=LOSE_SEGMENT_DURATION).with_fps(FPS) # Removed 'size' keyword
    video_clips.append(lose_clip)

    # --- Concatenate clips and write final video ---
    print("Concatenating clips and writing final video...")
    final_clip = concatenate_videoclips(video_clips)
    output_video_path = os.path.join(OUTPUT_FOLDER, "instagram_fish_game_video.mp4")


    try:
        final_clip.write_videofile(
            output_video_path,
            fps=FPS,
            codec="libx264", # H.264 codec, widely supported
            audio_codec="aac", # AAC audio codec (even without audio, good practice)
            bitrate="5000k", # Adjust bitrate for quality vs. file size (e.g., 5000k for good quality)
            preset="medium", # Encoding preset (ultrafast, superfast, fast, medium, slow, slower, veryslow)
            threads=os.cpu_count() or 4 # Use all available CPU cores or default to 4
        )
        print(f"\nVideo generated successfully at: {output_video_path}")
        print("You can now upload this MP4 to Instagram!")
    except Exception as e:
        print(f"\nError generating video with moviepy: {e}")
        print("Please ensure FFmpeg is installed and accessible in your system's PATH.")
        print("You can test FFmpeg by typing 'ffmpeg -version' in your terminal.")

    fish_audio(f"{OUTPUT_FOLDER}/instagram_fish_game_video.mp4", MUSIC_FILE_PATH, "instagram_fish_game.mp4")
    
# --- Run the script ---
if __name__ == "__main__":
    generate_instagram_video()