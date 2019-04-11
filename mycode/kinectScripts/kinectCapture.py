import freenect, cv2, numpy as np, frame_convert2 as fc2 

def get_depth():
	return fc2.pretty_depth_cv(freenect.sync_get_depth()[0])
	# return freenect.sync_get_depth()[0]

def get_bgr():
	return fc2.video_cv(freenect.sync_get_video()[0])

if __name__ == '__main__':
	# Testing
	count = 1

	# Takes count pics
	while count > 0:
		print('count =', count)

		depthImg = get_depth()
		print('DEBUG')
		# colorImg = get_bgr()

		cv2.imshow('Depth', get_depth())
		if cv2.waitKey(0) == 27:
			cv2.destroyAllWindows()

		# cv2.imwrite('depth-{}.png'.format(count), depthImg)
		# print(depthImg[100:150, 100:150])
		# print(depthImg.max())

		count -= 1