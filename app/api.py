
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
                    img_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)[:,:,:3]

                    detections = yolov5.predict(img_np, max_objects=max_per_class_dict)

                    return make_response(jsonify({"img_objects": detections}), 200)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({"message": "ERROR: Can't process data"}), 422)
            else:
                return make_response(jsonify({"message": "ERROR: Invalid POST request"}), 400)

        else:
            return make_response(jsonify({"message": "Unauthorized"}), 401)

class BURNTBASE(Resource):
    def post(self):
        auth_key = request.headers.get('clash-api-key')

        if auth_key == 'xxxxxxxxxxddddddddddtttttttttt12345':
            content = request.get_json()
            if "encoded_string" in content.keys() and len(content.keys()) == 1:
                try:
                    encoded_string = content["encoded_string"]

                    image_bytes = base64.b64decode(str(encoded_string))
                    img_from_buf = np.frombuffer(image_bytes, np.uint8)
                    img_np = cv2.imdecode(img_from_buf, 1)[:,:,:3]
                    #cv2.imwrite(f'F:/yolov5/data/burntbase/{time.time()}.jpg', img_np)
                    cv2.imwrite(f'/home/marcnano/clash_yolo/data/burntbase/{time.time()}.jpg', img_np)

                    print(img_np.shape)

                    detections = yolov5.predict(img_np, max_objects=max_per_class_dict)

                    height, width, _ = img_np.shape

                    resp = img_objects_to_formated_json(detections, width, height)

                    return make_response(jsonify(resp), 200)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({"message": "ERROR: Can't process data"}), 422)
            else:
                return make_response(jsonify({"message": "ERROR: Invalid POST request"}), 400)

        else:
            return make_response(jsonify({"message": "Unauthorized"}), 401)


def img_objects_to_formated_json(img_objects, img_width, img_height):
  
    xmin = 9999
    xmax = 0
    ymin = 9999
    ymax = 0
    
    objects = []

    th_level = None
    th_level_dict = {'eagle':0, 'inferno':0,
                'air_def':0, 'scatter':0, 'th':0,
                'wiz_tower': 0, 'xbow': 0, 'champ': 0,
                'warden': 0}

    for obj in img_objects:
        if obj['name'] in th_level_dict:
            th_level_dict[obj['name']] += 1

            if xmin > (obj['bndbox']['xmin'] + obj['bndbox']['xmax'])/2:
                xmin = (obj['bndbox']['xmin'] + obj['bndbox']['xmax'])/2
            if xmax < (obj['bndbox']['xmin'] + obj['bndbox']['xmax'])/2:
                xmax = (obj['bndbox']['xmin'] + obj['bndbox']['xmax'])/2
            if ymin > (obj['bndbox']['ymin'] + obj['bndbox']['ymax'])/2:
                ymin = (obj['bndbox']['ymin'] + obj['bndbox']['ymax'])/2
            if ymax < (obj['bndbox']['ymin'] + obj['bndbox']['ymax'])/2:
                ymax = (obj['bndbox']['ymin'] + obj['bndbox']['ymax'])/2
            

    if th_level_dict['scatter'] >= 1 or th_level_dict['champ'] == 1:
        th_level = 13
    elif th_level_dict['inferno'] >= 3:
        th_level = 12
    elif th_level_dict['eagle'] >= 1 or th_level_dict['warden'] >= 1:
        th_level = 11
    else:
        th_level = 10

    if th_level == None:
        print('Not able to infer th level of file ')
        print(th_level_dict)

    xcenter = (xmin + xmax) / 2
    ycenter = (ymin + ymax) / 2
    base_width = xmax - xmin
    base_height = ymax - ymin

    rel_base_width = base_width/img_width
    rel_base_height = base_height/img_height
    rel_starting_x = xmin/img_width
    rel_starting_y = ymin/img_height

    pos_dict = {}
    pos_dict['air_def'] = {}
    pos_dict['air_def']['positions'] = []
    pos_dict['eagle'] = {}
    pos_dict['eagle']['positions'] = []
    pos_dict['inferno'] = {}
    pos_dict['inferno']['positions'] = []
    pos_dict['scatter'] = {}
    pos_dict['scatter']['positions'] = []
    pos_dict['th'] = {}
    pos_dict['th']['positions'] = []
    pos_dict['wiz_tower'] = {}
    pos_dict['wiz_tower']['positions'] = []
    pos_dict['xbow'] = {}
    pos_dict['xbow']['positions'] = []

    for obj in img_objects:
        if obj['name'] in pos_dict:
            pos_dict[obj['name']]['positions'].append({
                "xPercent":round(((obj['bndbox']['xmin'] + obj['bndbox']['xmax'])/2-xmin)/base_width, 14),
                "yPercent":round(((obj['bndbox']['ymin'] + obj['bndbox']['ymax'])/2-ymin)/base_height, 14),
                "xMinPercent":round((obj['bndbox']['xmin']-xmin)/base_width, 14),
                "yMinPercent":round((obj['bndbox']['ymin']-ymin)/base_height, 14),
                "xMaxPercent":round((obj['bndbox']['xmax']-xmin)/base_width, 14),
                "yMaxPercent":round((obj['bndbox']['ymax']-ymin)/base_height, 14)
            })

    json_dict = {
        'th_level': th_level,
        'coord': {
            'ad':{
                "positions": pos_dict['air_def']['positions'],
                "buildingName": "Air Defense"
            },
            'ea':{
                "positions": pos_dict['eagle']['positions'],
                "buildingName": "Eagle Artillery"
            },
            'it':{
                "positions": pos_dict['inferno']['positions'],
                "buildingName": "Inferno Tower"
            },
            'ss':{
                "positions": pos_dict['scatter']['positions'],
                "buildingName": "Scattershot"
            },
            'th':{
                "positions": pos_dict['th']['positions'],
                "buildingName": "Townhall"
            },
            'wt':{
                "positions": pos_dict['wiz_tower']['positions'],
                "buildingName": "Wizard Tower"
            },
            'xb':{
                "positions": pos_dict['xbow']['positions'],
                "buildingName": "X-Bow"
            }
        },
        'matrix': {
            'size':{
                'width':rel_base_width,
                'height':rel_base_height
            },
            'startingPosition':{
                'x':rel_starting_x,
                'y':rel_starting_y
            }
        }
    }

    return json_dict
        