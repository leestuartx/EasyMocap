import pickle
import numpy as np

# Load the GMM file with Python 3.x compatibility
def load_gmm(file_path):
    with open(file_path, 'rb') as f:
        gmm = pickle.load(f, encoding='latin1')
    return gmm

# Save the GMM file in Python 3.x format
def save_gmm(gmm, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(gmm, f, protocol=pickle.HIGHEST_PROTOCOL)

# Path to the original and new GMM files
original_gmm_path = 'H:\\AI\\EasyMocap\\easymocap\\multistage\\gmm_08.pkl'
new_gmm_path = 'H:\\AI\\EasyMocap\\easymocap\\multistage\\gmm_08.pkl'

# Load and re-save the GMM file
gmm = load_gmm(original_gmm_path)
save_gmm(gmm, new_gmm_path)
