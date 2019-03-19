import os, sys, numpy as np, cv2 as cv, torch, pyrealsense2 as rs
import _init_paths
from lib.network import PoseNet, PoseRefineNet
from lib.transformations import euler_matrix, quaternion_matrix, quaternion_from_matrix

WIDTH, HEIGHT = 640, 480

# Gets bounding box
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

# Sets up camera params and starts streaming
def setupRS():
	# Creates pipeline
	pipeline = rs.pipeline()

	# Configs the camera params and enables streams
	config = rs.config()
	config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, 30)
	config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.rgb8, 30)

	# Align object
	align_to = rs.stream.color 
	align = rs.align(align_to)

	# Starts streaming and returns objects
	pipeline.start(config)
	return (pipeline, align)

# Runs inference on the frames
def streamImgs(pipeline, align):
	flag = True
	while flag:
		try:
			# Pulls aligned frames from stream
			frames = pipeline.wait_for_frames()
			aframes = align.process(frames)
			dframe = np.asanyarray(aframes.get_depth_frame().get_data())
			cframe = np.asanyarray(aframes.get_color_frame().get_data())

			# Runs inference on rgbd
			pose = runInf(dframe, cframe)

		except:
			print('\nStreaming Stopped')
			flag = False
			pipeline.stop()

# Runs inference on image
def runInf(dframe, cframe):
	pass

if __name__ == '__main__':
	# Test Camera setup
	pipeline, align = setupRS()
	streamImgs(pipeline, align)
	