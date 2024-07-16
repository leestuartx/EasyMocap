
import os

# This is the monocular video demo of the ice skater found here: https://chingswy.github.io/easymocap-public-doc/quickstart/quickstart.html#demo-on-monocularmirror-videos
# To get this to run the images have to be moved directly into the images directory (because I modified some code)
os.system(f'emc --data config/datasets/svimage.yml --exp config/1v1p/hrnet_pare_finetune.yml --root data/examples/internet-rotate --ranges 0 500 1 --subs 23EfsN7vEOA+003170+003670')
print('complete')