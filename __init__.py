import os
import requests
import json 
import random
import string 
import time
import subprocess
from flask_socketio import SocketIO, emit
from datetime import date, datetime 
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
from flaskr.util.helpers import upload_file_to_s3, get_file, show_image, show_video, show_canny, show_depth, show_pose, show_videoresult


ALLOWED_EXTENSIONS = {'mp4', 'txt', 'jpg', 'png'}
api_key = "rpa_7T3TQZWAL1HRKBWECWSD0FJ6ZL8453OSAD6KWNOI1sxsyz"
log_url = "https://api.runpod.ai/v2/vz67ieid7rzwxb/status/"
endpoint_url = "https://api.runpod.ai/v2/vz67ieid7rzwxb/run"
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
socketio = SocketIO()


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

@socketio.on("my_event")
def checklog(data):  # receive data from client
    sid = request.sid
    prev_log = ""
    # Get proc_id from event data, NOT from session (unless you handle sessions on websocket)
    proc_id = data.get("proc_id")
    if not proc_id:
        emit("log_update", {"data": "Please give your prompt to start the style transfer process"}, room=sid)
        return

    log_url = "https://api.runpod.ai/v2/vz67ieid7rzwxb/status/"

    while True:
        try:
            url = log_url + proc_id
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                current_log = response.text
                if current_log != prev_log:
                    emit("log_update", {"data": response.text}, room=sid)
                    prev_log = current_log

                # Example: stop loop if job is finished
                status = response.json().get("status", "")
                if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                    break

            else:
                emit("log_update", {"data": f"Error: {response.status_code}"}, room=sid)

            socketio.sleep(3)

        except Exception as e:
            emit("log_update", {"data": f"Exception: {str(e)}"}, room=sid)
            break



def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    socketio.init_app(app)
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
        file_key = session.get('file_key')
        if not file_key:
            return "No video uploaded recently."
        
        presigned_video = show_video(file_key)
        return render_template('videoUpload.html', presigned_video=presigned_video)
    
    @app.route('/runPrompt', methods=['POST'])
    def runPrompt(): 
        data = request.form
        file_key = session.get('file_key')
        unique_string = session.get('unique_string')

        # promptPositive = data['promptPositive'],
        # promptNegative = data['promptNegative'],
        # video_input= file_key,
        # unique_string = unique_string

        payload = {
                "input":
                {
                    "workflow":
                    {
                        "34":
                        {
                            "inputs":
                            {
                                "video": f"https://runpod-hizkia-fileupload.s3.ap-southeast-1.amazonaws.com/{file_key}",
                                "force_rate": 0,
                                "force_size": "Disabled",
                                "custom_width": 512,
                                "custom_height": 512,
                                "frame_load_cap": 0,
                                "skip_first_frames": 0,
                                "select_every_nth": 1
                            },
                            "class_type": "VHS_LoadVideoPath",
                            "_meta":
                            {
                                "title": "Load Video (Path) 🎥🅥🅗🅢"
                            }
                        },
                        "35":
                        {
                            "inputs":
                            {
                                "a": 6.283185307179586,
                                "bg_threshold": 0.1,
                                "resolution": 512,
                                "image": [
                                    "34",
                                    0
                                ]
                            },
                            "class_type": "MiDaS-DepthMapPreprocessor",
                            "_meta":
                            {
                                "title": "MiDaS Depth Map"
                            }
                        },
                        "36":
                        {
                            "inputs":
                            {
                                "filename_prefix": "test",
                                "images": [
                                    "35",
                                    0
                                ]
                            },
                            "class_type": "SaveImageS3",
                            "_meta":
                            {
                                "title": "Save Image to S3"
                            }
                        }
                    }
                }
            }
        
        try:
            response = requests.post(endpoint_url, headers=headers, json=payload)
            proc_info = response.json()
            proc_id = proc_info.get("id")
            return redirect(url_for('video_result', proc_id = proc_id))
            
        except Exception as e:  
            return jsonify({"error": str(e)}), 500  

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
            unique_string = rand_string() 
            new_filename = "Video_" + unique_string + ext
            file_key = f"Input/{new_filename}"

            output = upload_file_to_s3(file, new_filename)

            if output:
                flash("Success upload")
                session['unique_string'] = unique_string
                session['file_key'] = file_key
                return redirect(url_for('video_result'))
        


    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app)
