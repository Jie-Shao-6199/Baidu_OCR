import math
import re

import PyPDF2
import numpy as np
import tabula
import pandas as pd
from tqdm import tqdm
from txdpy import is_num, is_chinese, is_num_letter, get_num, get_chinese

school_code = school_name = subject_name = select_require = group_name = ''


def get_num_index(temp_str: str):
    """
    用来找到第一个数字出现的位置
    :param temp_str: 传入字符串
    :return:
    """
    if get_num(temp_str):
        for i in range(len(temp_str)):

            if temp_str[i].isdigit():
                return i

    else:
        return False


def arrange_data(data: pd.DataFrame):
    """
    整理传入的Dataframe提取数据
    :param data:
    :return:
    """

    if len(data.columns) == 6:
        if not data.isna().at[0, 'words0'] and '代号' in data['words0'][0]:
            data['school_code_name'] = np.nan
            temp_columns = ['school_code_name'] + list(data)[:-1]
            data = data[temp_columns]
            data = data.drop(index=0)
            data = data.reset_index(drop=True)

            for i in range(len(data)):
                if type(data['words0'][i]) != float:
                    if data['words0'][i][:4].isdigit() and len(data['words0'][i]) >= 4:

                        if '专业组' in data['words0'][i]:
                            data.loc[i, 'school_code_name'] = re.sub(" ", "", data['words0'][i][:4])
                            data.loc[i, 'words0'] = re.sub(" ", "", data['words0'][i][4:])
                        elif '专业组' in data['words1'][i]:
                            data['school_code_name'][i] = data['words0'][i]
                            data['words0'][i] = data['words1'][i]
                        else:
                            print('看看是啥')

                    elif '招生章程网址' in data['words0'][i]:

                        if data['words0'][i][:6] == '招生章程网址':
                            data.loc[i, 'school_code_name'] = data['words0'][i - 1] + '\r' + data['words0'][i]
                            data.loc[i, 'words0'] = np.nan
                            data = data.drop(index=i - 1)

                        else:
                            if get_num_index(data['words0'][i]):

                                num_index = get_num_index(data['words0'][i])
                                data['school_code_name'][i] = data['words0'][i][: num_index] + '\r' + data['words0'][i][
                                                                                                          num_index:]
                                data['school_code_name'][i] = re.sub("\r\r", "\r", data['school_code_name'][i])
                            else:
                                print('再看一眼')
        else:
            data['remark'] = np.nan
            for j in range(len(data)):

                if type(data['words0'][j]) == str and '招生章程网址' in data['words0'][j]:
                    if data['words0'][j][:6] == '招生章程网址':
                        data.loc[j, 'words0'] = data['words0'][j - 1] + '\r' + data['words0'][j]
                        # data.loc[j, 'words0'] = np.nan
                        data = data.drop(index=j - 1)

                    else:
                        if get_num_index(data['words0'][j]):

                            num_index = get_num_index(data['words0'][j])
                            data.loc[j, 'words0'] = data['words0'][j][:num_index] + '\r' + data['words0'][j][
                                                                                                      num_index:]
                            data.loc[j, 'words0'] = re.sub("\r\r", "\r", data['words0'][j])
                        else:
                            print('再看一眼2')
    elif len(data.columns) < 6:
        data = pd.DataFrame({'school_code_name': [0], 'major_group_code': [0], 'major_name': [0], 'edu_year': [0], 'plan_num': [0],
                                     'cost_year': [0], 'remark': [0]})
    else:
        for s in range(len(data)):

            if type(data['words0'][s]) == str and '招生章程网址' in data['words0'][s]:
                if data['words0'][s][:6] == '招生章程网址':
                    data.loc[s, 'words0'] = data['words0'][s - 1] + '\r' + data['words0'][s]
                    # data.loc[j, 'words0'] = np.nan
                    data = data.drop(index=s - 1)

                else:
                    if get_num_index(data['words0'][s]):

                        num_index = get_num_index(data['words0'][s])
                        data.loc[s, 'words0'] = data['words0'][s][:num_index] + '\r' + data['words0'][s][
                                                                                       num_index:]
                        data.loc[s, 'words0'] = re.sub("\r\r", "\r", data['words0'][s])
                    else:
                        print('再看一眼3')
    data.columns = ['school_code_name', 'major_group_code', 'major_name', 'edu_year', 'plan_num', 'cost_year', 'remark']
    data = data.reset_index(drop=True)
    for i in range(len(data)):

        if data.notna().at[i, 'school_code_name']:
            c = data['school_code_name'][i]
            b = str(data['school_code_name'][i]).split(".")[0]
            data.loc[i, 'school_code_name'] = str(data['school_code_name'][i]).split(".")[0]

    return data


