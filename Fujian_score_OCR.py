import base64
import json
import urllib

from tqdm import tqdm

from Two_Page_OCR import get_file
import pandas as pd
import requests

API_KEY = "GGysNlmR9TrpFEch8YsMN88w"
SECRET_KEY = "AzFH8dGlUlndIlz3dGUXpShy3dxOYTrw"

school_name = group_name = ''


def main(path):
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

    # print(response.json()['tables_result'])
    get_bytes = response.json()['excel_file'].encode('utf-8')
    decoded_data = base64.b64decode(get_bytes)
    df = pd.read_excel(decoded_data)
    return df


def handle_data(data: pd.DataFrame):
    """
    对获取到的数据进行整理
    :param data: 识别出来的数据
    :return: 返回处理完的Excel表
    """
    global school_name, group_name
    return_df = pd.DataFrame(columns=['school_name', 'group_name'], index=range(200))

    pass_row = 0
    row_id = 0

    data_no_nan_mask = data.notna()
    non_nan_count = data_no_nan_mask.sum(axis=1)
    # print(non_nan_count)
    for num in range(len(data)):

        if num == pass_row:

            pass
        elif non_nan_count[num] == 1:
            if non_nan_count[num + 1] == 1:
                if type(data[data.columns[0]][num + 1]) != float and data[data.columns[0]][num + 1][:3].isdigit():

                    school_name = data[data.columns[0]][num]
                    group_name = data[data.columns[0]][num + 1]
                    pass_row = num + 1

                elif type(data[data.columns[1]][num + 1]) != float and data[data.columns[1]][num + 1][:3].isdigit():

                    school_name = data[data.columns[0]][num]
                    group_name = data[data.columns[1]][num + 1]
                    pass_row = num + 1

            else:
                if type(data[data.columns[0]][num]) != float and data[data.columns[0]][num][:3].isdigit():

                    group_name = data[data.columns[0]][num]

                elif type(data[data.columns[1]][num]) != float and data[data.columns[1]][num][:3].isdigit():

                    group_name = data[data.columns[1]][num]
        else:
            # if type(return_df['school_name'][row_id]) != float:
            #
            #     row_id += 1
            return_df.loc[row_id, 'school_name'] = school_name
            return_df.loc[row_id, 'group_name'] = group_name
            # return_df['school_name'][row_id] = school_name
            # return_df['group_name'][row_id] = group_name
            for column_num in range(len(data.columns)):
                C = data[data.columns[column_num]][num]
                if 'words{}'.format(column_num) not in return_df.columns:
                    return_df['words{}'.format(column_num)] = 0
                # return_df['words{}'.format(column_num)][row_id] = data[data.columns[column_num]][num]
                return_df.loc[row_id, 'words{}'.format(column_num)] = data[data.columns[column_num]][num]
            row_id += 1
    return_df = return_df[:row_id]
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
    path = r"D:\桌面\福建OCR"
    df = pd.DataFrame(columns=['batch_name', 'subject_name', 'school_name', 'group_name'])
    for subject_name in get_file(path):

        for batch_name in get_file(path + '/' + subject_name):

            for page in tqdm(get_file(path + '/' + subject_name + '/' + batch_name)):

                page_path = path + '/' + subject_name + '/' + batch_name + '/' + page

                old_data = main(page_path)
                last_df = handle_data(old_data)
                last_df['batch_name'] = batch_name
                last_df['subject_name'] = subject_name
                last_df['page'] = page
                last_df.to_excel(r"D:\桌面\福建Excel\{}-{}.xlsx".format(subject_name, page), index=False)
                df = pd.concat([df, last_df], ignore_index=True)
    # old_data = main(r"D:\桌面\页面提取自－2022年福建普通类本科批录取分数（历史）.pdf.jpg")

    df.to_excel(r"D:\桌面\福建2022年录取分数.xlsx", index=False)

