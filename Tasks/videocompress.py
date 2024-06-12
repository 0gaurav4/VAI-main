# function to create video compression
import os
def create_video_compression(video_path="car.mp4",
                             resize=0.5,
                             fps=30,
                             output_name="compressed.mp4"):
    from moviepy.editor import VideoFileClip

    video = VideoFileClip(video_path)
    video = video.resize(resize)
    video = video.set_fps(fps)
    video.write_videofile(output_name)

if __name__ == "__main__":
    create_video_compression()