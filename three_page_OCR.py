"""
被分成三页的，OCR识别程序
适用于：安徽，广东，江西
"""
import base64
import json
import math
import os
import re
import urllib
from time import sleep

from Two_Page_OCR import get_file_content_as_base64, get_access_token, get_word_dict, handle_data
from tqdm import tqdm
from txdpy import get_chinese, get_num, get_num_letter, get_Bletter
# import cv2
import numpy as np
import pandas as pd
import requests

# API_KEY = "qWKwd5NQI3fxRu0f64MGGWYa"  # 19997106199
# SECRET_KEY = "mFuuSlq8L0PTelUQnGSk6bSqOokRoSX3"

# API_KEY = "PF9nG704jON3kEoHXKIiSXAP"  # 17519213264
# SECRET_KEY = "2CQzAwI28xpgEh2Xlzed06aBzQ2gEgtK"

API_KEY = "GGysNlmR9TrpFEch8YsMN88w"  # Tsuiwen
SECRET_KEY = "AzFH8dGlUlndIlz3dGUXpShy3dxOYTrw"


# def get_word_dict(path, len_school_code, len_major_code, len_group_code=None):
#     """
#     获取每行的Word字典
#     :param len_group_code:
#     :param len_major_code:
#     :param len_school_code:
#     :param path:
#     :return:
#     """
#     url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + get_access_token()
#
#     image = get_file_content_as_base64(path, True)
#     payload = 'image={}&recognize_granularity=small'.format(image)
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Accept': 'application/json'
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#     # 获取识别后的字段字典
#     return_dict = json.loads(response.text)['words_result']
#
#     print(return_dict)
#     last_dict = {}
#     location_dict = {}
#     temp_left_num = 0
#     temp_location = 0
#     dict_list = []
#     location_list = []
#     line_num = 0
#
#     a = 0
#     for d_ct in return_dict:
#         a += 1
#         # if d_ct['location']['left'] < width / 2 and d_ct['location']['left'] + d_ct['location']['width'] < width / 2:
#
#         # 先创建个字典的列表随后把字典变成Dataframe
#         if d_ct['location']['left'] + d_ct['location']['width'] > temp_left_num:
#             if d_ct['location']['top'] > temp_location:
#                 if temp_location != 0:
#                     dict_list.append(last_dict)
#                     location_list.append(location_dict)
#
#                 # 若为新的一行则进行重置
#                 last_dict = {}
#                 location_dict = {}
#                 line_num = 0
#                 last_dict['words{}'.format(line_num)] = d_ct['words']
#                 location_dict['location{}'.format(line_num)] = d_ct['location']
#                 temp_location = d_ct['location']['top'] + (d_ct['location']['height']) / 2
#                 line_num += 1
#
#             else:
#                 last_dict['words{}'.format(line_num)] = d_ct['words']
#                 location_dict['location{}'.format(line_num)] = d_ct['location']
#                 temp_location = d_ct['location']['top'] + (d_ct['location']['height']) / 2
#                 line_num += 1
#     dict_list.append(last_dict)
#     location_list.append(location_dict)
#
#     pd.DataFrame(dict_list).to_excel(r'{}.xlsx'.format(path[:-4]), index=False)
#
#     return return_dict


def main(path, len_school_code, len_major_code, columns, len_group_code=None):
    """
    主函数
    :param columns: 招生计划属性
    :param len_group_code: 专业组代码长度，默认为None
    :param path: 图片路径
    :param len_school_code: 学校代码长度
    :param len_major_code: 专业名称长度
    :return:
    """
    word = get_word_dict(path, len_school_code, len_major_code, len_group_code=len_group_code)
    last_location, last_df = handle_data(word)
    last_df.to_excel(r'{}.xlsx'.format(path[:-4]), index=False)


if __name__ == '__main__':
    # input_columns = ['school_major_code', 'school_major_name', 'select_require', 'year_plan_num', 'cost_year']  # 河北
    # input_columns = ['school_major_code', 'school_major_name', 'plan_num', 'select_require', 'edu_year', 'cost_year']  # 辽宁
    # input_columns = ['school_major_code', 'school_major_name', 'cost_year', 'plan_num']  # 吉林
    input_columns = ['school_major_code', 'school_major_name', 'plan_num', 'edu_year', 'cost_year']
    main(r"D:\桌面\广东省2023年招生计划（历史）.jpg", 5, 3, input_columns)
