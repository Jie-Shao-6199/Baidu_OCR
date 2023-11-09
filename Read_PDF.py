"""
直接可读取的PDF文件
"""
import fitz
from PyPDF2 import PdfReader
import re
import pandas as pd
from tqdm import tqdm
from txdpy import is_num, is_chinese, is_num_letter, get_num, get_chinese


school_code = school_name = group_code = group_name = subject_name = ''


def has_symbol(string):
    """
    检测字符串是否有标点符号
    :param string: 字符串
    :return: bool
    """
    pattern = r'[\W\sa-zA-Z_]'
    if re.search(pattern, string):
        return True
    else:
        return False


def main(path):
    """
    主函数
    :return:
    """


def all_to_half(all_string):
    """全角转半角"""
    half_string = ""
    for char in all_string:
        inside_code = ord(char)
        if inside_code == 12288:  # 全角空格直接转换,全角和半角的空格的Unicode值相差12256
            inside_code = 32
        elif 65281 <= inside_code <= 65374:  # 全角字符（除空格）根据关系转化,除空格外的全角和半角的Unicode值相差65248
            inside_code -= 65248

        half_string += chr(inside_code)
    return half_string


def read_pdf(page_text):
    """
    取出每一行内容，进行后续操作
    :param page_text:
    :return:
    """
    temp_str = page_text.get_text("")
    # print([temp_str])
    # temp_str = re.sub(" +", " ", temp_str).strip()
    last_str = ''
    last_list = []

    temp_list = re.split("\n", temp_str)
    for li in temp_list:
        if len(li) > 0:
            if li[0] == '\u3000':  # 专业前面都有两个\u3000
                if last_str != '':
                    last_list.append(last_str)
                chinese_index = 0
                temp_index = 0
                for i in range(len(li)):
                    if is_chinese(li[i]):
                        chinese_index = i
                        break

                for j in range(len(li)):
                    if j > chinese_index and is_num(all_to_half(li[j])) and (is_num(all_to_half(li[j])) or li[j] == ' '):
                        temp_index = j
                        break
                if '年' in li and li[-1].isdigit() and ' 年 ' not in li:
                    last_str = all_to_half(re.sub(" ", "_", re.sub("\u3000", "", li[:chinese_index])) + re.sub(" ", "", li[chinese_index:temp_index]) + re.sub(" ", "_", li[temp_index:]))
                else:
                    last_str = all_to_half(re.sub(" ", "_", re.sub("\u3000", "", li[:chinese_index])) + re.sub(" ", "", li[chinese_index:]))

            elif '年' in li and len(li) >= 6 and len("".join(get_num(all_to_half(li)))) >= 2 and len("".join(get_chinese(li))) <= 3:
                if all_to_half(li[0]).isdigit() and all_to_half(li[-1]).isdigit():
                    last_str += "_{}".format(all_to_half(re.sub(" ", "_", li)))
                elif all_to_half(li[-1]).isdigit():
                    num_index = None
                    for i in range(len(li)):
                        if i + 1 < len(li) and all_to_half(li[i]).isdigit() and (li[i + 1].isdigit() or li[i + 1] == ' ') and '年' in li[i:]:
                            num_index = i
                            break

                    if num_index:
                        last_str += all_to_half(li[:num_index] + re.sub(" ", "_", li[num_index:]))
                else:

                    last_str += all_to_half(li)

            elif is_num_letter(all_to_half(li[:4])) and len(li) > 5 and (li[4] == ' ' or is_chinese(li[4])):

                if last_str != '':
                    last_list.append(last_str)
                last_str = all_to_half(re.sub(" ", "_", li[:6]) + re.sub(" ", "", li[6:]))

            elif '注:' in li or (':' in li and '名' in li):

                if last_str != '':
                    last_list.append(last_str)
                last_str = all_to_half(re.sub(" ", "", li))
            else:
                last_str += all_to_half(re.sub(" ", "", li))

    last_list.append(last_str)
    finish_list = []
    for txt in last_list:
        if txt[0] == '_':
            txt = txt[1:]
        finish_list.append(re.split("_", txt))

    return finish_list


