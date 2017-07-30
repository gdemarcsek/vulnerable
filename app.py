#!/usr/bin/python
import os
import time
from hashlib import sha1
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import subprocess

app = Flask(__name__)

base_dir = os.path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = base_dir + '/uploads/'
app.config['RESULT_FOLDER'] = base_dir + '/converted/'
app.config['ALLOWED_EXTENSIONS'] = set(['mp4', 'avi', 'vmw', 'mkv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    scale_param = request.form['scale']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	output_file_path = os.path.join(app.config['RESULT_FOLDER'], sha1("%s_%s" % (filename, time.time())).hexdigest())
	file.save(input_file_path)
	# we will also do this with a vulnerable ffmpeg version...
	output_file_path += ".mp4"
        command = ["ffmpeg", "-i", input_file_path, "-vf", "scale=%s" % scale_param, "-strict", "-2", "-y", output_file_path]
	print(" ".join(command))
	ffmpeg_result = subprocess.call(command)
	if ffmpeg_result == 0:
		return redirect(url_for('uploaded_file', filename=os.path.basename(output_file_path)))
	else:
		return "Conversion failed", 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8080"),
        debug=True,
	threaded=True
    )

