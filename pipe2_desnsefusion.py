import os, sys, flask, werkzeug as wz, json
from zipfile import ZipFile
# from urllib.parse import urljoin
# DOMAIN = '127.0.0.1'
DOMAIN = 'home.sawyer0.com'
PORT = 665
FULLDOMAIN = 'http://{}:665'.format(DOMAIN)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'])
UPLOAD_FOLDER = 'uploads-pipe1'
UPLOAD_FOLDER_REL = '/uploads-pipe1/'

refiner = None

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"

sys.path.insert(0, os.getcwd())

# import _init_paths
import argparse
# import os
import copy
import random
import numpy as np
from PIL import Image
import scipy.io as scio
import scipy.misc
import numpy.ma as ma
import math
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
import torch.nn.functional as F
from torch.autograd import Variable
from datasets.ycb.dataset import PoseDataset
from lib.network import PoseNet, PoseRefineNet
from lib.transformations import euler_matrix, quaternion_matrix, quaternion_from_matrix

parser = argparse.ArgumentParser()
# parser.add_argument('--dataset_root', type=str, default = '', help='dataset root dir')
# parser.add_argument('--model', type=str, default = '',  help='resume PoseNet model')
parser.add_argument('-m', '--refine_model', type=str, default = '',  help='resume PoseRefineNet model')
opt = parser.parse_args()

norm = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
border_list = [-1, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400, 440, 480, 520, 560, 600, 640, 680]
xmap = np.array([[j for i in range(640)] for j in range(480)])
ymap = np.array([[i for i in range(640)] for j in range(480)])
cam_cx = 312.9869
cam_cy = 241.3109
cam_fx = 1066.778
cam_fy = 1067.487
cam_scale = 10000.0
num_obj = 21
img_width = 480
img_length = 640
num_points = 1000
num_points_mesh = 500
iteration = 2
bs = 1

def get_bbox(posecnn_rois):
    rmin = int(posecnn_rois[idx][3]) + 1
    rmax = int(posecnn_rois[idx][5]) - 1
    cmin = int(posecnn_rois[idx][2]) + 1
    cmax = int(posecnn_rois[idx][4]) - 1
    r_b = rmax - rmin
    for tt in range(len(border_list)):
        if r_b > border_list[tt] and r_b < border_list[tt + 1]:
            r_b = border_list[tt + 1]
            break
    c_b = cmax - cmin
    for tt in range(len(border_list)):
        if c_b > border_list[tt] and c_b < border_list[tt + 1]:
            c_b = border_list[tt + 1]
            break
    center = [int((rmin + rmax) / 2), int((cmin + cmax) / 2)]
    rmin = center[0] - int(r_b / 2)
    rmax = center[0] + int(r_b / 2)
    cmin = center[1] - int(c_b / 2)
    cmax = center[1] + int(c_b / 2)
    if rmin < 0:
        delt = -rmin
        rmin = 0
        rmax += delt
    if cmin < 0:
        delt = -cmin
        cmin = 0
        cmax += delt
    if rmax > img_width:
        delt = rmax - img_width
        rmax = img_width
        rmin -= delt
    if cmax > img_length:
        delt = cmax - img_length
        cmax = img_length
        cmin -= delt
    return rmin, rmax, cmin, cmax

@app.route('/{}/<filename>'.format(UPLOAD_FOLDER))
def uploaded_file(filename):
	return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	# global logger, model
	if flask.request.method == 'POST':
		file1 = flask.request.files['file1']
		file2 = flask.request.files['file2']
		if file1 and allowedFile(file1.filename) and file2 and allowedFile(file2.filename):
			# Gets filenames, paths, and saves them
			fname1 = wz.secure_filename(file1.filename)
			fpath1 = os.path.join(app.config['UPLOAD_FOLDER'], fname1)
			fname2 = wz.secure_filename(file2.filename)
			fpath2 = os.path.join(app.config['UPLOAD_FOLDER'], fname2)
			# print(fname1, fname2)
			file1.save(fpath1)
			file2.save(fpath2)

def main():
	# Globals
	global refiner

	# Setup upload folder and run server
	if not os.path.exists(UPLOAD_FOLDER):
		os.makedirs(UPLOAD_FOLDER)

	# Sets up network
	refiner = PoseRefineNet(num_points = num_points, num_obj = num_obj)
	refiner.cuda()
	refiner.load_state_dict(torch.load(opt.refine_model))
	refiner.eval()

	app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
	app.run(port=PORT, host='0.0.0.0', debug=False)

if __name__ == '__main__':
	main()