"""
直接可读取的PDF文件
"""
import re

import numpy as np
import pandas as pd
import pdfplumber
from tqdm import tqdm

school_name = group_code = group_name = select_require = ''


def handle_data(data: pd.DataFrame):
    """
    处理Dataframe数据，形成最终格式
    :param data: 需要处理的数据
    :return: 最终的DataFrame
    """
    global school_name, group_name, group_code, select_require
    return_df = pd.DataFrame()

    data_no_nan_mask = data.notna()
    non_nan_count = data_no_nan_mask.sum(axis=1)

    for num in range(len(data)):

        if non_nan_count[num] == 2:

            school_name = data['group_major_code'][num]
        else:
            group_major_code = data['group_major_code'][num].split("\n")
            if data.notna().at[num, 'select_require']:
                select_require = data['select_require'][num]
            group_major_name = data['group_major_name'][num].split("\n")
            while '组' not in group_major_name[0] and len(group_major_code[0]) > 2:
                group_major_name = ["".join(group_major_name[:2])] + group_major_name[2:]
            edu_year = data['edu_year'][num].split("\n")

            if data.notna().at[num, 'plan_num']:
                plan_num = data['plan_num'][num].split("\n")
            else:
                plan_num = None

            if data.notna().at[num, 'cost_year']:
                cost_year = data['cost_year'][num].split("\n")
            else:
                cost_year = None

            if data.notna().at[num, 'language']:
                language = data['language'][num].split("\n")
            else:
                language = None

            if data.notna().at[num, 'oral_test']:
                oral_test = data['oral_test'][num].split("\n")
            else:
                oral_test = None

            remark = data['remark'][num].split("\n")

            temp_df = pd.DataFrame(
                columns=[
                    'school_name', 'group_code', 'group_name', 'select_require',
                    'major_code', 'major_name', 'edu_year', 'plan_num', 'cost_year',
                    'language', 'oral_test', 'remark']
            )
            if len(group_major_code) == len(edu_year):

                temp_df.set_index = range(len(group_major_code))
                temp_df['major_code'] = group_major_code
                if len(group_major_name) > len(group_major_code):
                    temp_name = ''
                    temp_list = []
                    for n in range(len(group_major_name)):
                        temp_name += group_major_name[n]
                        if (group_major_name[n][-1] == ")" and n + 1 < len(group_major_name)
                                and group_major_name[n + 1][0] != "(") or "(" not in temp_name:
                            temp_list.append(temp_name)
                            temp_name = ''
                    if temp_name != '':
                        temp_list.append(temp_name)
                    while len(temp_list) < len(group_major_code):
                        temp_list.append('')
                    temp_df['major_name'] = temp_list
                else:
                    temp_df['major_name'] = group_major_name
                temp_df['plan_num'] = plan_num

            else:
                temp_df.set_index = range(len(group_major_code) - 1)
                group_code = group_major_code[0]
                group_name = group_major_name[0]
                temp_df['major_code'] = group_major_code[1:]

                if len(group_major_name[1:]) > len(group_major_code[1:]):
                    temp_name = ''
                    temp_list = []
                    for n in range(len(group_major_name[1:])):
                        temp_name += group_major_name[1:][n]
                        if (group_major_name[1:][n][-1] == ")" and n + 1 < len(group_major_name[1:])
                                and group_major_name[1:][n + 1][0] != "(") or "(" not in temp_name:
                            temp_list.append(temp_name)
                            temp_name = ''
                    if temp_name != '':
                        temp_list.append(temp_name)
                    while len(temp_list) < len(group_major_code[1:]):
                        temp_list.append('')
                    temp_df['major_name'] = temp_list
                else:
                    temp_df['major_name'] = group_major_name[1:]

                temp_df['plan_num'] = plan_num[1:]

            temp_df['school_name'] = school_name
            temp_df['group_code'] = group_code
            temp_df['group_name'] = group_name
            temp_df['select_require'] = select_require
            temp_df['edu_year'] = edu_year

            while cost_year is not None and len(cost_year) < len(edu_year):
                cost_year.append('')

            temp_df['cost_year'] = cost_year

            while language is not None and len(language) < len(edu_year):
                language.append('')
            temp_df['language'] = language

            while oral_test is not None and len(oral_test) < len(edu_year):
                oral_test.append('')
            temp_df['oral_test'] = oral_test

            if data.isna().at[num, 'remark'] or len(remark) == len(edu_year):
                temp_df['remark'] = remark
            else:
                temp_df['remark'] = re.sub("\n", "", data['remark'][num])
            return_df = pd.concat([return_df, temp_df], ignore_index=True)
    return return_df


def main(pdf_file):
    """
    主函数
    :param pdf_file:文件地址
    :return:
    """
    # pdf_file = r"D:\桌面\天津2023年招生计划（本科批）.pdf"
    pdf = pdfplumber.open(pdf_file)
    last_df = pd.DataFrame()
    # # 遍历每一页
    for page in tqdm(pdf.pages):
        # 提取页面中的表格
        # 遍历提取的表格
        # page = pdf.pages[100]
        tables = page.extract_tables()
        df = pd.DataFrame()
        for table in tables[0][1:]:
            df = df.append(pd.Series(table), ignore_index=True)
        df.columns = ['group_major_code', 'select_require', 'group_major_name', 'edu_year', 'plan_num', 'cost_year',
                      'language', 'oral_test', 'remark']
        df.replace("", np.nan, inplace=True)
        return_df = handle_data(df)
        return_df['page'] = page
        last_df = pd.concat([last_df, return_df], ignore_index=True)
    last_df.to_excel(r"D:\桌面\天津2023年招生计划（本科批）.xlsx", index=False)


if __name__ == '__main__':
    main(r"D:\桌面\天津2023年招生计划（本科批）.pdf")
