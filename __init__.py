import os
import requests
import boto3
import base64
import json 
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flaskr.util.helpers import upload_file_to_s3

ALLOWED_EXTENSIONS = {'mp4', 'txt', 'jpg'}
api_key = "[API KEY RUNPOD]"
endpoint_id = "[ENDPOINT RUNPOD ID]"

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

        file = request.files['user_file']

        if file.filename == '':
            flash('No selected title')
            return "Tidak ada namafile"

        if file and allowed_file(file.filename):
            output = upload_file_to_s3(file)

            if output:
                flash("Success upload")
                url = "https://api.comfydeploy.com/api/sessions"
                headers = {
                    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8ycFcxMVZWNlZiN2xJQm1SZVpSRWx6VWtsRFQiLCJpYXQiOjE3MzMzNjk1MDh9.YMr6B7ISUEeVTkH5b8qcKGt94Vmb1bJiHdgJp0K4qdU",
                    'Content-Type': 'application/json'
                }
                res = requests.get(url, headers=headers)
                print(f"Response code : {res.status_code}")
                return render_template('upload_success.html')
            else:
                flash("Unable to upload")
                return "Gagal upload"
        else:
            flash("Extension not accepted")
            return "Ekstensi tidak didukung"

    return app
