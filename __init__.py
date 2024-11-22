import os
import boto3
from flask import Flask, render_template, flash, redirect, url_for, request
from flaskr.util.helpers import upload_file_to_s3

ALLOWED_EXTENSIONS = {'mp4', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=['GET', 'POST'])
    def hello():
        return render_template('index.html')

    # Define the '/upload' route inside the app context
    @app.route('/upload', methods=['POST'])
    def create():
        if 'user_file' not in request.files:
            flash('No user_file key in request.files')
            return None

        file = request.files['user_file']

        if file.filename == '':
            flash('No selected title')
            return "Gagal"

        if file and allowed_file(file.filename):
            output = upload_file_to_s3(file)

            if output:
                flash("Success upload")
                return "Sukses"
            else:
                flash("Unable to upload")
                return "Gagal"
        else:
            flash("Extension not accepted")
            return "Gagal"

    return app