def handle_data(temp_list: list, len_school_code, len_major_code, columns: list,
                len_group_code=None):
    """
    将各行内容进行分列，把各自放到各自的列
    :param columns:  该省份的列数
    :param len_major_code:  专业代码长度
    :param len_school_code: 学校代码长度
    :param len_group_code: 专业组代码长度（默认：None）
    :param temp_list: 需要处理的每一行数据列表
    :return:
    """
    
    global school_code, school_name, group_code, group_name, subject_name
    last_dict = []
    for li in temp_list:
        # print(li, len(li))
        temp_dict = {}
        for s in range(len(li)):
            temp_dict['words{}'.format(s)] = all_to_half(li[s])
        last_dict.append(temp_dict)
    last_df = pd.DataFrame(columns=['batch_name', 'subject_name', 'school_code', 'school_name', 'group_code', 'group_name', 'major_code', 'major_name', 'major_num', 'edu_year', 'cost_year', 'remark'], index=range(200))
    df = pd.DataFrame(last_dict)
    df.columns = columns
    row_id = 0
    for i in range(len(df)):
        if is_num_letter(df['school_major_code'][i]):
            if len(df['school_major_code'][i]) == len_major_code:

                if type(last_df['major_name'][row_id]) != float:
                    row_id += 1
                # print(last_df.columns)
                last_df['school_code'][row_id] = school_code
                last_df['school_name'][row_id] = school_name
                last_df['major_code'][row_id] = df['school_major_code'][i]
                last_df['major_name'][row_id] = df['school_major_name'][i]
                last_df['subject_name'][row_id] = subject_name
                if len_group_code:
                    last_df['group_code'][row_id] = group_code
                    last_df['group_name'][row_id] = group_name
                if is_num(df['major_num'][i]):
                    last_df['major_num'][row_id] = df['major_num'][i]
                    if type(df['edu_year'][i]) != float and len(df['edu_year'][i]) <= 3 and '年' in df['edu_year'][i]:
                        last_df['edu_year'][row_id] = df['edu_year'][i]
                        last_df['cost_year'][row_id] = df['cost_year'][i]
                    else:
                        pass
                elif is_chinese(df['major_num'][i]) and len(df['major_num'][i]) <= 3 and '年' in df['major_num'][i]:
                    if len(df['school_major_name'][i]) >= 3:
                        # print()
                        last_df['major_num'][row_id] = "".join(get_num(df['school_major_name'][i][int(len(df['school_major_name'][i])/2):]))
                    elif is_num(df['school_major_name'][i]):
                        last_df['major_num'][row_id] = df['school_major_name'][i]
                    else:
                        pass

                    last_df['edu_year'][row_id] = df['major_num'][i]
                    last_df['cost_year'][row_id] = df['edu_year'][i]

                else:
                    # last_df['major_name'][row_id] += df['school_major_name'][i]
                    pass
            elif len(df['school_major_code'][i]) == len_school_code:
                school_code = df['school_major_code'][i]
                school_name = df['school_major_name'][i]
            elif len_group_code and len(df['school_major_code'][i]) == len_group_code:
                group_code = df['school_major_code'][i]
                group_name = df['school_major_name'][i]
            else:
                pass

        elif '理工类' in df['school_major_code'][i]:
            subject_name = '理科'
        elif'文史类' in df['school_major_code'][i]:
            subject_name = '文科'
        elif df['school_major_code'][i][:2] == '注:':
            last_df['remark'][row_id] = df['school_major_code'][i]
        else:
            pass

    # print(df)
    # df.to_excel(r'D:\桌面\黑龙江2023年招生计划.xlsx', index=False)
    return last_df[:row_id + 1]


if __name__ == '__main__':
    pdf_file = fitz.open(r"D:\桌面\黑龙江2023年招生计划-纯净版.pdf")
    data_df = pd.DataFrame()
    for page in range(len(pdf_file)):
        text = pdf_file[page]
        return_list = read_pdf(text)
        pd_columns = ['school_major_code', 'school_major_name', 'major_num', 'edu_year', 'cost_year']  # 黑龙江
        return_df = handle_data(return_list, 4, 2, pd_columns)
        # print(len(return_df.columns), page)  # 检测一下是不是列数一致
        return_df.to_excel(r"D:\桌面\hlj\{}.xlsx".format(page), index=False)
        data_df = pd.concat([data_df, return_df], ignore_index=True)

    data_df.to_excel(r"D:\桌面\黑龙江2023年招生计划.xlsx", index=False)

