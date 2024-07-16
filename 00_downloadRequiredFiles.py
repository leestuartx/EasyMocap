import os
import requests

def download_file(url, dest_path):
    if not os.path.exists(dest_path):
        print(f"Downloading {url} to {dest_path}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {dest_path}")
    else:
        print(f"File {dest_path} already exists")

base_path = r'H:\AI\EasyMocap\data\models'
os.makedirs(base_path, exist_ok=True)

files_to_download = [
    {"url": "http://visiondata.cis.upenn.edu/spin/model_checkpoint.pt", "dest": os.path.join(base_path, 'spin_checkpoints.pt')},
    {"url": "http://visiondata.cis.upenn.edu/spin/data.tar.gz", "dest": os.path.join(base_path, 'smpl_mean_params.npz')},
    {"url": "URL_TO_YOLOV4_WEIGHTS", "dest": os.path.join(base_path, 'yolov4.weights')},  # Replace with actual URL
    {"url": "URL_TO_HRNET_WEIGHTS", "dest": os.path.join(base_path, 'pose_hrnet_w48_384x288.pth')}  # Replace with actual URL
]

for file_info in files_to_download:
    download_file(file_info["url"], file_info["dest"])

print("All required files are downloaded.")
