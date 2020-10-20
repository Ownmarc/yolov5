import redis
import json
import time
import base64

import cv2
import numpy as np
from datetime import timedelta

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
                      'champ':1,
                      '100':1}

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
                [255,255,0],
                [255,255,255]]

#weights_path = 'runs/exp33/weights/best.pt'
weights_path = 'clash_weights/best.pt'

redisClient = redis.StrictRedis(host='localhost', port=6379, db=0)

yolov5 = Yolov5(weights_path, img_size=800, device='0', conf_thres=0.7, colors=clash_colors)


while True:
    try:
        if redisClient.llen('img_list') > 0:
            time_now = time.time()
            keys = []
            batch = []
            while len(batch) < 4 and redisClient.llen('img_list') != 0:
                key = ''
                try:
                    data = json.loads(redisClient.lpop('img_list').decode('utf8'))
                    key = list(data.keys())[0]
                    encoded_string = data[key]

                    image_bytes = base64.b64decode(str(encoded_string))
                    img_from_buf = np.frombuffer(image_bytes, np.uint8)
                    img_np = cv2.imdecode(img_from_buf, 1)[:,:,:3]

                    batch.append(img_np)
                    keys.append(key)
                    
                except Exception:
                    payload = {
                    'status':'error'
                    }
                    redisClient.setex(str(key), timedelta(minutes=1), value=json.dumps(payload))
                    continue
            
            
            if len(batch) > 0:
                pred_time = time.time()
                batch_detections = yolov5.predict_batch(batch, max_objects=max_per_class_dict)

                for key, detections, img in zip(keys, batch_detections, batch):
                    height, width, _ = img.shape
                    payload = {
                        'status':'success',
                        'height':height,
                        'width':width,
                        'detections':detections
                    }
                    redisClient.setex(str(key), timedelta(minutes=1), value=json.dumps(payload))
                print(f'processed batch of {len(batch)} images in {time.time()-time_now} seconds')
        else:
            time.sleep(0.05)   

    except Exception as e:
        print(e)
        time.sleep(0.05)
        continue