import os
import sys
import argparse
import cv2

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

def run_mediapipe(data_dir):
    os.system(f'python H:\\AI\\EasyMocap\\apps\\preprocess\\extract_keypoints.py {data_dir} --mode mp-holistic')

def initialize_pose(data_config, exp_config, root_dir, subs):
    os.system(f'emc --data {data_config} --exp {exp_config} --root {root_dir} --subs {subs}')

def fit_smpl(data_path, config_dir):
    # Define paths
    cfg_model = os.path.join(config_dir, 'model/smpl.yml')
    cfg_data = os.path.join(config_dir, 'data/multivideo.yml')    # Update with your data config path
    cfg_exp = os.path.join(config_dir, 'fit/1v1p.yml')      # Update with your experiment config path

    cmd = f'python H:\\AI\\EasyMocap\\apps\\fit\\fit.py --cfg_model {cfg_model} --cfg_data {cfg_data} --cfg_exp {cfg_exp} --opt_data args.path {data_path} args.out {os.path.join(data_path, "output")}'

    # Log and run the command
    print(f'Running command: {cmd}')
    os.system(cmd)

    #os.system(f'python H:\\AI\\EasyMocap\\apps\\fit\\fit.py --cfg_data config/fit/')
    pass
    # There is no smpl filtting, the fitting is done on yml file apparently

def convert_to_bvh(script_path, input_smpl_path, output_bvh_path):
    blender_path = r'C:/Program Files/Blender Foundation/Blender 3.3/blender.exe'
    os.makedirs(output_bvh_path, exist_ok=True)
    command = f'"{blender_path}" -b -P {script_path} -- {input_smpl_path} --out {output_bvh_path}'
    os.system(command)

def main(video_path):
    # Extract the name of the video
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Define paths
    base_dir = 'H:\\AI\\EasyMocap' # Base Project Path
    output_dir = os.path.join(base_dir, 'output') # Where we will output all files.
    project_dir = os.path.join(output_dir, video_name)  # Where everything for this capture are located
    data_dir = os.path.join(base_dir, video_name)  # Where the SMPL models are located

    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(project_dir, exist_ok=True)

    images_dir = os.path.join(project_dir, 'images')
    annots_dir = os.path.join(project_dir, 'annots')
    smpl_output_dir = os.path.join(project_dir, 'smpl')
    bvh_output_dir = os.path.join(project_dir, 'bvh')

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(annots_dir, exist_ok=True)
    os.makedirs(smpl_output_dir, exist_ok=True)
    os.makedirs(bvh_output_dir, exist_ok=True)

    data_config = 'H:\\AI\\EasyMocap\\config\\datasets\\svimage.yml'
    exp_config = 'H:\\AI\\EasyMocap\\config\\1v1p\\hrnet_pare_finetune.yml'#_smplx.yml'
    script_path = 'H:\\AI\\EasyMocap\\scripts\\postprocess\\convert2bvh.py'
    subs = 'images'

    print('Starting processing...')
    # Run the steps
    #extract_frames(video_path, images_dir)
    print('Extracted image frames to', images_dir)
    #run_mediapipe(project_dir)
    #initialize_pose(data_config, exp_config, project_dir, subs)

    fit_smpl(project_dir, 'H:\\AI\\EasyMocap\\config')
    #convert_to_bvh(script_path, smpl_output_dir, bvh_output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video for mocap")
    parser.add_argument('--video_path', type=str, required=True, help='Path to the input video')
    args = parser.parse_args()

    main(args.video_path)
