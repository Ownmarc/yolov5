
from app import app
from flask import request, jsonify, session, make_response
from flask_restful import abort, Resource
from functools import wraps
import json
import base64
import os
import time
import datetime
import cv2
import numpy as np

from yolov5 import Yolov5

try:
    with open("creds.json") as f:
        s3_creds = json.load(f)

    import boto3
    import youtube_dl
    from datetime import datetime
    from io import BytesIO
    import pandas as pd

    s3 = boto3.client('s3',
    aws_access_key_id=s3_creds["aws_access_key_id"],
    aws_secret_access_key=s3_creds["aws_secret_access_key"])

except FileNotFoundError:
    print('vidscan not running')
    

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

war_buildings_of_interest = ['th',
                      'eagle', 
                      'air_def',
                      'inferno' ,
                      'xbow',
                      'wiz_tower' ,
                      'air_sweeper',
                      'queen' ,
                      'king' ,
                      'warden' ,
                      'cc',
                      'scatter',
                      'champ']


any_buildings_of_interest = ['gold_mine',
                            'elx_mine',
                            'dark_mine',
                            'th',
                            'eagle',
                            'air_def',
                            'inferno',
                            'xbow',
                            'wiz_tower',
                            'bomb_tower',
                            'air_sweeper',
                            'cannon',
                            'mortar',
                            'archer_tower',
                            'queen',
                            'king',
                            'warden',
                            'gold_storage',
                            'elx_storage',
                            'dark_storage',
                            'cc',
                            'scatter',
                            'champ']

yolov5 = Yolov5('clash_weights/best.pt', img_size=800, device='0', conf_thres=0.7, colors=clash_colors)

class UPLOAD(Resource):
    def get(self):
        return 'hello'
    def post(self):
        auth_key = request.headers.get('clash-api-key')

        if auth_key == 'xxxxxxxxxxddddddddddtttttttttt12345' or "pyjHNAYVWY4484TqlGqLYGAyiUsYFWcX": 
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

        if auth_key == 'xxxxxxxxxxddddddddddtttttttttt12345' or "pyjHNAYVWY4484TqlGqLYGAyiUsYFWcX":
            content = request.get_json()
            if "encoded_string" in content.keys() and len(content.keys()) == 1:
                try:
                    encoded_string = content["encoded_string"]

                    image_bytes = base64.b64decode(str(encoded_string))
                    img_from_buf = np.frombuffer(image_bytes, np.uint8)
                    img_np = cv2.imdecode(img_from_buf, 1)[:,:,:3]
                    #cv2.imwrite(f'F:/yolov5/data/burntbase/{time.time()}.jpg', img_np)
                    #cv2.imwrite(f'/home/marcnano/clash_yolo/data/burntbase/{time.time()}.jpg', img_np)

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


class VIDSCAN(Resource):
    def post(self):
        auth_key = request.headers.get('clash-api-key')

        if auth_key == 'xxxxxxxxxxddddddddddtttttttttt12345' or "pyjHNAYVWY4484TqlGqLYGAyiUsYFWcX":
            content = request.get_json()
            if "youtube_url" in content.keys() and len(content.keys()) == 1:
                try:
                    youtube_url = content["youtube_url"]

                    resp = process_video_from_path(youtube_url)

                    return make_response(jsonify(resp), 200)
                except Exception as e:
                    print(e)
                    try:
                        os.remove('F:/yolov5/current.mp4')
                    except:
                        pass
                    try:
                        os.remove('F:/yolov5/current.part')
                    except:
                        pass

                    return make_response(jsonify({"message": "ERROR: Can't process data"}), 422)
            else:
                return make_response(jsonify({"message": "ERROR: Invalid POST request"}), 400)

        else:
            return make_response(jsonify({"message": "Unauthorized"}), 401)

