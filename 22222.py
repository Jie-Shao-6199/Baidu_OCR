import pandas as pd
tmp_nan = ['nan' for _ in range(10)]
inde = [i for i in range(1)]
return_df = pd.DataFrame({'batch_name': [0], 'subject_name': [0], 'school_code': [0], 'school_name': [0], 'major_code': [0],
                                  'major_name': [0], 'select_require': [0], 'edu_year': [0], 'plan_num': [0], 'cost_year': [0]})
return_df['page'] = 29
print(return_df)
