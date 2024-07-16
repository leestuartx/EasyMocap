from easymocap.mytools.debug_utils import run_cmd


# This is the mirror dance video found here: https://chingswy.github.io/easymocap-public-doc/quickstart/quickstart.html#demo-for-motion-capture
cmd = 'python3 apps/demo/mocap.py data/examples/mirror-youtube-clip --work mirror --fps 30 --vis_scale 0.5'
run_cmd(cmd)