def process_video_from_path(url):
    filename = 'F:/yolov5/current.mp4'
    
    ydl_opts = {
        "cookiefile":"cookies.txt",
        'outtmpl': filename
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    videoFile = filename
    vidcap = cv2.VideoCapture(videoFile)
    success,image = vidcap.read()

    seconds = 1
    fps = vidcap.get(cv2.CAP_PROP_FPS) # Gets the frames per second
    multiplier = fps * seconds

    timestamp = 0
    wanted_frame = round(multiplier * timestamp)
    data = []
    img_dict={}
    while success:

        frameId = int(round(vidcap.get(1))) #current frame number, rounded b/c sometimes you get frame intervals which aren't integers...this adds a little imprecision but is likely good enough
        success, image = vidcap.read()

        if frameId == wanted_frame+1:
            war_buildings_of_interest_current_count = 0
            any_buildings_of_interest_current_count = 0
            try:
                detections = yolov5.predict(image, max_objects=max_per_class_dict)
            except Exception:
                detections = []
            if detections:
                for obj in detections:
                    if obj['name'] in war_buildings_of_interest:
                        war_buildings_of_interest_current_count += 1
                    if obj['name'] in any_buildings_of_interest:
                        any_buildings_of_interest_current_count += 1
            print(f'{timestamp}s ', round(war_buildings_of_interest_current_count/27, 3), '    ', round(any_buildings_of_interest_current_count/74, 3))
            moy = ((war_buildings_of_interest_current_count/27 + any_buildings_of_interest_current_count/74)/2) * (100_000+timestamp)/100_000
            if moy > 0.8:
                img_dict[str(int(timestamp))] = image

            data.append({'second':int(timestamp),
                        'war_build_perct':round(war_buildings_of_interest_current_count/27, 3),
                        'any_build_perct':round(any_buildings_of_interest_current_count/74, 3)
                        }, )
            timestamp += 1
            wanted_frame = round(multiplier * timestamp)

    vidcap.release()
    df = pd.DataFrame(data, columns=['second', 'war_build_perct', 'any_build_perct'])

    high_moy = []
    what_to_return = []
    for row in df.values:
        moy = ((row[1]+row[2])/2) * (100_000+row[0])/100_000
        if moy > 0.8:
            high_moy.append((int(row[0]), moy))
            ok_6_8 = False
            ok_3_6 = False
            ok_1_3 = False
        if 0.6 < moy < 0.8:
            ok_6_8 = True
        if 0.3 < moy < 0.6:
            ok_3_6 = True
        if 0.1 < moy < 0.3:
            ok_1_3 = True
        if moy < 0.07 and len(high_moy) > 0:
            if ok_6_8 and ok_3_6 and ok_1_3:
                max_tup = max(high_moy, key=lambda x:x[1])
                name = '--%02d--%02d--%02d' % (int(max_tup[0]//3600), int(max_tup[0]//60)-int(max_tup[0]//3600)*60, int(max_tup[0]%60))
                name = name.replace('--', '%')
                try:
                    s3_file_name = image_to_s3(img_dict[str(max_tup[0])])
                    interesting = {}
                    interesting['timestamp_sec'] = max_tup[0]
                    interesting['is_triple'] = True
                    interesting["frame_url"] = s3_file_name
                    what_to_return.append(interesting)
                    
                    #cv2.imwrite(f'url_api/{videoFile.replace(".mp4", "")}{name}.jpg', img_dict[str(max_tup[0])])
                    
                except KeyError:
                    print(f'url_api/{videoFile.replace(".mp4", "")}{name}.jpg')
                high_moy = []
                ok_6_8 = False
                ok_3_6 = False
                ok_1_3 = False
            else:
                high_moy = []
                ok_6_8 = False
                ok_3_6 = False
                ok_1_3 = False

    try:
        os.remove('F:/yolov5/current.mp4')
    except:
        pass
                
    return what_to_return

def image_to_s3(img, filename=None, bucket_name="images.burntbase.com", key_prefix="img/marc"):
    if filename==None:
        filename = f"videocapture_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    aws_filename = f"{key_prefix}/{filename}"
    _, buffer = cv2.imencode(".jpg", img)
    io_buf = BytesIO(buffer)
    s3.upload_fileobj(
        Fileobj=io_buf, 
        Bucket=bucket_name, 
        Key=aws_filename,
        ExtraArgs={'ACL':'public-read'})
    
    frame_s3_url = f'https://s3.amazonaws.com/{bucket_name}/{key_prefix}/{filename}'
    return frame_s3_url

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
        