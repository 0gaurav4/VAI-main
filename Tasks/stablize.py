import numpy as np
import cv2
import os

def movingAverage(curve, radius): 
    window_size = 2 * radius + 1
    f = np.ones(window_size) / window_size 
    curve_pad = np.lib.pad(curve, (radius, radius), 'edge') 
    curve_smoothed = np.convolve(curve_pad, f, mode='same') 
    curve_smoothed = curve_smoothed[radius:-radius]
    return curve_smoothed 

def smooth(trajectory, smoothing_radius): 
    smoothed_trajectory = np.copy(trajectory) 
    for i in range(3):
        smoothed_trajectory[:,i] = movingAverage(trajectory[:,i], radius=smoothing_radius)
    return smoothed_trajectory

def fixBorder(frame):
    s = frame.shape
    T = cv2.getRotationMatrix2D((s[1]/2, s[0]/2), 0, 1.04)
    frame = cv2.warpAffine(frame, T, (s[1], s[0]))
    return frame

def stabilize_video(video_path="stable.mp4", output_name="stabilized_video_out.avi", smoothing_radius=50):
    cap = cv2.VideoCapture(video_path) 
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) 
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_name, fourcc, fps, (2 * w, h))
    _, prev = cap.read() 
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY) 
    transforms = np.zeros((n_frames-1, 3), np.float32) 

    for i in range(n_frames-2):
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
        success, curr = cap.read() 
        if not success: 
            break 
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY) 
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None) 
        assert prev_pts.shape == curr_pts.shape 
        idx = np.where(status==1)[0]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]
        m = cv2.estimateAffinePartial2D(prev_pts, curr_pts)[0]
        dx = m[0,2]
        dy = m[1,2]
        da = np.arctan2(m[1,0], m[0,0])
        transforms[i] = [dx, dy, da]
        prev_gray = curr_gray

    trajectory = np.cumsum(transforms, axis=0) 
    smoothed_trajectory = smooth(trajectory, smoothing_radius) 
    difference = smoothed_trajectory - trajectory
    transforms_smooth = transforms + difference
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 

    for i in range(n_frames-2):
        success, frame = cap.read() 
        if not success:
            break
        dx = transforms_smooth[i,0]
        dy = transforms_smooth[i,1]
        da = transforms_smooth[i,2]
        m = np.zeros((2,3), np.float32)
        m[0,0] = np.cos(da)
        m[0,1] = -np.sin(da)
        m[1,0] = np.sin(da)
        m[1,1] = np.cos(da)
        m[0,2] = dx
        m[1,2] = dy
        frame_stabilized = cv2.warpAffine(frame, m, (w,h))
        frame_stabilized = fixBorder(frame_stabilized) 
        frame_out = cv2.hconcat([frame, frame_stabilized])
        if frame_out.shape[1] > 1920: 
            frame_out = cv2.resize(frame_out, (frame_out.shape[1]//2, frame_out.shape[0]//2));
        out.write(frame_out)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    return output_name

if __name__ == "__main__":
    # Example usage:
    stabilized_video_path = stabilize_video(r"C:\Users\gaura\Desktop\VAI\Tasks\stablize.mp4", "stabilized_video_out.avi")
    print("Stabilized video saved at:", stabilized_video_path)
