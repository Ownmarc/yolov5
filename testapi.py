import os 
import requests
import time
import base64

API = 'http://localhost:5001'

with open(r'data/new/3kMvc2p69AE%00%00%05.jpg', 'rb') as reader:
    image = reader.read()

img64_bytes = base64.b64encode(image)
img64_string = img64_bytes.decode('utf-8')
post_data = {'encoded_string': img64_string}

timeit = time.time()
valid_response = requests.get(f'{API}/upload', json=post_data)
print(valid_response.text)
print(time.time()-timeit)