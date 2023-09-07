import requests
import json

API_KEY = "jGF4ZN10RT7zCYFxinSzBRH8"
SECRET_KEY = "DqK3WZG5Xpr1hGTbU78U6zoFW8E8RibX"


def main():
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/create?access_token=" + get_access_token()

    payload = json.dumps({
        "speech_url": "https://sj-111021112.bj.bcebos.com/236999.m4a?authorization=bce-auth-v1/8ad975eb84614721a3f714b9a80d5eb2/2023-04-10T02%3A25%3A21Z/300/host/19eed825a4a362f7e3b023f49bd88eba4eb4a787095d05850d9b22009fa5432b",
        "format": "pcm",
        "pid": 80001,
        "rate": 16000
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    main()