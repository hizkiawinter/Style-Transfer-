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
log_url = "https://api.runpod.ai/v2/fa4ibxru565wt3/status/"
endpoint_url = "https://api.runpod.ai/v2/fa4ibxru565wt3/run"
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

    log_url = "https://api.runpod.ai/v2/fa4ibxru565wt3/status/"

    while True:
        try:
            url = log_url + proc_id
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                current_log = response.text
                if current_log != prev_log:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    emit("log_update", {
                        "timestamp": dt_string, 
                        "message": response.text
                    }, room=sid)
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
"2": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "samples": [
        "289",
        0
      ],
      "vae": [
        "2",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "53": {
    "inputs": {
      "upscale_method": "nearest-exact",
      "width": 1024,
      "height": 576,
      "crop": "center",
      "image": [
        "367",
        0
      ]
    },
    "class_type": "ImageScale",
    "_meta": {
      "title": "Upscale Image"
    }
  },
  "56": {
    "inputs": {
      "pixels": [
        "53",
        0
      ],
      "vae": [
        "2",
        0
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "70": {
    "inputs": {
      "control_net_name": "xinsir-controlnet-scribble.safetensors"
    },
    "class_type": "ControlNetLoaderAdvanced",
    "_meta": {
      "title": "Load Advanced ControlNet Model 🛂🅐🅒🅝"
    }
  },
  "110": {
    "inputs": {
      "ckpt_name": "juggernautXL_juggXIByRundiffusion.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "127": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "masterpiece, flat color, 1girl, blonde hair, simple background, looking at viewer, smile, white shirt, pink shirt, anime style, blue eyes",
      "text_l": "masterpiece, flat color, 1girl, blonde hair, simple background, looking at viewer, smile, white shirt, pink shirt, anime style, blue eyes",
      "clip": [
        "110",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "CLIPTextEncodeSDXL"
    }
  },
  "128": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "(worst quality, low quality:1)",
      "text_l": "(worst quality, low quality:1)",
      "clip": [
        "110",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "CLIPTextEncodeSDXL"
    }
  },
  "164": {
    "inputs": {
      "images": [
        "427",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "249": {
    "inputs": {
      "beta_schedule": "linear (HotshotXL/default)",
      "model": [
        "110",
        0
      ],
      "m_models": [
        "250",
        0
      ],
      "context_options": [
        "425",
        0
      ],
      "sample_settings": [
        "422",
        0
      ]
    },
    "class_type": "ADE_UseEvolvedSampling",
    "_meta": {
      "title": "Use Evolved Sampling 🎭🅐🅓②"
    }
  },
  "250": {
    "inputs": {
      "start_percent": 0,
      "end_percent": 1,
      "motion_model": [
        "304",
        0
      ]
    },
    "class_type": "ADE_ApplyAnimateDiffModel",
    "_meta": {
      "title": "Apply AnimateDiff Model (Adv.) 🎭🅐🅓②"
    }
  },
  "252": {
    "inputs": {
      "add_noise": True,
      "noise_seed": 0,
      "cfg": 2,
      "model": [
        "249",
        0
      ],
      "positive": [
        "127",
        0
      ],
      "negative": [
        "128",
        0
      ],
      "sampler": [
        "255",
        0
      ],
      "sigmas": [
        "258",
        0
      ],
      "latent_image": [
        "56",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "255": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "258": {
    "inputs": {
      "sigmas": [
        "375",
        0
      ]
    },
    "class_type": "FlipSigmas",
    "_meta": {
      "title": "FlipSigmas"
    }
  },
  "280": {
    "inputs": {
      "beta_schedule": "linear (HotshotXL/default)",
      "model": [
        "110",
        0
      ],
      "m_models": [
        "371",
        0
      ],
      "context_options": [
        "425",
        0
      ],
      "sample_settings": [
        "414",
        0
      ]
    },
    "class_type": "ADE_UseEvolvedSampling",
    "_meta": {
      "title": "Use Evolved Sampling 🎭🅐🅓②"
    }
  },
  "289": {
    "inputs": {
      "add_noise": False,
      "noise_seed": 0,
      "cfg": 5,
      "model": [
        "280",
        0
      ],
      "positive": [
        "396",
        0
      ],
      "negative": [
        "396",
        1
      ],
      "sampler": [
        "255",
        0
      ],
      "sigmas": [
        "375",
        0
      ],
      "latent_image": [
        "252",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "296": {
    "inputs": {
      "images": [
        "53",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "304": {
    "inputs": {
      "model_name": "hotshotxl_mm_v1.pth"
    },
    "class_type": "ADE_LoadAnimateDiffModel",
    "_meta": {
      "title": "Load AnimateDiff Model 🎭🅐🅓②"
    }
  },
  "312": {
    "inputs": {
      "samples": [
        "252",
        0
      ],
      "vae": [
        "2",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "313": {
    "inputs": {
      "images": [
        "312",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "367": {
    "inputs": {
      "video": "https://runpod-hizkia-fileupload.s3.ap-southeast-1.amazonaws.com/Input/Video_1wIobgDU2n94AqzQ.mp4",
      "force_rate": 0,
      "force_size": "Disabled",
      "custom_width": 512,
      "custom_height": 512,
      "frame_load_cap": 0,
      "skip_first_frames": 0,
      "select_every_nth": 2
    },
    "class_type": "VHS_LoadVideoPath",
    "_meta": {
      "title": "Load Video (Path) 🎥🅥🅗🅢"
    }
  },
  "371": {
    "inputs": {
      "start_percent": 0,
      "end_percent": 1,
      "motion_model": [
        "304",
        0
      ]
    },
    "class_type": "ADE_ApplyAnimateDiffModel",
    "_meta": {
      "title": "Apply AnimateDiff Model (Adv.) 🎭🅐🅓②"
    }
  },
  "375": {
    "inputs": {
      "model_type": "SDXL",
      "steps": 16,
      "denoise": 1
    },
    "class_type": "AlignYourStepsScheduler",
    "_meta": {
      "title": "AlignYourStepsScheduler"
    }
  },
  "396": {
    "inputs": {
      "strength": 0.4,
      "start_percent": 0,
      "end_percent": 0.4,
      "positive": [
        "127",
        0
      ],
      "negative": [
        "128",
        0
      ],
      "control_net": [
        "70",
        0
      ],
      "image": [
        "427",
        0
      ]
    },
    "class_type": "ACN_AdvancedControlNetApply",
    "_meta": {
      "title": "Apply Advanced ControlNet 🛂🅐🅒🅝"
    }
  },
  "414": {
    "inputs": {
      "batch_offset": 0,
      "noise_type": "empty",
      "seed_gen": "comfy",
      "seed_offset": 0,
      "adapt_denoise_steps": False
    },
    "class_type": "ADE_AnimateDiffSamplingSettings",
    "_meta": {
      "title": "Sample Settings 🎭🅐🅓"
    }
  },
  "422": {
    "inputs": {
      "batch_offset": 0,
      "noise_type": "empty",
      "seed_gen": "comfy",
      "seed_offset": 0,
      "adapt_denoise_steps": False
    },
    "class_type": "ADE_AnimateDiffSamplingSettings",
    "_meta": {
      "title": "Sample Settings 🎭🅐🅓"
    }
  },
  "425": {
    "inputs": {
      "context_length": 8,
      "context_stride": 1,
      "context_overlap": 2,
      "fuse_method": "pyramid",
      "use_on_equal_length": False,
      "start_percent": 0,
      "guarantee_steps": 1
    },
    "class_type": "ADE_StandardUniformContextOptions",
    "_meta": {
      "title": "Context Options◆Standard Uniform 🎭🅐🅓"
    }
  },
  "427": {
    "inputs": {
      "coarse": "disable",
      "resolution": 576,
      "image": [
        "53",
        0
      ]
    },
    "class_type": "LineArtPreprocessor",
    "_meta": {
      "title": "Realistic Lineart"
    }
  },
  "428": {
    "inputs": {
      "filename_prefix": "Image",
      "images": [
        "10",
        0
      ]
    },
    "class_type": "SaveImageS3",
    "_meta": {
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
