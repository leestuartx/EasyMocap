
import os

# This is the Fit MANO to Monocular Videos: https://chingswy.github.io/easymocap-public-doc/quickstart/quickstart.html#demo-on-monocularmirror-videos

os.system(f'emc --data config/datasets/svimage.yml --exp config/1v1p/hand_detect_finetune.yml --root data/examples/hand --ranges 0 1800 1 --subs video')
print('complete')