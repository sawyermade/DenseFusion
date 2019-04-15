import numpy as np, pyrealsense2 as rs, cv2

def pipeconfig(width, height):
	config = rs.config()
	config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
	config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
	return config

# Main for testing
if __name__ == '__main__':
	# Creates pipeline and config
	pipeline = rs.pipeline()
	config = pipeconfig(640, 480)
	profile = pipeline.start(config)

	# Gets depth and scale
	depth_sensor = profile.get_device().first_depth_sensor()
	depth_scale = depth_sensor.get_depth_scale()
	# print('scale = {}'.format(depth_scale))

	# Alignment
	align_to = rs.stream.color
	align = rs.align(align_to)

	# First few images are no good
	count = 10
	while count > 0:
		# Get frames
		frames = pipeline.wait_for_frames()
		aligned_frames = align.process(frames)

		# Get aligned frames
		depth_frame = aligned_frames.get_depth_frame()
		color_frame = aligned_frames.get_color_frame()

		count -= 1

	# Loops count times
	count = 5
	# while True:
	while count > 0:
		# Get frames
		frames = pipeline.wait_for_frames()
		aligned_frames = align.process(frames)

		# Get aligned frames
		depth_frame = aligned_frames.get_depth_frame()
		color_frame = aligned_frames.get_color_frame()

		# Checks if it got the depth and color frame
		if depth_frame and color_frame:
			# Creates np arrays of img
			depthImg = np.asanyarray(depth_frame.get_data())
			colorImg = np.asanyarray(color_frame.get_data())
			print(depthImg.max())

			bc = 0
			for x in depthImg.flatten():
				if x > 50000:
					bc += 1
			print(bc)

			# Wrties frames
			# depthImg3d = np.dstack((depthImg, depthImg, depthImg))
			# depthImg = cv2.applyColorMap(cv2.convertScaleAbs(depthImg3d, alpha=0.03), cv2.COLORMAP_JET)
			cv2.imwrite('{}-depth.png'.format(count), depthImg)
			cv2.imwrite('{}-color.png'.format(count), colorImg)

			# Views frames
			# d = np.dstack((d, d, d))
			# d = cv2.applyColorMap(cv2.convertScaleAbs(d, alpha=0.03), cv2.COLORMAP_JET)
			# images = np.hstack((c, d))
			# cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
			# cv2.imshow('Align Example', images)
			# key = cv2.waitKey(1)
			# # Press esc or 'q' to close the image window
			# if key & 0xFF == ord('q') or key == 27:
			# 	cv2.destroyAllWindows()
			# 	break

			# Decrements counter
			count -= 1