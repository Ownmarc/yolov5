import os 
import requests
import base64

API = f'https://llw6mvw5rh.execute-api.ca-central-1.amazonaws.com'

# load an image from where ever

image_path = r'data/copied_data/images/3kMvc2p69AE%00%00%05.jpg'
image_path = 'C:/Users/marcp/Downloads/videocapture_20200904_215946_995283_0_0.jpg'
with open(image_path, 'rb') as reader:
    image = reader.read()

#convert to base64
img64_bytes = base64.b64encode(image)
img64_string = img64_bytes.decode('utf-8')
post_data = {'encoded_string': img64_string}

#required headers
headers = {'clash-api-key': 'xxxxxxxxxxddddddddddtttttttttt12345'}

response = requests.post(f'{API}/burntbase', json=post_data, headers=headers)
print(response.text)