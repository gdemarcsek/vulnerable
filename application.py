# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os
import time
from hashlib import sha1
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import subprocess
import boto3

try:
    import apparmor_light as aalight
except (ImportError, OSError) as error:
    if os.getenv("ENVIRONMENT", "production") == "production":
        raise error

app = Flask(__name__)

base_dir = os.path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = base_dir + '/uploads/'
app.config['RESULT_FOLDER'] = base_dir + '/converted/'
app.config['ALLOWED_EXTENSIONS'] = set(['mp4', 'avi', 'vmw', 'mkv'])
s3_client = None

def load_config():
    app.config.from_pyfile(os.path.join(base_dir, 'config.prod.cfg'))

def create_s3_client():
    global s3_client
    s3_client = boto3.client("s3", region_name="eu-west-2", aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'], aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

def upload_file_to_s3(file_object, target_path):
    return s3_client.put_object(ACL='public-read', Body=file_object, Bucket=app.config['S3_BUCKET_NAME'], Key=target_path)

@app.before_first_request
def app_setup():
    print("[*] AppArmor setup...")
    aa = aalight.apparmor()
    print("[*] Loading config...")
    load_config()
    print("[*] Creating S3 client...")
    create_s3_client()
    try:
        aa.change_profile("serve_user_requests")
    except OSError as error:
        if os.getenv("ENVIRONMENT", "production") == "production":
            raise error

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
        output_file_path = os.path.join(app.config['RESULT_FOLDER'],
                                        sha1("%s_%s" % (filename, time.time())).hexdigest())
        file.save(input_file_path)
        # we will also do this with a vulnerable ffmpeg version...
        output_file_path += ".mp4"
        command = ["ffmpeg", "-i", input_file_path, "-vf", "scale=%s" % scale_param, "-strict", "-2", "-y",
                   output_file_path]
        ffmpeg_result = subprocess.call(command)
        if ffmpeg_result == 0:
            upload_file_to_s3(open(output_file_path), os.path.basename(output_file_path))
            os.remove(output_file_path)
            return redirect(url_for('uploaded_file', filename=os.path.basename(output_file_path)))
        else:
            return "Conversion failed", 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    bucket_location = s3_client.get_bucket_location(Bucket=app.config['S3_BUCKET_NAME'])
    object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'], app.config['S3_BUCKET_NAME'], filename)
    return redirect(object_url)
