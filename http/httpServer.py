import os, sys, flask, werkzeug as wz

DOMAIN = 'http://home.sawyer0.com:666'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'])
UPLOAD_FOLDER = 'uploads'
app = flask.Flask(__name__)

def allowedFile(fname):
	if fname[-3:].lower() in ALLOWED_EXTENSIONS or fname[-4:].lower() in ALLOWED_EXTENSIONS:
		return True
	else:
		return False

def main(port, upPath, domain=None):
	global UPLOAD_FOLDER, app, DOMAIN
	if domain:
		DOMAIN = DOMAIN.split(':')[0] + ':' + str(port)
	UPLOAD_FOLDER = upPath
	app.config['UPLOAD_FOLDER'] = upPath
	app.run(port=port, host='0.0.0.0', debug=True)
	# app.run(port=port, host='0.0.0.0')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if flask.request.method == 'POST':
		file = flask.request.files['file']
		if file and allowedFile(file.filename):
			print('**found file: {}'.format(file.filename))
			fname = wz.secure_filename(file.filename)
			fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
			file.save(fpath)

			
			retUrl = flask.url_for('uploaded_file', filename=fname)
			retUrl = os.path.join(DOMAIN, *retUrl.split(os.sep))
			print(retUrl)
			
			# Run inference on file
			inf = None
			# Save inference as file, edit retUrl

			return retUrl

	return None

@app.route('/{}/<filename>'.format(UPLOAD_FOLDER))
def uploaded_file(filename):
	return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
	port = int(sys.argv[1])
	upPath = sys.argv[2]

	main(port, upPath)