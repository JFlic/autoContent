#!/usr/bin/env python3
"""
Simple script to add music.mp3 to instagram_fish_game_video.mp4
Requires: pip install moviepy
"""

from moviepy import VideoFileClip, AudioFileClip

# Your file names
video_file = r"instagram_fish_videos/instagram_fish_game_video.mp4"
audio_file = "music.mp3"
output_file = "instagram_fish_game_video_with_music.mp4"

def fish_audio(video_file, audio_file, output_file):
    print("Loading video...")
    video = VideoFileClip(video_file)

    print("Loading music...")
    audio = AudioFileClip(audio_file)

    print("Combining video and audio...")
    # If music is longer than video, it will be trimmed automatically
    # If music is shorter, it will just play once
    final_video = video.with_audio(audio)

    print("Saving final video...")
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac')

    print(f"Done! Your video with music is saved as: {output_file}")

    # Clean up
    video.close()
    audio.close()
    final_video.close()