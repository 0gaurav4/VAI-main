# function to create clip extractor
import os
def create_clip_extractor(video_path="car.mp4",
                          start_time = 3,
                          end_time = 4,
                          output_name="clip.mp4"):
    from moviepy.editor import VideoFileClip
    video = VideoFileClip(video_path)
    clip = video.subclip(start_time, end_time)
    clip.write_videofile(output_name)

if __name__ == "__main__":
    create_clip_extractor()
    