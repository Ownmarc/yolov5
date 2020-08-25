
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

yolov5 = Yolov5('clash_weights/best.pt', device='0', conf_thres=0.5)

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

                    return jsonify({"img_objects": detections}), 200
                except Exception as e:
                    print(e)
                    return jsonify({"message": "ERROR: Can't process data"}), 422
            else:
                return jsonify({"message": "ERROR: Invalid POST request"}), 400

        else:
                return jsonify({"message": "Unauthorized"}), 401
        