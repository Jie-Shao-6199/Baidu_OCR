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
import cv2

from Two_Page_OCR import get_file_content_as_base64, get_access_token, cut_name_str, get_location, get_file
from tqdm import tqdm
from txdpy import get_chinese, get_num, get_num_letter, get_Bletter, is_num_letter
import numpy as np
import pandas as pd
import requests

# API_KEY = "qWKwd5NQI3fxRu0f64MGGWYa"  # 19997106199
# SECRET_KEY = "mFuuSlq8L0PTelUQnGSk6bSqOokRoSX3"

# API_KEY = "PF9nG704jON3kEoHXKIiSXAP"  # 17519213264
# SECRET_KEY = "2CQzAwI28xpgEh2Xlzed06aBzQ2gEgtK"

API_KEY = "GGysNlmR9TrpFEch8YsMN88w"  # Tsuiwen
SECRET_KEY = "AzFH8dGlUlndIlz3dGUXpShy3dxOYTrw"

school_code = school_name = group_name = again_select = remark = plan_page = plan_batch_name = plan_first_select = ''
last_columns = ['batch_name', 'first_select', 'school_code', 'school_name', 'group_name', 'major_code',
                'major_name', 'again_select', 'having_major', 'major_remark', 'plan_num', 'remark', 'page']

judge = 0  # 1.having_major 2.major_remark 3.remark 4.major_name

temp_left_line = 0
temp_right_line = 0

school_df = pd.DataFrame(columns=last_columns, index=range(200))
row_id = 0


def get_word_dict(path):
    """
    获取每行的Word字典
    :param path:文件路径
    :return:
    """
    global temp_right_line, temp_left_line
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + get_access_token()

    image = get_file_content_as_base64(path, True)
    # payload = 'image={}&recognize_granularity=small'.format(image)
    payload = 'image={}&recognize_granularity=small'.format(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # 获取识别后的字段字典
    return_dict = json.loads(response.text)['words_result']

    image_size = cv2.imread(path)
    height, width, channels = image_size.shape
    line_list = get_line(path)
    # print(line_list)

    left_OCR_list = []
    middle_OCR_list = []
    right_OCR_df = []
    # print(return_dict)
    for dict_0 in return_dict:

        if dict_0['location']['left'] + dict_0['location']['width'] < 140 or dict_0['location']['left'] > width - 140:

            pass

        else:
            if len(line_list) > 1 and line_list[-1] - line_list[0] > 100:
                if dict_0['location']['left'] < line_list[0]:
                    temp_left_line = line_list[0]
                elif dict_0['location']['left'] < line_list[-1]:
                    temp_right_line = line_list[-1]

            if dict_0['location']['left'] < temp_left_line:
                left_OCR_list.append(dict_0)
            elif dict_0['location']['left'] < temp_right_line:
                middle_OCR_list.append(dict_0)
            else:
                right_OCR_df.append(dict_0)

    left_location, left_df = handle_data(left_OCR_list, 5, 3)
    middle_location, middle_df = handle_data(middle_OCR_list, 5, 3)
    right_location, right_df = handle_data(right_OCR_df, 5, 3)

    last_location = pd.concat([left_location, middle_location, right_location])
    last_df = pd.concat([left_df, middle_df, right_df], ignore_index=True)

    return last_location, last_df


def handle_data(data: list, len_school_code, len_major_code, len_group_code=None):
    """
    用来获取每个部分的哪些内容在同一行
    :param data: 已经将各部分拆分清楚地识别结果
    :param len_school_code:
    :param len_major_code:
    :param len_group_code:
    :return:
    """
    last_dict_list = []

    for value in data:
        c = value['words']
        value['words'] = re.sub(' ', '', value['words'])

        if len("".join(get_num_letter(value['words'][:len_school_code]))) == len_school_code and \
                len(value['words']) > len_school_code and get_chinese(value['words'][len_school_code]) and \
                len("".join(get_chinese(value['words'][len_school_code:]))) > 1 and '元' not in value['words'][len_school_code:]:

            temp_row_data1, temp_row_data2 = cut_name_str(value, len_school_code)

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)

        elif len("".join(get_num_letter(value['words'][:len_major_code]))) == len_major_code and \
                len(value['words']) > len_major_code and get_chinese(value['words'][len_major_code]) and \
                len("".join(get_chinese(value['words'][len_major_code:]))) > 1:

            temp_row_data1, temp_row_data2 = cut_name_str(value, len_major_code)

            last_dict_list.append(temp_row_data1)
            last_dict_list.append(temp_row_data2)

        elif len_group_code and len(
                "".join(get_num_letter(value['words'][:len_group_code]))) == len_group_code and \
                len(value['words']) > len_group_code and get_chinese(value['words'][len_group_code]) and \
                len("".join(get_chinese(value['words'][len_group_code:]))) > 1:

            temp_row_data1, temp_row_data2 = cut_name_str(value['words'], len_group_code)

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
    dict_list = []
    location_list = []
    a = 0
    for d_ct in last_dict_list:
        a += 1
        c = d_ct['words']
        # if d_ct['location']['left'] < width / 2 and d_ct['location']['left'] + d_ct['location']['width'] < width / 2:

        # 先创建个字典的列表随后把字典变成Dataframe
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
    dict_list.append(last_dict)
    location_list.append(location_dict)

    data_df = pd.DataFrame(dict_list)
    data_location = pd.DataFrame(location_list)

    temp_data = data_df, data_location
    temp_location1 = get_location(temp_data)
    column_location = [temp_location1[i]['left'] for i in temp_location1.keys()]
    column_location.sort()

    last_df = pd.DataFrame(columns=['words{}'.format(i) for i in range(len(column_location))],
                           index=range(200))
    last_location = pd.DataFrame(columns=['location{}'.format(i) for i in range(len(column_location))],
                                 index=range(200))

    for num in range(len(data_df.columns)):

        for da in range(len(data_df)):

            # 用来计算该单元格离哪列更近
            if type(data_location['location{}'.format(num)][da]) != float:
                temp_column = [abs(data_location['location{}'.format(num)][da]['left'] - column_location[i])
                               for i in range(len(column_location))]
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


