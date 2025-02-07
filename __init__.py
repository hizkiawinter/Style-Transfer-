import os
import requests
import json 
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flaskr.util.helpers import upload_file_to_s3, get_file, show_image, show_video


ALLOWED_EXTENSIONS = {'mp4', 'txt', 'jpg', 'png'}
api_key = "rpa_7T3TQZWAL1HRKBWECWSD0FJ6ZL8453OSAD6KWNOI1sxsyz"
endpoint_url = "https://api.runpod.ai/v2/vz67ieid7rzwxb/runsync"

headers = {
    "Authorization" : f"Bearer {api_key}",
    "Content-Type": "application/json"
}

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

    @app.route('/index')
    def index():
        return render_template('index.html')
    
    @app.route('/upload')
    def upload():
        return render_template('upload.html')

    @app.route('/', methods=['GET', 'POST'])
    def hello():
        return render_template('landing_page.html')
        # return render_template('index.html', result = result, result_video = result_video)


    # # Define the '/upload' route inside the app context
    # @app.route('/upload', methods=['POST'])
    # def create():
    #     if 'user_file' not in request.files:
    #         flash('No user_file key in request.files')

    #     file = request.files['user_file']
    #     data = {
    #           "input": {
    #               "workflow": {
    #               "10": {
    #                   "inputs": {
    #                     "video": f"https://runpod-hizkia-fileupload.s3.ap-southeast-1.amazonaws.com/{file.filename}",
    #                     "force_rate": 0,
    #                     "force_size": "Disabled",
    #                     "custom_width": 512,
    #                     "custom_height": 512,
    #                     "frame_load_cap": 0,
    #                     "skip_first_frames": 0,
    #                     "select_every_nth": 1
    #                   },
    #                   "class_type": "VHS_LoadVideoPath",
    #                   "_meta": {
    #                     "title": "Load Video (Path) 🎥🅥🅗🅢"
    #                   }
    #                 },
    #                 "12": {
    #                   "inputs": {
    #                     "a": 6.283185307179586,
    #                     "bg_threshold": 0.1,
    #                     "resolution": 512,
    #                     "image": [
    #                       "10",
    #                       0
    #                     ]
    #                   },
    #                   "class_type": "MiDaS-DepthMapPreprocessor",
    #                   "_meta": {
    #                     "title": "MiDaS Depth Map"
    #                   }
    #                 },
    #                 "14": {
    #                   "inputs": {
    #                     "filename_prefix": "ControlNet",
    #                     "images": [
    #                       "12",
    #                       0
    #                     ]
    #                   },
    #                   "class_type": "SaveImageS3",
    #                   "_meta": {
    #                     "title": "Save Image to S3"
    #                   }
    #                 }
    #               }
    #           }
    #       }

    #     if file.filename == '':
    #         flash('No selected title')
    #         return "Tidak ada namafile"

    #     if file and allowed_file(file.filename):
    #         output = upload_file_to_s3(file)

    #         if output:
    #             flash("Success upload")
    #             response = requests.post(endpoint_url, headers=headers, data=json.dumps(data))
    #             if(response.status_code == 200):
    #                 print("Request Successful: ", response.json())
    #                 read_file = get_file(); 
    #                 return render_template('upload_success.html', response_data = response.json(), read_file = read_file)
    #             else:
    #                 print(f"Request failed with status code {response.status_code} : {response}")
    #         else:
    #             flash("Unable to upload")
    #             return "Gagal upload"
    #     else:
    #         flash("Extension not accepted")
    #         return "Ekstensi tidak didukung"

    return app
