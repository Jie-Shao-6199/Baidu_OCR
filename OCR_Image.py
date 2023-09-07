"""
ceshi
"""
import base64
import json
import urllib
from txdpy import get_chinese, get_num, get_num_letter, get_Bletter
import cv2
import pandas as pd
import requests

API_KEY = "qWKwd5NQI3fxRu0f64MGGWYa"
SECRET_KEY = "mFuuSlq8L0PTelUQnGSk6bSqOokRoSX3"


def handle_data(data):
    """
    对获取到的数据进行拆分
    :param data:原始数据
    :return:返回Excel，完成数据的
    """
    words = data['words'].values
    location = data['location'].values

    temp_x = 0
    temp_y = 0

    for da in range(len(data)):
        pass


def main(path, len_school_code, len_major_code, len_group_code=None):
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + get_access_token()

    image = get_file_content_as_base64(path, True)
    payload = 'image={}&recognize_granularity=small'.format(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return_dict = json.loads(response.text)

    print(return_dict)

    left_df = pd.DataFrame(columns=return_dict['words_result'][0].keys())
    right_df = left_df.copy()

    image = cv2.imread(path)
    height, width, channels = image.shape
    target_size = (int(width / 5), int(height / 5))
    image = cv2.resize(image, target_size)

    # 左侧页面，离左侧距离的列表
    left_loc = []
    # 右侧页面，离左侧距离的列表
    right_loc = []
    last_dict_list = []
    for value in return_dict['words_result']:
        if len("".join(get_num_letter(value['words'][:len_school_code]))) == len_school_code and \
                len(value['words']) > len_school_code and get_chinese(value['words'][len_school_code]):

            temp_row_data1 = {'words': value['words'][:len_school_code],
                               'top': value['chars'][0]['location']['top'],
                               'left': value['chars'][0]['location']['left'],
                               'height': value['chars'][0]['location']['height'],
                               'width': value['chars'][len_school_code - 1]['location']['left'] +
                                        value['chars'][len_school_code - 1]['location']['width'] -
                                        value['chars'][0]['location']['left'],
                              'chars': value['chars'][:len_school_code]}
            temp_row_data2 = {'words': value['words'][len_school_code:],
                                'top': value['chars'][len_school_code]['location']['top'],
                                'left': value['chars'][len_school_code]['location']['left'],
                                'height': value['chars'][len_school_code]['location']['height'],
                                'width': value['chars'][-1]['location']['left'] +
                                         value['chars'][-1]['location']['width'] -
                                         value['chars'][len_school_code]['location']['left'],
                              'chars': value['chars'][len_school_code:]}

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)

        elif len("".join(get_num_letter(value['words'][:len_major_code]))) == len_major_code and \
                len(value['words']) > len_major_code and get_chinese(value['words'][len_major_code]):

            temp_row_data1 = {'words': value['words'][:len_major_code],
                               'top': value['chars'][0]['location']['top'],
                               'left': value['chars'][0]['location']['left'],
                               'height': value['chars'][0]['location']['height'],
                               'width': value['chars'][len_major_code - 1]['location']['left'] +
                                        value['chars'][len_major_code - 1]['location']['width'] -
                                        value['chars'][0]['location']['left'],
                              'chars': value['chars'][:len_major_code]}
            temp_row_data2 = {'words': value['words'][len_major_code:],
                               'top': value['chars'][len_major_code]['location']['top'],
                               'left': value['chars'][len_major_code]['location']['left'],
                               'height': value['chars'][len_major_code]['location']['height'],
                               'width': value['chars'][-1]['location']['left'] +
                                        value['chars'][-1]['location']['width'] -
                                        value['chars'][len_major_code]['location']['left'],
                              'chars': value['chars'][len_major_code:]}

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)

        elif len_group_code and len(
                "".join(get_num_letter(value['words'][:len_group_code]))) == len_group_code and \
                len(value['words']) > len_group_code and get_chinese(value['words'][len_group_code]):

            temp_row_data1 = {'words': value['words'][:len_group_code],
                               'top': value['chars'][0]['location']['top'],
                               'left': value['chars'][0]['location']['left'],
                               'height': value['chars'][0]['location']['height'],
                               'width': value['chars'][len_group_code - 1]['location']['left'] +
                                        value['chars'][len_group_code - 1]['location']['width'] -
                                        value['chars'][0]['location']['left'],
                              'chars': value['chars'][:len_group_code]}
            temp_row_data2 = {'words': value['words'][len_group_code:],
                               'top': value['chars'][len_group_code]['location']['top'],
                               'left': value['chars'][len_group_code]['location']['left'],
                               'height': value['chars'][len_group_code]['location']['height'],
                               'width': value['chars'][-1]['location']['left'] +
                                        value['chars'][-1]['location']['width'] -
                                        value['chars'][len_group_code]['location']['left'],
                              'chars': value['chars'][len_group_code:]}

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)
        else:
            temp_row_data = {'words': value['words'],
                               'top': value['location']['top'],
                               'left': value['location']['left'],
                               'height': value['location']['height'],
                               'width': value['location']['width'],
                              'chars': value['chars']}
            last_dict_list.append(temp_row_data)

    top_list = [i['top'] for i in last_dict_list]
    left_list = [i['left'] for i in last_dict_list]


    for d in last_dict_list:

        # if len(d['words']) > 1 and (len(''.join(get_num_letter(d['words']))) == len_major_code or
        #                             len(''.join(get_num_letter(d['words']))) == len_school_code or
        #                             len(''.join(get_num_letter(d['words']))) == len_group_code):
        if d['left'] == min(left_list):

            if get_chinese(d['words']):

                left_list = left_list.remove(min(left_list))






    for d_ct in last_dict_list:
        if d_ct['left'] < width / 2:
            left_loc.append(d_ct['left'])
            left_df = pd.concat([left_df, pd.DataFrame([d_ct])], ignore_index=True)

        else:
            right_loc.append(d_ct['left'])
            right_df = pd.concat([right_df, pd.DataFrame([d_ct])], ignore_index=True)

    return_df = pd.concat([left_df, right_df], ignore_index=True)

    for i in range(len(return_df)):
        # for char in df['chars'][i]:
        #
        #     x = char['location']['left']
        #     y = char['location']['top']
        #     h = char['location']['height']
        #     w = char['location']['width']

        x = int(return_df['left'][i] / 5)
        y = int(return_df['top'][i] / 5)
        h = int(return_df['height'][i] / 5)
        w = int(return_df['width'][i] / 5)

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # cv2.rectangle(image, (x, y), (x1, y1), (0, 255, 0), 2)
        # cv2.rectangle(image, (34, 163), (124, 196), (0, 255, 0), 2)
        # cv2.rectangle(image, (306, 172), (551, 193), (0, 255, 0), 2)
    cv2.rectangle(image, (int(width / 2 / 5), height), (0, 0), (0, 255, 0), 2)
    # target_size = (int(width / 4), int(height / 4))  # 你可以根据实际情况调整大小
    # resized_image = cv2.resize(image, target_size)

    cv2.imshow('Rectangles', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return_df.to_excel(r"{}.xlsx".format(path[:-4]), index=False)
    return return_df


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

    # print(content)
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
    word = main(r"E:\OpenCV_Test\hb.jpg", 4, 2)
    handle_data(word)