def get_line(path):
    """
    基于边缘检测，直线检测，找到中间最长的两条分割线
    :param path:
    :return: 分割线的坐标
    """
    # 读入图像
    img = cv2.imread(path, 0)
    height, width = img.shape
    # 使用Canny边缘检测
    edges = cv2.Canny(img, 50, 150, apertureSize=3)

    # 使用霍夫线变换
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=0, minLineLength=300, maxLineGap=0)
    temp_list = []
    temp_width = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 判断线是否为垂直线
            if abs(x2 - x1) < 10 and x1 > width / 4 and x2 > width / 4 and x1 < width * 3 / 4 and x2 < width * 3 / 4:
                temp_width = x1
                temp_list.append(x1)
    temp_list.sort()

    return temp_list


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
    global school_code, school_name, group_name, again_select, remark, school_df, last_columns, row_id, judge
    df_location, df_data = get_word_dict(path)
    if len(df_data.columns) == len(input_columns):
        df_data.columns = input_columns
    else:
        last_df = school_df[:row_id + 1]
        judge = 0  # 1.having_major 2.major_remark 3.remark 4.major_name
        school_df = pd.DataFrame(columns=last_columns, index=range(200))
        row_id = 0
        return last_df

    last_df = pd.DataFrame(columns=last_columns)

    for num in range(len(df_data)):

        if df_data.notna().at[num, 'school_major_code']:

            if is_num_letter(df_data['school_major_code'][num]):

                if len(df_data['school_major_code'][num]) == len_school_code:
                    if school_name != '':
                        # 把remark赋值
                        school_df['remark'] = remark

                        last_df = pd.concat([last_df, school_df[:row_id + 1]], ignore_index=True)
                        # 重置
                        school_df = pd.DataFrame(columns=last_columns, index=range(200))
                        remark = ''
                        judge = 0
                        row_id = 0
                    school_code = df_data['school_major_code'][num]
                    school_name = df_data['school_major_name'][num]

                elif len(df_data['school_major_code'][num]) == len_major_code:

                    if school_df.notna().at[row_id, 'major_code']:
                        row_id += 1
                    school_df['school_code'][row_id] = school_code
                    school_df['school_name'][row_id] = school_name
                    school_df['group_name'][row_id] = group_name
                    school_df['major_code'][row_id] = df_data['school_major_code'][num]
                    school_df['major_name'][row_id] = df_data['school_major_name'][num]
                    school_df['plan_num'][row_id] = df_data['plan_num'][num]
                    school_df['again_select'][row_id] = again_select

                    school_df['page'][row_id] = plan_page
                    school_df['batch_name'][row_id] = plan_batch_name
                    school_df['first_select'][row_id] = plan_first_select

                    judge = 4

                else:
                    print(school_df)

            else:
                if '专业组' in df_data['school_major_code'][num]:
                    group_name = df_data['school_major_code'][num]

                elif '再选' in df_data['school_major_code'][num]:
                    again_select = df_data['school_major_code'][num]

                else:
                    remark += df_data['school_major_code'][num]
        else:
            if df_data.notna().at[num, 'school_major_name']:

                if df_data['school_major_name'][num][0] == '含' and judge == 4:

                    school_df['having_major'][row_id] = df_data['school_major_name'][num]
                    judge = 1

                elif df_data['school_major_name'][num][:4] == '以上专业':

                    remark += df_data['school_major_name'][num]
                    judge = 3

                else:
                    if judge == 1:
                        school_df['having_major'][row_id] += df_data['school_major_name'][num]
                        if df_data['school_major_name'][num][-2:] == '专业':
                            judge = 2

                    elif judge == 2:
                        if school_df.notna().at[row_id, 'major_remark']:
                            school_df['major_remark'][row_id] += df_data['school_major_name'][num]
                        else:
                            school_df['major_remark'][row_id] = df_data['school_major_name'][num]

                    elif judge == 3:
                        remark += df_data['school_major_name'][num]

                    elif judge == 4:
                        if school_df.notna().at[row_id, 'plan_num']:
                            school_df['major_remark'][row_id] = df_data['school_major_name'][num]
                            judge = 2
                        else:
                            school_df['major_name'][row_id] += df_data['school_major_name'][num]
                            if df_data.notna().at[num, 'plan_num']:
                                school_df['plan_num'][row_id] = df_data['plan_num'][num]

    return last_df


