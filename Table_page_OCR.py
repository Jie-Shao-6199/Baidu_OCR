"""
大本被做成表格的，OCR识别程序
适用于：新疆，天津，福建
"""
import base64
import json
import urllib
import requests
import pandas as pd
from io import BytesIO


API_KEY = "GGysNlmR9TrpFEch8YsMN88w"
SECRET_KEY = "AzFH8dGlUlndIlz3dGUXpShy3dxOYTrw"


def main(path):
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/table?access_token=" + get_access_token()

    # image 可以通过 get_file_content_as_base64("C:\fakepath\js.jpg",True) 方法获取
    image = get_file_content_as_base64(path, True)
    payload = 'image={}&cell_contents=false&return_excel=true'.format(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # excel_file = BytesIO(base64.b64decode(json.loads(response.text)['excel_file']))
    # df = pd.read_excel(excel_file)
    print(json.loads(response.text))


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    main(r"E:\OpenCV_Test\js.jpg")
