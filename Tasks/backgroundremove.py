# background removal
import os
import cv2
import mediapipe as mp
import numpy as np
from moviepy.editor import VideoFileClip

def create_video_background_removal(video_path=r"C:\Users\gaura\Desktop\VAI\Tasks\man.mp4",
                                     output_name="remove_background.mp4"):
    BG_COLOR = (192, 192, 192) # gray
    MASK_COLOR = (255, 255, 255) # white
    mp_drawing = mp.solutions.drawing_utils
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    video = VideoFileClip(video_path)
    
    
    def remove_background(image):
        with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = selfie_segmentation.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
            bg_image = None
            if bg_image is None:
                bg_image = np.zeros(image.shape, dtype=np.uint8)
                bg_image[:] = BG_COLOR
                output_image = np.where(condition, image, bg_image)
            return output_image
    
    modified_video = video.fl_image(remove_background)
    modified_video.write_videofile(output_name, codec="libx264", audio_codec="aac", fps=video.fps)


if __name__ == "__main__":
    create_video_background_removal()