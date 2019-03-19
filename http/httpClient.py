import sys, requests

if __name__ == '__main__':
	url = sys.argv[1]
	fpath = sys.argv[2]
	with open(fpath, 'rb') as f:
		files = {'file' : f}

		try:
			r = requests.post(url, files=files)
			print(r.text)

		except Exception as e:
			print('Did not send file: {}\nException:\n{}'.format(fpath, e))