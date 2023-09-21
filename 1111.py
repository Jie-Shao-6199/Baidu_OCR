import requests
import json

API_KEY = "GXnDWlpUxWtUBl3ogrxD3lcR"
SECRET_KEY = "UuF2m3VL0ciaTtqnpoPFcUgKHDmZhWLH"


def main():
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v2/dnnlm_cn?charset=UTF-8&access_token=" + get_access_token()

    payload = json.dumps({
        "text": "以上专业除有说明外，其他专业学制：4年；学费：4200元/学年；住宿费：待定；办学地点：第一学年北校区，第二至四学年樱花"
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