if __name__ == '__main__':
    # input_columns = ['school_major_code', 'school_major_name', 'select_require', 'year_plan_num', 'cost_year']  # 河北
    # input_columns = ['school_major_code', 'school_major_name', 'plan_num', 'select_require', 'edu_year', 'cost_year']  # 辽宁
    # input_columns = ['school_major_code', 'school_major_name', 'cost_year', 'plan_num']  # 吉林
    input_columns = ['school_major_code', 'school_major_name', 'plan_num']
    image_path = r'E:\OpenCV_Test\image'
    final_df = pd.DataFrame()
    for first_select in get_file(image_path):

        for batch_name in get_file(image_path + '/' + first_select):

            for page in tqdm(get_file(image_path + '/' + first_select + '/' + batch_name)):
                plan_page = page[:-4]
                plan_batch_name = batch_name
                plan_first_select = first_select
                page_path = image_path + '/' + first_select + '/' + batch_name + '/' + page
                return_df = main(page_path, 5, 3, input_columns)

                if len(final_df) == 0:

                    final_df = return_df

                else:
                    final_df = pd.concat([final_df, return_df], ignore_index=True)

                return_df = pd.concat([return_df, school_df], ignore_index=True)
                return_df.to_excel(r"E:\OpenCV_Test\excel\{}_{}.xlsx".format(first_select, page), index=False)

    final_df = pd.concat([final_df, school_df], ignore_index=True)
    final_df.to_excel(r"E:\OpenCV_Test\excel\01.xlsx", index=False)
