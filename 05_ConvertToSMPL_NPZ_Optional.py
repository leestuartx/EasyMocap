import numpy as np
import os
import json


def read_smpl_params(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    params_list = data if isinstance(data, list) else data['annots']
    return [{
        'poses': np.array(entry['poses'][0]),  # Flatten the single-element list
        'shapes': np.array(entry['shapes'][0]),  # Flatten the single-element list
        'Rh': np.array(entry['Rh'][0]),  # Flatten the single-element list
        'Th': np.array(entry['Th'][0]),  # Flatten the single-element list
        'expression': np.zeros(10),  # Assuming expression is not in the data, use zeros
        'pose_hand': np.zeros(90)  # Assuming pose_hand is not in the data, use zeros
    } for entry in params_list]


def combine_smpl_params(json_dir):
    all_poses, all_shapes, all_Rh, all_Th, all_expression, all_pose_hand = [], [], [], [], [], []

    json_files = sorted([os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')])
    for json_path in json_files:
        params = read_smpl_params(json_path)
        for param in params:
            all_poses.append(param['poses'])
            all_shapes.append(param['shapes'])
            all_Rh.append(param['Rh'])
            all_Th.append(param['Th'])
            all_expression.append(param['expression'])
            all_pose_hand.append(param['pose_hand'])

    print(f"Total poses: {len(all_poses)}, Each pose length: {len(all_poses[0]) if all_poses else 'N/A'}")

    all_poses = np.array(all_poses)
    print(f"all_poses shape before reshape: {all_poses.shape}")

    if len(all_poses[0]) == 69:
        print("Each pose has 69 elements, appending zeros to match 75 dimensions.")
        all_poses = np.hstack([all_poses, np.zeros((all_poses.shape[0], 6))])

    all_poses = all_poses.reshape(-1, 75)  # Adjusted to fit 75 dimensions for SMPL-X
    all_shapes = np.array(all_shapes).reshape(-1, 10)
    all_Rh = np.array(all_Rh).reshape(-1, 3)
    all_Th = np.array(all_Th).reshape(-1, 3)
    all_expression = np.array(all_expression).reshape(-1, 10)
    all_pose_hand = np.array(all_pose_hand).reshape(-1, 90)

    return all_Th, all_poses, all_shapes, all_Rh, all_expression, all_pose_hand


def save_to_npz(output_path, trans, poses, betas, root_orient, expression, pose_hand):
    np.savez(output_path, trans=trans, pose_body=poses, betas=betas, root_orient=root_orient, expression=expression,
             pose_hand=pose_hand)
    print(f'Saved to {output_path}')


if __name__ == "__main__":
    json_dir = 'H:\\AI\\EasyMocap\\output\\sv1p\\smpl'  # Adjust to your directory
    output_path = 'H:\\AI\\EasyMocap\\output\\combined_smplx.npz'  # Adjust to your output path

    trans, poses, betas, root_orient, expression, pose_hand = combine_smpl_params(json_dir)
    save_to_npz(output_path, trans, poses, betas, root_orient, expression, pose_hand)
