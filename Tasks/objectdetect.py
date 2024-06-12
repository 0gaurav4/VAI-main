import cv2 as cv
import argparse
import sys
import numpy as np
import os

def object_detection_yolo(video_path="run.mp4", output_name="yolo_out_py", device='cpu'):
    # Initialize the parameters
    confThreshold = 0.5  # Confidence threshold
    nmsThreshold = 0.4   # Non-maximum suppression threshold
    inpWidth = 416       # Width of network's input image
    inpHeight = 416      # Height of network's input image

    # Load names of classes
    classesFile = r"C:\Users\gaura\Desktop\VAI\Tasks\coco.names"
    with open(classesFile, 'rt') as f:
        classes = f.read().rstrip('\n').split('\n')

    # Give the configuration and weight files for the model and load the network using them.
    modelConfiguration = r"C:\Users\gaura\Desktop\VAI\Tasks\yolov3.cfg"
    modelWeights = r"C:\Users\gaura\Desktop\VAI\Tasks\yolov3.weights"

    net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)

    if device == 'cpu':
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        print('Using CPU device.')
    elif device == 'gpu':
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        print('Using GPU device.')

    # Get the names of the output layers
    def getOutputsNames(net):
        # Get the names of all the layers in the network
        layersNames = net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # Draw the predicted bounding box
    def drawPred(classId, conf, left, top, right, bottom):
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

        label = '%.2f' % conf

        # Get the label for the class name and its confidence
        if classes:
            assert(classId < len(classes))
            label = '%s:%s' % (classes[classId], label)

        # Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])), (left + round(1.5 * labelSize[0]), top + baseLine),
                     (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

    # Remove the bounding boxes with low confidence using non-maxima suppression
    def postprocess(frame, outs):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non-maximum suppression to eliminate redundant overlapping boxes with lower confidences.
        indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            drawPred(classIds[i], confidences[i], left, top, left + width, top + height)

    # Process inputs
    winName = 'Deep learning object detection in OpenCV'
    cv.namedWindow(winName, cv.WINDOW_NORMAL)

    output_file = f"{output_name}.avi"
    cap = cv.VideoCapture(video_path) if video_path else cv.VideoCapture(0)

    # Get the video writer initialized to save the output video
    if not video_path:
        output_file = f"{output_name}.jpg"
    else:
        vid_writer = cv.VideoWriter(output_file, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                                    (round(cap.get(cv.CAP_PROP_FRAME_WIDTH)), round(cap.get(cv.CAP_PROP_FRAME_HEIGHT))))

    while cv.waitKey(1) < 0:
        # Get frame from the video
        has_frame, frame = cap.read()

        # Stop the program if reached end of video
        if not has_frame:
            print("Done processing !!!")
            print("Output file is stored as ", output_file)
            cv.waitKey(3000)
            # Release device
            cap.release()
            break

        # Create a 4D blob from a frame.
        blob = cv.dnn.blobFromImage(frame, 1 / 255, (inpWidth, inpHeight), [0, 0, 0], 1, crop=False)

        # Sets the input to the network
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = net.forward(getOutputsNames(net))

        # Remove the bounding boxes with low confidence
        postprocess(frame, outs)

        # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
        t, _ = net.getPerfProfile()
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        # Write the frame with the detection boxes
        if not video_path:
            cv.imwrite(output_file, frame.astype(np.uint8))
        else:
            vid_writer.write(frame.astype(np.uint8))

        cv.imshow(winName, frame)

    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Object Detection using YOLO in OpenCV')
    parser.add_argument('--device', default='cpu', help="Device to perform inference on 'cpu' or 'gpu'.")
    parser.add_argument('--image', help='Path to image file.')
    parser.add_argument('--video', help='Path to video file.')
    args = parser.parse_args()
    
    object_detection_yolo(video_path=args.video, output_name="yolo_out_py", device=args.device)
