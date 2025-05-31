import pandas as pd
import random
import requests
import os
from moviepy import ImageClip, TextClip, CompositeVideoClip
from PIL import Image
import time

class FishVideoGenerator:
    def __init__(self, csv_path, output_dir="fish_videos", image_dir="fish_images"):
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.image_dir = image_dir
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
    
    def load_fish_data(self):
        """Load fish data from CSV file"""
        try:
            df = pd.read_csv(self.csv_path)
            return df
        except FileNotFoundError:
            print(f"CSV file {self.csv_path} not found!")
            return None
    
    def get_random_fish(self, df):
        """Get a random fish from the dataframe"""
        return df.sample(1).iloc[0]
    
    def download_fish_image(self, fish_name, image_url=None):
        """
        Download fish image from URL or use a placeholder service
        Returns the local image path
        """
        # Clean fish name for filename
        safe_filename = "".join(c for c in fish_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_path = os.path.join(self.image_dir, f"{safe_filename}.jpg")
        
        # Check if image already exists
        if os.path.exists(image_path):
            return image_path
        
        try:
            if image_url:
                # Download from provided URL
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
            else:
                # Use a placeholder service or search API
                # This is a simplified example - you'd want to implement proper image search
                placeholder_url = f"https://via.placeholder.com/800x600/0066cc/ffffff?text={fish_name.replace(' ', '+')}"
                response = requests.get(placeholder_url, timeout=10)
                response.raise_for_status()
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
            
            return image_path
            
        except Exception as e:
            print(f"Failed to download image for {fish_name}: {e}")
            return self.create_text_placeholder(fish_name)
    
    def create_text_placeholder(self, fish_name):
        """Create a simple text-based placeholder image"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple colored background with fish name
        img = Image.new('RGB', (800, 600), color='#0066cc')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position to center it
        text = fish_name
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((800 - text_width) // 2, (600 - text_height) // 2)
        draw.text(position, text, fill='white', font=font)
        
        # Save placeholder image
        safe_filename = "".join(c for c in fish_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_path = os.path.join(self.image_dir, f"{safe_filename}_placeholder.jpg")
        img.save(image_path)
        
        return image_path
    
    def create_video(self, fish_name, image_path, video_duration=5):
        """Create video with fish image and text"""
        try:
            # Load and resize image if needed
            image_clip = ImageClip(image_path).with_duration(video_duration)
            
            # Resize image to fit standard dimensions while maintaining aspect ratio
            # image_clip = image_clip.resize(height=720)
            
            # For now, let's just create a video with the image only
            # You can add text overlays later once we get the basic version working
            final_clip = image_clip
            
            # Generate output filename
            safe_filename = "".join(c for c in fish_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_path = os.path.join(self.output_dir, f"{safe_filename}_quiz.mp4")
            
            # Write video file
            final_clip.write_videofile(
                output_path, 
                fps=24,
                logger=None  # Suppress moviepy logs
            )
            
            # Clean up clips to free memory
            final_clip.close()
            image_clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error creating video for {fish_name}: {e}")
            return None
    
    def generate_single_video(self):
        """Generate a single random fish video"""
        # Load fish data
        df = self.load_fish_data()
        if df is None:
            return None
        
        # Get random fish
        fish_data = self.get_random_fish(df)
        fish_name = fish_data.get('name', 'Unknown Fish')
        
        # Check if CSV has image URL column
        image_url = fish_data.get('image_url', None)
        
        print(f"Selected fish: {fish_name}")
        
        # Download/get fish image
        image_path = self.download_fish_image(fish_name, image_url)
        
        if not image_path:
            print("Failed to get fish image")
            return None
        
        # Create video
        video_path = self.create_video(fish_name, image_path)
        
        if video_path:
            print(f"Video created successfully: {video_path}")
            return video_path
        else:
            print("Failed to create video")
            return None
    
    def generate_multiple_videos(self, count=5):
        """Generate multiple random fish videos"""
        df = self.load_fish_data()
        if df is None:
            return []
        
        created_videos = []
        
        for i in range(count):
            print(f"\nGenerating video {i+1}/{count}...")
            
            fish_data = self.get_random_fish(df)
            fish_name = fish_data.get('name', f'Unknown Fish {i+1}')
            image_url = fish_data.get('image_url', None)
            
            print(f"Selected fish: {fish_name}")
            
            # Download/get fish image
            image_path = self.download_fish_image(fish_name, image_url)
            
            if image_path:
                # Create video
                video_path = self.create_video(fish_name, image_path)
                
                if video_path:
                    created_videos.append(video_path)
                    print(f"✓ Video created: {video_path}")
                else:
                    print(f"✗ Failed to create video for {fish_name}")
            else:
                print(f"✗ Failed to get image for {fish_name}")
            
            # Small delay to avoid overwhelming APIs
            time.sleep(1)
        
        return created_videos

# Example usage
if __name__ == "__main__":
    # Initialize the generator
    generator = FishVideoGenerator('fish_list.csv')
    
    # Generate a single video
    video_path = generator.generate_single_video()
    
    # Or generate multiple videos
    # video_paths = generator.generate_multiple_videos(3)
    
    print("Done!")

# Example CSV structure (fish_list.csv):
# name,scientific_name,image_url,description
# "Clownfish","Amphiprioninae","https://example.com/clownfish.jpg","Colorful reef fish"
# "Blue Tang","Paracanthurus hepatus","https://example.com/bluetang.jpg","Bright blue marine fish"
# "Angelfish","Pterophyllum","https://example.com/angelfish.jpg","Elegant freshwater fish"