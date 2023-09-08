"""
被分成两页的，OCR识别程序
"""
import base64
import json
import math
import os
import urllib
from time import sleep

from tqdm import tqdm
from txdpy import get_chinese, get_num, get_num_letter, get_Bletter
# import cv2
import numpy as np
import pandas as pd
import requests

# API_KEY = "qWKwd5NQI3fxRu0f64MGGWYa"
# SECRET_KEY = "mFuuSlq8L0PTelUQnGSk6bSqOokRoSX3"

API_KEY = "PF9nG704jON3kEoHXKIiSXAP"
SECRET_KEY = "2CQzAwI28xpgEh2Xlzed06aBzQ2gEgtK"

school_code = school_name = group_code = group_name = ''


def get_location(data):
    """
    对获取到的数据进行拆分
    :param data:原始数据
    :return:返回每列数据的左上角坐标，字典
    """
    column_location = {}
    data_df, data_location = data
    # 判断哪列是最全的然后获取最全这列的坐标
    for da in range(len(data_df)):
        judge = False
        for column in data_df.columns:

            if type(data_df[column][da]) != float and data_df['words0'][da].isdigit():

                judge = True

            else:

                judge = False
                break
        if judge:

            for column1 in data_location.columns:
                column_location[column1] = data_location[column1][da]

            break

    return column_location


def handle_data(data):
    """
    对获取到的数据进行拆分
    :param data:原始数据
    :return:返回excel表，各列数据都分配完后的Excel表
    """
    column_location = get_location(data)
    data_df, data_location = data

    last_df = pd.DataFrame(columns=['words{}'.format(i) for i in range(len(column_location.keys()))],
                           index=range(200))
    last_location = pd.DataFrame(columns=['location{}'.format(i) for i in range(len(column_location.keys()))],
                                 index=range(200))
    # print(column_location.keys())
    for num in range(len(column_location.keys())):

        for da in range(len(data_df)):
            # 用来计算该单元格离哪列更近
            if type(data_location['location{}'.format(num)][da]) != float:
                temp_column = [abs(data_location['location{}'.format(num)][da]['left'] - column_location[i]['left'])
                               for i in column_location.keys()]
                # print(column_location)
                # print(temp_column)
                # print(min(temp_column))
                # print(temp_column.index(min(temp_column)))
                # print(type(min(temp_column)))
                # print(math.isnan(min(temp_column)))
                data_index = temp_column.index(min(temp_column))  # 获取最小值的位置
                if math.isnan(min(temp_column)):

                    pass

                else:
                    if type(last_df['words{}'.format(data_index)][da]) == float:  # 原本没内容直接赋值
                        last_df['words{}'.format(data_index)][da] = data_df['words{}'.format(num)][da]
                        last_location['location{}'.format(data_index)][da] = data_location['location{}'.format(num)][da]

                    else:  # 原本有内容将其合并
                        last_df['words{}'.format(data_index)][da] += data_df['words{}'.format(num)][da]

    return last_location[:len(data_df)], last_df[:len(data_df)]


def cut_name_str(value, len_code):
    """
    用来分割专业，学校及其代码
    :param value: 数据源，是个字典
    :param len_code: 字符长度，代码长度
    :return:
    """
    temp_row_data1 = {'words': value['words'][:len_code],
                      'location': {'top': value['chars'][0]['location']['top'],
                                   'left': value['chars'][0]['location']['left'],
                                   'height': value['chars'][0]['location']['height'],
                                   'width': value['chars'][len_code - 1]['location']['left'] +
                                            value['chars'][len_code - 1]['location']['width'] -
                                            value['chars'][0]['location']['left']},
                      'chars': value['chars'][:len_code]}
    temp_row_data2 = {'words': value['words'][len_code:],
                      'location': {'top': value['chars'][len_code]['location']['top'],
                                   'left': value['chars'][len_code]['location']['left'],
                                   'height': value['chars'][len_code]['location']['height'],
                                   'width': value['chars'][-1]['location']['left'] +
                                            value['chars'][-1]['location']['width'] -
                                            value['chars'][len_code]['location']['left']},
                      'chars': value['chars'][len_code:]}
    return temp_row_data1, temp_row_data2


