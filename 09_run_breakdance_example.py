
import os

# This is the breakdance video here: https://chingswy.github.io/easymocap-public-doc/quickstart/quickstart.html#demo-for-motion-capture

os.system(f'emc --data config/datasets/mvimage.yml --exp config/mv1p/detect_triangulate_fitSMPL.yml --root data/examples/street_dance --ranges 0 500 1 --subs_vis 07 01 05 03')

print('complete')