def handle_data(data: pd.DataFrame, ):
    """
    处理Dataframe数据，形成最终格式
    :param data: 需要处理的数据
    :return: 最终的DataFrame
    """
    global school_code, school_name, group_name, subject_name, select_require
    final_df = pd.DataFrame(columns=['school_code', 'school_name', 'group_name', 'subject_name', 'select_require',
                                     'major_code', 'major_name', 'edu_year', 'plan_num', 'cost_year', 'remark'])
    data_no_nan_mask = data.notna()
    non_nan_count = data_no_nan_mask.sum(axis=1)
    # c = len(data)
    if len(data) == 1 and data['school_code_name'][0] == '0':
        final_df = pd.DataFrame(
            {'school_code': [0], 'school_name': [0], 'group_name': [0], 'subject_name': [0], 'select_require': [0],
                'major_code': [0], 'major_name': [0], 'edu_year': [0], 'plan_num': [0],
             'cost_year': [0], 'remark': [0]})
    else:
        for num in range(len(data)):

            if not data.isna().at[num, 'school_code_name']:

                if len(data['school_code_name'][num]) == 4 and data['school_code_name'][num].isdigit() \
                        and '专业组' in data['major_group_code'][num]:

                    school_code = data['school_code_name'][num]

                    if '不限' not in data['major_group_code'][num]:
                        select_index = data['major_group_code'][num].index('选考')

                        group_name = data['major_group_code'][num][: select_index - 1]
                        select_require = data['major_group_code'][num][select_index + 2: -1]
                    else:
                        select_index = data['major_group_code'][num].index('不限')
                        group_name = data['major_group_code'][num][: select_index - 1]
                        select_require = "不限"

                elif '招生章程网址' in data['school_code_name'][num]:
                    school_name = data['school_code_name'][num].split("\r")[0]

            elif not data.isna().at[num, 'major_group_code']:
                if '\r' in data['major_group_code'][num]:
                    major_code = data['major_group_code'][num].split("\r")
                    major_name = data['major_name'][num].split("\r")
                    edu_year = data['edu_year'][num].split("\r")
                    plan_num = data['plan_num'][num].split("\r")
                    if not data.isna().at[num, 'cost_year'] and not get_num(data['cost_year'][num]) and data['cost_year'][num] != '免费':
                        remark = data['cost_year'][num].split("\r")
                        cost_year = np.nan
                    elif data.isna().at[num, 'cost_year']:
                        cost_year = data['cost_year'][num]
                    else:
                        cost_year = data['cost_year'][num].split("\r")
                    if not data.isna().at[num, 'remark']:
                        remark = data['remark'][num].split("\r")
                    else:
                        remark = data['remark'][num]

                    temp_df = pd.DataFrame(
                        columns=['school_code', 'school_name', 'group_name', 'subject_name', 'select_require',
                                 'major_code', 'major_name', 'edu_year', 'plan_num', 'cost_year', 'remark'],
                        index=range(len(major_code)))
                    temp_df['school_code'] = school_code
                    temp_df['school_name'] = school_name
                    temp_df['group_name'] = group_name
                    temp_df['subject_name'] = subject_name
                    temp_df['select_require'] = select_require
                    temp_df['major_code'] = major_code

                    if len(major_name) > len(major_code):
                        temp_name = ''
                        temp_list = []
                        for n in range(len(major_name)):
                            temp_name += major_name[n]
                            if ((major_name[n][-1] == ")" or major_name[n][-1] == "]") and n + 1 < len(major_name)
                                and major_name[n + 1][0] != "[" and major_name[n + 1][0] != "(")\
                                    or "(" not in temp_name:
                                temp_list.append(temp_name)
                                temp_name = ''
                        if temp_name != '':
                            temp_list.append(temp_name)
                        while len(temp_list) < len(major_code):
                            temp_list.append('')
                        temp_df['major_name'] = temp_list
                    else:
                        temp_df['major_name'] = major_name
                    while len(edu_year) < len(major_code):
                        edu_year.append('')
                    temp_df['edu_year'] = edu_year
                    temp_df['plan_num'] = plan_num
                    if type(cost_year) == float or (type(cost_year) != list and math.isnan(cost_year)) or len(cost_year) == len(major_code):
                        temp_df['cost_year'] = cost_year

                    else:
                        while len(cost_year) < len(major_code):

                            cost_year.append('')
                            temp_df['cost_year'] = cost_year

                    if (type(remark) != list and math.isnan(remark)) or len(remark) == len(major_code):
                        temp_df['remark'] = remark
                    elif len(remark) > len(major_code):
                        temp_df['remark'] = "".join(remark)

                    else:
                        while len(remark) < len(major_code):
                            remark.append('')
                        temp_df['remark'] = remark
                    final_df = pd.concat([final_df, temp_df], ignore_index=True)
                else:
                    temp_df = pd.DataFrame(
                        columns=['school_code', 'school_name', 'group_name', 'subject_name', 'select_require',
                                 'major_code', 'major_name', 'edu_year', 'plan_num', 'cost_year', 'remark'],
                        index=range(1))
                    temp_df['school_code'] = school_code
                    temp_df['school_name'] = school_name
                    temp_df['group_name'] = group_name
                    temp_df['subject_name'] = subject_name
                    temp_df['select_require'] = select_require
                    temp_df['major_code'] = data['major_group_code'][num]
                    if type(data['major_name'][num]) == str:
                        data.loc[num, 'major_name'] = re.sub("[\r ]", "", data['major_name'][num])
                    temp_df['major_name'] = data['major_name'][num]
                    temp_df['edu_year'] = data['edu_year'][num]
                    temp_df['plan_num'] = data['plan_num'][num]
                    temp_df['cost_year'] = data['cost_year'][num]
                    temp_df['remark'] = data['remark'][num]
                    final_df = pd.concat([final_df, temp_df], ignore_index=True)
            else:
                if non_nan_count[num] == 1 and not data.isna().at[num, 'remark']:
                    a = final_df['remark'][len(final_df) - 1]
                    b = data['remark'][num]
                    final_df.loc[len(final_df) - 1, 'remark'] += data['remark'][num]
    # print(final_df)
    return final_df


