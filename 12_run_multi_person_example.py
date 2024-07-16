'''
Install the matching extension first:
cd library/pymatch
python3 setup.py develop
'''


cmd = 'python3 apps/demo/mocap.py data/examples/mirror-youtube-clip --work mirror --fps 30 --vis_scale 0.5'
run_cmd(cmd)