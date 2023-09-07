#  获取access_token
import requests
import json


def main():
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=qWKwd5NQI3fxRu0f64MGGWYa&client_secret=mFuuSlq8L0PTelUQnGSk6bSqOokRoSX3"

    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(bytes.decode(response.__dict__['_content']))["access_token"]


if __name__ == '__main__':
    main()
