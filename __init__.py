import os
import requests
import boto3
import base64
import json 
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flaskr.util.helpers import upload_file_to_s3

ALLOWED_EXTENSIONS = {'mp4', 'txt', 'jpg', 'png'}
api_key = "[runpod_api_key]"
endpoint_url = "https://api.runpod.ai/v2/vz67ieid7rzwxb/runsync"

headers = {
    "Authorization" : f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
     "input": {
        "workflow": {
              "165": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "172",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "172": {
    "inputs": {
      "detect_hand": "enable",
      "detect_body": "enable",
      "detect_face": "enable",
      "resolution": 512,
      "bbox_detector": "yolox_l.onnx",
      "pose_estimator": "dw-ll_ucoco_384_bs5.torchscript.pt",
      "scale_stick_for_xinsr_cn": "disable",
      "image": [
        "177",
        0
      ]
    },
    "class_type": "DWPreprocessor",
    "_meta": {
      "title": "DWPose Estimator"
    }
  },
  "177": {
    "inputs": {
      "video": "https://runpod-hizkia-fileupload.s3.ap-southeast-1.amazonaws.com/htpsfb1r3bwa1.png",
      "force_rate": 0,
      "force_size": "Disabled",
      "custom_width": 512,
      "custom_height": 512,
      "frame_load_cap": 0,
      "skip_first_frames": 0,
      "select_every_nth": 1
    },
    "class_type": "VHS_LoadVideoPath",
    "_meta": {
      "title": "Load Video (Path) 🎥🅥🅗🅢"
    }
  }
        }
    }
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
                response = requests.post(endpoint_url, headers=headers, data=json.dumps(data))
                if(response.status_code == 200):
                    print("Request Successful: ", response.json())
                else:
                    print(f"Request failed with status code {response.status_code} : {response}")
                return render_template('upload_success.html', response_data = response.json())
            else:
                flash("Unable to upload")
                return "Gagal upload"
        else:
            flash("Extension not accepted")
            return "Ekstensi tidak didukung"

    return app