def get_word_dict(path, len_school_code, len_major_code, len_group_code=None):
    """
    获取每行的Word字典
    :param len_group_code:
    :param len_major_code:
    :param len_school_code:
    :param path:
    :return:
    """
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + get_access_token()

    image = get_file_content_as_base64(path, True)
    payload = 'image={}&recognize_granularity=small'.format(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # 获取识别后的字段字典
    return_dict = json.loads(response.text)['words_result']
    dict_list = []
    temp_left_num = 0
    # temp_right_num = 0
    location_list = []

    # image = cv2.imread(path)
    # height, width, channels = image.shape

    last_dict_list = []
    for value in return_dict:
        if len("".join(get_num_letter(value['words'][:len_school_code]))) == len_school_code and \
                len(value['words']) > len_school_code and get_chinese(value['words'][len_school_code]) and \
                len("".join(get_chinese(value['words'][len_school_code:]))) > 1:

            temp_row_data1, temp_row_data2 = cut_name_str(value, len_school_code)

            if temp_left_num == 0 or value['location']['left'] < temp_left_num:
                temp_left_num = value['location']['left']

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)

        elif len("".join(get_num_letter(value['words'][:len_major_code]))) == len_major_code and \
                len(value['words']) > len_major_code and get_chinese(value['words'][len_major_code]) and \
                len("".join(get_chinese(value['words'][len_major_code:]))) > 1:

            temp_row_data1, temp_row_data2 = cut_name_str(value, len_major_code)

            if temp_left_num == 0 or value['location']['left'] < temp_left_num:
                temp_left_num = value['location']['left']

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)

        elif len_group_code and len(
                "".join(get_num_letter(value['words'][:len_group_code]))) == len_group_code and \
                len(value['words']) > len_group_code and get_chinese(value['words'][len_group_code]) and \
                len("".join(get_chinese(value['words'][:len_major_code]))) > 1:

            temp_row_data1, temp_row_data2 = cut_name_str(value, len_group_code)

            if temp_left_num == 0 or value['location']['left'] < temp_left_num:
                temp_left_num = value['location']['left']

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)
        else:
            last_dict_list.append(value)

    line_num = 0  # 现有列数
    # right_line_num = 0  # 右侧现有列数
    temp_location = 0  # 文本框右下角y坐标
    # right_temp_location = 0  # 右侧文本框右下角y坐标
    last_dict = {}
    # right_dict = {}
    location_dict = {}
    # right_location_dict = {}
    a = 0
    for d_ct in last_dict_list:
        a += 1
        # if d_ct['location']['left'] < width / 2 and d_ct['location']['left'] + d_ct['location']['width'] < width / 2:

        # 先创建个字典的列表随后把字典变成Dataframe
        if d_ct['location']['left'] + d_ct['location']['width'] > temp_left_num:
            if d_ct['location']['top'] > temp_location:
                if temp_location != 0:
                    dict_list.append(last_dict)
                    location_list.append(location_dict)

                # 若为新的一行则进行重置
                last_dict = {}
                location_dict = {}
                line_num = 0
                last_dict['words{}'.format(line_num)] = d_ct['words']
                location_dict['location{}'.format(line_num)] = d_ct['location']
                temp_location = d_ct['location']['top'] + (d_ct['location']['height']) / 2
                line_num += 1

            else:
                last_dict['words{}'.format(line_num)] = d_ct['words']
                location_dict['location{}'.format(line_num)] = d_ct['location']
                temp_location = d_ct['location']['top'] + (d_ct['location']['height']) / 2
                line_num += 1

        # else:
        #
        #     # 先创建个字典的列表随后把字典变成Dataframe
        #
        #     if d_ct['location']['top'] > right_temp_location:
        #         if right_temp_location != 0:
        #             right_dict_list.append(right_dict)
        #             right_location_list.append(right_location_dict)
        #         # 若为新的一行则进行重置
        #         right_dict = {}
        #         right_location_dict = {}
        #         right_line_num = 0
        #         right_dict['words{}'.format(right_line_num)] = d_ct['words']
        #         right_location_dict['location{}'.format(right_line_num)] = d_ct['location']['left']
        #         right_temp_location = d_ct['location']['top'] + (d_ct['location']['height'])/2
        #         right_line_num += 1
        #
        #     else:
        #         right_dict['words{}'.format(right_line_num)] = d_ct['words']
        #         right_location_dict['location{}'.format(right_line_num)] = d_ct['location']['left']
        #         right_temp_location = d_ct['location']['top'] + (d_ct['location']['height']) / 2
        #         right_line_num += 1

    dict_list.append(last_dict)
    location_list.append(location_dict)
    # right_dict_list.append(right_dict)
    # right_location_list.append(right_location_dict)
    # return_df = pd.concat([pd.DataFrame(dict_list), pd.DataFrame(right_dict_list)], ignore_index=True)
    # return_location = pd.concat([pd.DataFrame(location_list), pd.DataFrame(right_location_list)], ignore_index=True)
    # return_df.to_excel(r'E:\OpenCV_Test\return_df.xlsx', index=False)
    # return_location.to_excel(r'E:\OpenCV_Test\return_location.xlsx', index=False)

    return pd.DataFrame(dict_list), pd.DataFrame(location_list)


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


