# function to create speed adjustment of video
import os
from moviepy.editor import VideoFileClip


def change_playback_speed(video_path="static/uploads/car.mp4", speed_factor=2):
    print(video_path)
    print(speed_factor)
    os.makedirs('static/results', exist_ok=True)
    video = VideoFileClip(video_path)
    video_high_speed = video.speedx(speed_factor)  # High speed segment
    video_high_speed.write_videofile(f"static/results/updated_{os.path.basename(video_path)}")
    return f"updated_{os.path.basename(video_path)}"


# def create_high_speed(video_path="car.mp4"):
#     video = VideoFileClip(video_path)
#     video_high_speed = video.speedx(2)  # High speed segment
#     video_high_speed.write_videofile("high_speed.mp4")

# def create_slow_motion(video_path="car.mp4"):
#     video = VideoFileClip(video_path)
#     video_slow_motion = video.speedx(0.5)  # Slow motion segment
#     video_slow_motion.write_videofile("slow_motion.mp4")

# create_high_speed()
# create_slow_motion()


if __name__ == "__main__":
    change_playback_speed()