import pandas as pd

# 加载CSV文件
echo_record_list = pd.read_csv("echo-record-list.csv")
admissions = pd.read_csv("admissions.csv")

# 转换时间格式
echo_record_list['acquisition_datetime'] = pd.to_datetime(echo_record_list['acquisition_datetime'], errors='coerce')
admissions['admittime'] = pd.to_datetime(admissions['admittime'], errors='coerce')
admissions['dischtime'] = pd.to_datetime(admissions['dischtime'], errors='coerce')

# 初始化 hadm_id 列
echo_record_list['hadm_id'] = None

# 匹配 hadm_id
for index, record in echo_record_list.iterrows():
    subject_id = record['subject_id']
    acquisition_time = record['acquisition_datetime']

    # 筛选相同 subject_id 的住院记录
    subject_admissions = admissions[admissions['subject_id'] == subject_id]

    # 找到符合时间范围的 hadm_id
    matching_admission = subject_admissions[
        (subject_admissions['admittime'] <= acquisition_time) &
        (subject_admissions['dischtime'] >= acquisition_time)
    ]

    # 赋值 hadm_id
    if not matching_admission.empty:
        echo_record_list.at[index, 'hadm_id'] = matching_admission.iloc[0]['hadm_id']

# 保存结果
echo_record_list.to_csv("updated_echo_record_list.csv", index=False)