def main(pdf_file):
    """
    主函数
    :param pdf_file: 指定要读取的PDF文件的路径
    :return:
    """

    # 获取PDF文件的总页数
    with open(pdf_file, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        total_pages = len(pdf.pages)

    # 初始化一个空的DataFrame来保存表格数据
    excel = pd.DataFrame()

    # 逐页读取表格
    for page in tqdm(range(1, total_pages+1)):
        # 使用Tabula来读取当前页的表格
        tables = tabula.read_pdf(pdf_file, pages=page)

        # 处理每一页的表格，类似你之前的代码
        for table in tables:
            for column in table.columns[1:]:
                if table[column][1:].notna().sum() < 1:
                    table.drop(column, axis=1, inplace=True)
            table.columns = ["words{}".format(i) for i in range(len(table.columns))]

            # 将当前页的表格数据添加到excel DataFrame中
            # excel = pd.concat([excel, table], ignore_index=True)
            unify_df = arrange_data(table)
            last_df = handle_data(unify_df)
            last_df['page'] = page
            excel = pd.concat([excel, last_df], ignore_index=True)

            # 将整个PDF中的表格数据保存到Excel文件
    excel.to_excel(r"D:\桌面\2023年福建省普通高校招生计划普通类历史-物理科目组-本科批.xlsx", index=False)


if __name__ == '__main__':
    main(r"D:\桌面\2023年福建省普通高校招生计划普通类历史-物理科目组-本科批.pdf")
