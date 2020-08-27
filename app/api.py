
from app import app
from flask import request, jsonify, session, make_response
from flask_restful import abort, Resource
from functools import wraps
import json
import base64
import os
import time
import time
import datetime
import cv2
import numpy as np

from yolov5 import Yolov5

max_per_class_dict = {'gold_mine': 7, 
                      'elx_mine': 7,
                      'dark_mine': 3, 
                      'th': 1, 
                      'eagle': 1, 
                      'air_def': 4, 
                      'inferno': 3, 
                      'xbow': 4, 
                      'wiz_tower': 5, 
                      'bomb_tower': 2, 
                      'air_sweeper': 2, 
                      'cannon': 7, 
                      'mortar': 4, 
                      'archer_tower': 8, 
                      'queen': 1, 
                      'king': 1, 
                      'warden': 1, 
                      'gold_storage': 4, 
                      'elx_storage': 4, 
                      'dark_storage': 1, 
                      'cc': 1,
                      'scatter':2,
                      'champ':1}

clash_colors = [[255,255,255],
                [240,163,255],
                [0,117,220],
                [153,63,0],
                [76,0,92],
                [25,25,25],
                [0,92,49],
                [43,206,72],
                [255,204,153],
                [128,128,128],
                [148,255,181],
                [143,124,0],
                [157,204,0],
                [194,0,136],
                [0,51,128],
                [255,164,5],
                [255,168,187],
                [66,102,0],
                [255,0,16],
                [94,241,242],
                [0,153,143],
                [116,10,255],
                [153,0,0],
                [255,255,0]]

yolov5 = Yolov5('clash_weights/best.pt', device='0', conf_thres=0.5, colors=clash_colors)

class UPLOAD(Resource):
    def get(self):
        return 'hello'
    def post(self):
        auth_key = request.headers.get('clash-api-key')

        if auth_key == 'xxxxxxxxxxddddddddddtttttttttt12345': 
            content = request.get_json()
            if "encoded_string" in content.keys() and len(content.keys()) == 1:
                try:
                    encoded_string = content["encoded_string"]

                    image_bytes = base64.b64decode(str(encoded_string))
                    img_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)

                    detections = yolov5.predict(img_np, max_objects=max_per_class_dict)

                    return make_response(jsonify({"img_objects": detections}), 200)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({"message": "ERROR: Can't process data"}), 422)
            else:
                return make_response(jsonify({"message": "ERROR: Invalid POST request"}), 400)

        else:
            return make_response(jsonify({"message": "Unauthorized"}), 401)
        