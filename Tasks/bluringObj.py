from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import cv2

# Function to blur the person in the frame
def blur_person(frame, boxes, clss, model, blur_item_name="person",  blur_ratio = 50):
    print("Entering blur_person function...")
    names = model.names
    print(f"Number of boxes: {len(boxes)}")
    print(f"Number of classes: {len(clss)}")
    for box, cls in zip(boxes, clss):
        print(f"Current box: {box}")
        print(f"Current class: {cls}")
        class_name = names[int(cls)]
        print(f"Current class name: {class_name}")
        if class_name == blur_item_name:
            print(f"Object {blur_item_name} found at box {box}")
            obj = frame[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
            print(f"Object obtained from frame: {obj.shape}")
            blur_obj = cv2.blur(obj, (blur_ratio, blur_ratio))
            print(f"Blurred object shape: {blur_obj.shape}")
            frame[int(box[1]):int(box[3]), int(box[0]):int(box[2])] = blur_obj
            print("Object blurred and replaced in frame successfully")
    print("Exiting blur_person function.")
    return frame
    return frame

# ...
def blur_content_in_video(path="/static/uploads", model=YOLO("yolov8n.pt"), output_path="/static/uploads", blur_ratio=50, show_preview=False, skip_save=False):
    """
    Function to blur content in a video.
    
    Args:
        path (str): Path to the input video.
        model (YOLO): YOLO object for object detection.
        output_path (str): Path to save the output video.
        blur_ratio (int): Blur radius for the objects.
        show_preview (bool): Flag to show video preview.
        skip_save (bool): Flag to skip saving the video.
    """
    print("Initializing VideoCapture object...")
    # Initialize VideoCapture object
    cap = cv2.VideoCapture(path)
    print("VideoCapture object initialized")
    
    # Get names of classes
    names = model.names
    print("Names of classes obtained")
    
    # Check if VideoCapture is open
    print(f"VideoCapture object is open: {cap.isOpened()}")
    
    # Initialize VideoWriter object (for saving the output video)
    if not skip_save:
        print("Initializing VideoWriter object...")
        w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
        codec = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        video_writer = cv2.VideoWriter(f"{output_path}", codec, fps, (w, h))
        print("VideoWriter object initialized")
    
    # Inside the while loop
    print("Processing video...")
    while True:
        print("Reading a frame from the video...")
        # Read a frame from the video
        success, im0 = cap.read()
        
        # Break the loop if there are no more frames
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break
        
        print("Performing object detection...")
        # Perform object detection
        results = model.predict(im0, show=False)
        boxes = results[0].boxes.xyxy.cpu().tolist()
        clss = results[0].boxes.cls.cpu().tolist()
        
        print("Creating an Annotator object for annotating the frame...")
        # Create an Annotator object for annotating the frame
        annotator = Annotator(im0, line_width=2, example=names)
        
        print("Blurring person in the frame...")
        # Blur person in the frame
        if boxes is not None:
            blur_item_name = "bird"  # Replace input statement with the desired value
            im0 = blur_person(im0, boxes, clss, model, blur_item_name=blur_item_name, blur_ratio=blur_ratio)
            
            # Annotate the frame with the detected objects
            for box, cls in zip(boxes, clss):
                annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])
        
        print("Showing video preview...")
        # Show video preview
        if show_preview:
            cv2.imshow("blur task", im0)
        
        print("Writing the frame to the output video...")
        # Write the frame to the output video
        if not skip_save: 
            video_writer.write(im0)
        
        print("Waiting for key press...")
        # Exit the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break
    
    print("Releasing resources...")
    # Release resources
    cap.release()
    if not skip_save:video_writer.release()
    if show_preview:cv2.destroyAllWindows()
    print("Resources released")

# testing
if __name__ == "__main__":
    blur_content_in_video(show_preview=True, skip_save=True, path=r'C:\Users\gaura\Desktop\VAI\static\uploads\1.mp4')