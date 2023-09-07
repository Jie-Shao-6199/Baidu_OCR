import pandas as pd

# 创建一个示例DataFrame
data = {'A': [1, 2, 3],
        'B': [4, 5, 6]}

df = pd.DataFrame(data)

# 要插入的新行数据
new_row_data = {'A': [7, 9], 'B': [8, 9]}

# 插入新行数据在第2行之后
index_to_insert_after = 1
df = pd.concat([df.iloc[:index_to_insert_after + 1], pd.DataFrame(new_row_data, index=[0, 0]), df.iloc[index_to_insert_after + 1:]])
# df = pd.concat([df.iloc[:index_to_insert_after + 2], pd.DataFrame(new_row_data, index=[0]), df.iloc[index_to_insert_after + 2:]])
# .reset_index(drop=True)
# 打印结果
print(df)