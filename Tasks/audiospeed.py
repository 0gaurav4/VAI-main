def adjust_video_volume(video_path, mute=False, volume=1.0, speed=2.0):
    # Import necessary libraries
    import moviepy.editor as mp

    # Load the video
    video = mp.VideoFileClip(video_path="audio.mp4")

    # Mute the video if required
    if mute:
        video = video.volumex(0)

    # Adjust the volume if required
    if volume != 1.0:
        video = video.volumex(volume)

    # Speed up the video if required
    if speed == "fast":
        video = video.fx(mp.vfx.speedx, 2.0)

    # Slow down the video if required
    if speed == "slow":
        video = video.fx(mp.vfx.speedx, 0.5)

    # Save the modified video
    output_path = video_path.replace('.mp4', '_modified.mp4')
    video.write_videofile(output_path, codec='libx264')

    # Print the output path
    print(f"Modified video saved at: {output_path}")

if __name__ == "__main__":
    adjust_video_volume(video_path="audio.mp4", mute=False, volume=1.0, speed=2.0)
