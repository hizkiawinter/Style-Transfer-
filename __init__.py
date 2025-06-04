import os
import requests
import json 
import random
import string 
from celery import Celery
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
from flaskr.util.helpers import upload_file_to_s3, get_file, show_image, show_video, show_canny, show_depth, show_pose, show_videoresult


ALLOWED_EXTENSIONS = {'mp4', 'txt', 'jpg', 'png'}
api_key = "rpa_7T3TQZWAL1HRKBWECWSD0FJ6ZL8453OSAD6KWNOI1sxsyz"
endpoint_url = "https://api.runpod.ai/v2/vz67ieid7rzwxb/runsync"

headers = {
    "Authorization" : f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def rand_string(): 
    length = 16
    random_string = ''. join(random.choices(string.ascii_letters + string.digits, k=length))

    return random_string

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def celery_init_app(app: Flask) -> Celery: 
    class FlaskTask: 
        def __call__(self, *args: object, **kwargs: object) -> object: 
            with app.app_context(): 
                return self.run(*args, **kwargs)
    celery_app = Celery(app.name, task_cls = FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app 
    return celery_app


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
        return render_template('request.html')
    
    @app.route('/upload')
    def upload():
        return render_template('upload.html')

    @app.route('/', methods=['GET', 'POST'])
    def hello():
        return render_template('upload.html')
        # return render_template('index.html', result = result, result_video = result_video)
    
    @app.route('/response', methods=['GET'])
    def response(): 
        presigned_video = show_video()
        presigned_image = show_image()
        presigned_depth = show_depth() 
        presigned_canny = show_canny()
        presigned_pose = show_pose() 
        presigned_videoresult = show_videoresult()
        return render_template('response.html', presigned_video = presigned_video, presigned_image = presigned_image, presigned_canny = presigned_canny, presigned_depth = presigned_depth, presigned_pose = presigned_pose, presigned_videoresult = presigned_videoresult)

    @app.route('/video')
    def video_result():
        file_key = session.get('uploaded_key')
        if not file_key:
            return "No video uploaded recently."
        
        presigned_video = show_video(file_key)
        return render_template('videoUpload.html', presigned_video=presigned_video)
    # # Define the '/upload' route inside the app context
    @app.route('/run', methods=['POST'])
    def run():
        if 'user_file' not in request.files:
            flash('No user_file key in request.files')
        
        
        file = request.files['user_file'] 

        if file.filename == '':
            flash('No selected title')
            return "Tidak ada namafile"
        
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1].lower() 
            new_filename = "Video_" + rand_string() + ext
            file_key = f"Input/{new_filename}"
            output = upload_file_to_s3(file, new_filename)

            if output:
                flash("Success upload")
                session['uploaded_key'] = file_key
                return redirect(url_for('video_result'))
        #         response = requests.post(endpoint_url, headers=headers, data=json.dumps(data))
        #         if(response.status_code == 200):
        #             print("Request Successful: ", response.json())
        #             read_file = get_file(); 
        #             return render_template('videoUpload.html', response_data = response.json(), read_file = read_file)
        #         else:
        #             print(f"Request failed with status code {response.status_code} : {response}")
        #     else:
        #         flash("Unable to upload")
        #         return "Gagal upload"
        # else:
        #     flash("Extension not accepted")
        #     return "Ekstensi tidak didukung"

      
      

        # file = request.files['user_file']
        # prefix = rand_string()
        # data = {
        #       "input": {
        #           "workflow": {
        #           "10": {
        #               "inputs": {
        #                 "video": f"https://runpod-hizkia-fileupload.s3.ap-southeast-1.amazonaws.com/{file.filename}",
        #                 "force_rate": 0,
        #                 "force_size": "Disabled",
        #                 "custom_width": 512,
        #                 "custom_height": 512,
        #                 "frame_load_cap": 0,
        #                 "skip_first_frames": 0,
        #                 "select_every_nth": 1
        #               },
        #               "class_type": "VHS_LoadVideoPath",
        #               "_meta": {
        #                 "title": "Load Video (Path) 🎥🅥🅗🅢"
        #               }
        #             },
        #             "12": {
        #               "inputs": {
        #                 "a": 6.283185307179586,
        #                 "bg_threshold": 0.1,
        #                 "resolution": 512,
        #                 "image": [
        #                   "10",
        #                   0
        #                 ]
        #               },
        #               "class_type": "MiDaS-DepthMapPreprocessor",
        #               "_meta": {
        #                 "title": "MiDaS Depth Map"
        #               }
        #             },
        #             "14": {
        #               "inputs": {
        #                 "filename_prefix": f"{prefix}",
        #                 "images": [
        #                   "12",
        #                   0
        #                 ]
        #               },
        #               "class_type": "SaveImageS3",
        #               "_meta": {
        #                 "title": "Save Image to S3"
        #               }
        #             }
        #           }
        #       }
        #   }

        # 

        

    return app