def data_arrange(data: pd.DataFrame, location: pd.DataFrame, len_school_code, len_major_code, columns: list,
                 len_group_code=None):
    """
    将传入的表格内容进行整理, 删除多余的数据
    :param len_group_code: 专业组代码长度，默认为None
    :param len_major_code: 专业代码长度
    :param len_school_code: 学校代码长度
    :param location:  需要处理的表格各单元格的坐标   (目前没啥用)
    :param columns: 大本中的属性，按从左到右的顺序形成列表
    :param data: DataFrame, 需要处理的表格
    :return:
    """
    global school_code, school_name, group_code, group_name
    # 'school_major_code', 'school_major_name', 'select_require', 'edu_year', 'plan_num', 'cost_year'
    if len(data.columns) == len(columns) * 2:

        left_df = data.iloc[:, :len(columns)]
        right_df = data.iloc[:, len(columns):]
        left_location = location.iloc[:, :len(columns)]
        right_location = location.iloc[:, len(columns):]
        left_df.columns = columns
        right_df.columns = columns
        left_location.columns = columns
        right_location.columns = columns
        last_df = pd.concat([left_df, right_df], ignore_index=True)
        last_location = pd.concat([left_location, right_location], ignore_index=True)

    elif len(data.columns) == len(columns):
        last_df = data
        last_location = location
        last_df.columns = columns
        last_location.columns = columns

    else:
        return pd.DataFrame({'batch_name': [0], 'subject_name': [0], 'school_code': [0], 'school_name': [0],
                             'major_code': [0], 'major_name': [0], 'select_require': [0], 'edu_year': [0],
                             'plan_num': [0], 'cost_year': [0]})

    return_df = pd.DataFrame(columns=['batch_name', 'subject_name', 'school_code', 'school_name', 'major_code',
                                      'major_name', 'select_require', 'edu_year', 'plan_num', 'cost_year'],
                             index=range(200))
    row_id = 0
    temp_top = 0

    for num in range(len(last_df)):

        if type(last_df['school_major_code'][num]) != float and get_chinese(last_df['school_major_code'][num]):

            if temp_top == 0 or last_location['school_major_code'][num]['top'] + \
                    last_location['school_major_code'][num]['height'] > temp_top:
                temp_top = last_location['school_major_code'][num]['top'] + \
                           last_location['school_major_code'][num]['height']

    for la in range(len(last_df)):

        if type(last_df['school_major_code'][la]) == float:
            if type(last_df['school_major_name'][la]) != float and get_chinese(last_df['school_major_name'][la]):
                if last_location['school_major_name'][la]['top'] > temp_top:
                    if type(return_df['major_name'][row_id]) != float:
                        return_df['major_name'][row_id] += last_df['school_major_name'][la]

                    else:
                        return_df['major_name'][row_id] = last_df['school_major_name'][la]
        elif last_location['school_major_code'][la]['top'] > temp_top:
            if len(last_df['school_major_code'][la]) == len_school_code:

                school_code = last_df['school_major_code'][la]
                school_name = last_df['school_major_name'][la]

            elif len(last_df['school_major_code'][la]) == len_major_code:

                if type(return_df['major_name'][row_id]) != float:
                    row_id += 1

                return_df['school_code'][row_id] = school_code
                return_df['school_name'][row_id] = school_name
                return_df['major_code'][row_id] = last_df['school_major_code'][la]
                return_df['major_name'][row_id] = last_df['school_major_name'][la]
                if 'select_require' in last_df.columns:
                    return_df['select_require'][row_id] = last_df['select_require'][la]
                if 'edu_year' in last_df.columns:
                    return_df['edu_year'][row_id] = last_df['edu_year'][la]
                if 'plan_num' in last_df.columns:
                    return_df['plan_num'][row_id] = last_df['plan_num'][la]
                if 'cost_year' in last_df.columns:
                    return_df['cost_year'][row_id] = last_df['cost_year'][la]
                if 'year_plan_num' in last_df.columns:
                    if type(last_df['year_plan_num'][la]) != float:
                        if last_df['year_plan_num'][la].isdigit():
                            return_df['edu_year'][row_id] = last_df['year_plan_num'][la][-1:]
                            return_df['plan_num'][row_id] = last_df['year_plan_num'][la][:-1]

                        else:

                            return_df['edu_year'][row_id] = "".join(get_chinese(last_df['year_plan_num'][la]))
                            return_df['plan_num'][row_id] = "".join(get_num(last_df['year_plan_num'][la]))

    return return_df[:row_id + 1]


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
    word = get_word_dict(path, len_school_code, len_major_code)
    last_location, last_df = handle_data(word)
    # right_location, right_df = handle_data(word[2:])
    # 山东省招生计划属性,之后需要自定义功能
    # columns = ['school_major_code', 'school_major_name', 'select_require', 'edu_year', 'plan_num', 'cost_year']
    # columns = ['school_major_code', 'school_major_name', 'select_require', 'year_plan_num', 'cost_year']

    last_df = data_arrange(last_df, last_location, len_school_code, len_major_code, columns)

    # last_df.to_excel(r'{}.xlsx'.format(path[:-4]), index=False)
    # last_location.to_excel(r'{}location.xlsx'.format(path[:-4]), index=False)
    # word[0].to_excel(r'{}df.xlsx'.format(path[:-4]), index=False)
    # word[1].to_excel(r'{}location.xlsx'.format(path[:-4]), index=False)

    return last_df


