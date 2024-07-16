import os

# Paths
blender_path = r'C:/Program Files/Blender Foundation/Blender 3.3/blender.exe'
script_path = r'H:\AI\EasyMocap\scripts\postprocess\convert2bvh.py'
input_smpl_path = r'H:\AI\EasyMocap\output\proj\smpl'
output_bvh_path = r'H:\AI\EasyMocap\output\bvh'  # Directory where you want the BVH files

# Ensure the output directory exists
os.makedirs(output_bvh_path, exist_ok=True)

# Construct the Blender command
command = f'"{blender_path}" -b -P {script_path} -- {input_smpl_path} --out {output_bvh_path} '

# Print the command (optional, for debugging purposes)
print(command)

# Execute the command
os.system(command)
