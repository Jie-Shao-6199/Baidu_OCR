"""
天津历年录取分数OCR
"""
import base64
import json
import urllib
import re

from tqdm import tqdm
from Fujian_score_OCR import get_access_token, get_file_content_as_base64
from Two_Page_OCR import get_file
import pandas as pd
import requests
from txdpy import is_num, is_chinese, is_num_letter, get_num, get_chinese

# 本月无法继续访问
API_KEY = "GGysNlmR9TrpFEch8YsMN88w"
SECRET_KEY = "AzFH8dGlUlndIlz3dGUXpShy3dxOYTrw"

# API_KEY = "PF9nG704jON3kEoHXKIiSXAP"  # 17519213264
# SECRET_KEY = "2CQzAwI28xpgEh2Xlzed06aBzQ2gEgtK"

# API_KEY = "qWKwd5NQI3fxRu0f64MGGWYa"  # 19997106199
# SECRET_KEY = "mFuuSlq8L0PTelUQnGSk6bSqOokRoSX3"

school_name = group_code = ''


def main(path):
    """
    主函数
    :param path:
    :return:
    """
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/table?access_token=" + get_access_token()

    # image 可以通过 get_file_content_as_base64("C:\fakepath\页面提取自－2022年福建普通类本科批录取分数（历史）.pdf.jpg",True) 方法获取
    image = get_file_content_as_base64(path, True)
    # print(image)
    payload = 'image={}&cell_contents=false&return_excel=true'.format(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.json())
    get_bytes = response.json()['excel_file'].encode('utf-8')
    decoded_data = base64.b64decode(get_bytes)
    df = pd.read_excel(decoded_data, header=None)


    return df


def handle_data(data: pd.DataFrame):
    """
    处理Dataframe数据，形成最终格式
    :param data: 需要处理的数据
    :return: 最终的DataFrame
    """
    global school_name, group_code

    data_is_nan_mask = data.isna()
    is_nan_count = data_is_nan_mask.sum(axis=0)

    if len(data.columns) > 4:
        for i in range(len(data)):
            for column in data.columns[:4]:
                a = is_nan_count[column]
                b = max(is_nan_count)
                if is_nan_count[column] == max(is_nan_count[:4]):
                    if data.isna().at[i, column]:
                        data.iloc[i, data.columns.get_loc(column): -1] = data.iloc[i, data.columns.get_loc(column) + 1:].values
        data_not_nan_mask = data.notna()
        not_nan_count = data_not_nan_mask.sum(axis=0)
        data = data.drop(columns=data.columns[-1])

    data.columns = ['school_major_name', 'enrollment', 'avg_score', 'min_score_rank']

    return_df = pd.DataFrame(columns=['school_name', 'group_code', 'major_name', 'enrollment', 'avg_score', 'min_score', 'min_rank'], index=range(200))
    row_id = 0
    for num in range(len(data)):
        if data.notna().at[num, 'school_major_name']:

            if '组)' in data['school_major_name'][num]:
                temp_str = data['school_major_name'][num].split("\n")
                temp_group_name = temp_str[0]
                i = 1
                while temp_group_name[-2:] != '组)':

                    temp_group_name += temp_str[i]
                    i += 1

                group_code = temp_group_name.rstrip("*")[temp_group_name.rfind("(") + 1: -1]
                school_name = temp_group_name.replace("({})".format(group_code), "")

            else:
                if type(return_df['major_name'][row_id]) != float:
                    row_id += 1
                if data.isna().at[num, 'avg_score'] or get_chinese(data['avg_score'][num]):
                    pass
                else:
                    return_df['school_name'][row_id] = school_name
                    return_df['group_code'][row_id] = group_code
                    return_df['major_name'][row_id] = data['school_major_name'][num]
                    return_df['enrollment'][row_id] = data['enrollment'][num]
                    return_df['avg_score'][row_id] = data['avg_score'][num]
                    return_df['min_score'][row_id] = data['min_score_rank'][num].split("\n")[0]
                    return_df['min_rank'][row_id] = data['min_score_rank'][num].split("\n")[1]
    return return_df[:row_id]


if __name__ == '__main__':
    path = r"D:\桌面\天津分数图片"
    df = pd.DataFrame()
    for subject_name in get_file(path):

        for batch_name in get_file(path + '/' + subject_name):

            for page in tqdm(get_file(path + '/' + subject_name + '/' + batch_name)):
                page_path = path + '/' + subject_name + '/' + batch_name + '/' + page
                data_df = main(page_path)
                last_df = handle_data(data_df)
                last_df['page'] = page
                last_df['subject_name'] = subject_name
                last_df['batch_name'] = batch_name
                df = pd.concat([df, last_df])
                last_df.to_excel(r"D:\桌面\天津分数Excel\{}.xlsx".format(page), index=False)

    df.to_excel(r"D:\桌面\天津2023年招生计划（本科批）.xlsx", index=False)
