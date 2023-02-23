# Naver Clova OCR Request

import requests
import time
import json


# api_url : Naver API Gateway
# secret_key : Naver API Gateway Secret Key
# uuid : 각 PC 에서 import uuid 를 통해 발급
# image_file : 이미지의 url
def request_api(api_url, secret_key, uuid, image_file):
    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': 'demo'
            }
        ],
        'requestId': uuid,
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json)}
    files = [
      ('file', image_file)
    ]
    headers = {
      'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

    result = response.json()

    return result