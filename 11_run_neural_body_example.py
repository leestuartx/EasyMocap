from easymocap.mytools.debug_utils import run_cmd


# This is the mirror dance video found here: https://chingswy.github.io/easymocap-public-doc/quickstart/quickstart.html#demo-for-motion-capture

print('Train NeuralBody')
cmd = 'python3 apps/neuralbody/demo.py data/examples/neuralbody --mode neuralbody --gpus 0'
run_cmd(cmd)

print('Render NeuralBody')
cmd = 'python3 apps/neuralbody/demo.py data/examples/neuralbody --mode neuralbody --gpus 0, --demo'
run_cmd(cmd)

print('Full Step Motion Capture Preparation')
cmd = 'python3 apps/demo/mocap.py data/examples/neuralbody --work lightstage-dense-unsync --subs_vis 01 07 13 19 --disable_crop'
run_cmd(cmd)