def get_file(path):
    """
    获取文件夹下所有目录
    :param path: 文件路径
    :return: 文件列表
    """

    # os.listdir()方法获取文件夹名字，返回数组
    file_name_list = os.listdir(path)

    return file_name_list


if __name__ == '__main__':
    input_columns = ['school_major_code', 'school_major_name', 'select_require', 'year_plan_num', 'cost_year']
    # main(r"E:\OpenCV_Test\hb.jpg", 4, 2, input_columns)
    school_len = 4
    major_len = 2
    path = r'D:\桌面\河北省图片'
    final_df = pd.DataFrame()
    for subject_name in get_file(path):

        for batch_name in get_file(path + '/' + subject_name):

            for page in tqdm(get_file(path + '/' + subject_name + '/' + batch_name)):

                page_path = path + '/' + subject_name + '/' + batch_name + '/' + page

                df = main(page_path, school_len, major_len, input_columns)
                df['batch_name'] = batch_name
                df['subject_name'] = subject_name
                df['page'] = page[:-4]
                df.to_excel(r'D:\桌面\河北省招生计划Excel\{}_{}.xlsx'.format(subject_name, page), index=False)
                if len(final_df) == 0:

                    final_df = df

                else:

                    final_df = pd.concat([df, final_df], ignore_index=True)

    final_df.to_excel(r'D:\桌面\河北省图片\河北省招生计划.xlsx', index=False)
