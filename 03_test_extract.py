import os
import cv2

# Step 1: Extract frames from the video
def extract_frames(video_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(os.path.join(output_dir, f'{frame_id:06d}.jpg'), frame)
        frame_id += 1
    cap.release()

# Step 2: Run Mediapipe for keypoint detection
def run_mediapipe(data_dir):
    os.system(f'python H:\\AI\\EasyMocap\\apps\\preprocess\\extract_keypoints.py {data_dir} --mode mp-holistic')

# Step 3: Initialize the pose estimation
def initialize_pose(data_config, exp_config, root_dir, ranges, subs):
    os.system(f'emc --data {data_config} --exp {exp_config} --root {root_dir} --ranges {ranges} --subs {subs}')

# Define paths
video_path = 'H:\\AI\\EasyMocap\\video\\sample1.mp4'
data_dir = 'H:\\AI\\EasyMocap\\data\\sample1'
images_dir = os.path.join(data_dir, 'images\\video')
data_config = 'H:\\AI\\EasyMocap\\config\\datasets\\svimage.yml'
exp_config = 'H:\\AI\\EasyMocap\\config\\1v1p\\hrnet_pare_finetune.yml'
ranges = '0 500 1'
subs = 'video'

# Run the steps
extract_frames(video_path, images_dir)
run_mediapipe(data_dir)
initialize_pose(data_config, exp_config, data_dir, ranges, subs)
