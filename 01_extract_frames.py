import cv2
import os

video_path = 'H:\\AI\\EasyMocap\\video\\sample1.mp4'
output_dir = 'H:\\AI\\EasyMocap\\data\\sample1\\images'

cap = cv2.VideoCapture(video_path)
frame_id = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imwrite(os.path.join(output_dir, f'{frame_id:06d}.jpg'), frame)
    frame_id += 1
cap.release()
