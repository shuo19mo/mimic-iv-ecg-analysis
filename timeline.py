# 重新导入 pandas 和 gzip 并等待用户上传文件
import pandas as pd
import numpy as np
import gzip

# 读取 admissions.csv
admissions_file = "admissions.csv"
admissions_df = pd.read_csv(admissions_file)

# 读取 icustays.csv.gz
icustays_file = "icustays.csv.gz"
with gzip.open(icustays_file, 'rt', encoding='utf-8') as f_in:
    icustays_df = pd.read_csv(f_in)

# 读取 updated_record_list.csv (ECG 记录，包含 hadm_id)
updated_record_list_file = "updated_record_list.csv"
updated_record_list_df = pd.read_csv(updated_record_list_file)

# 转换时间格式
time_columns = ['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime']
for col in time_columns:
    admissions_df[col] = pd.to_datetime(admissions_df[col], errors='coerce')

icustays_df['intime'] = pd.to_datetime(icustays_df['intime'], errors='coerce')
icustays_df['outtime'] = pd.to_datetime(icustays_df['outtime'], errors='coerce')
updated_record_list_df['ecg_time'] = pd.to_datetime(updated_record_list_df['ecg_time'], errors='coerce')

# **1️⃣ 随机选择 20 个病人**
random_subjects = np.random.choice(admissions_df['subject_id'].unique(), 20, replace=False)

# 过滤数据
admissions_sample = admissions_df[admissions_df['subject_id'].isin(random_subjects)]
icustays_sample = icustays_df[icustays_df['subject_id'].isin(random_subjects)]
ecg_sample = updated_record_list_df[updated_record_list_df['subject_id'].isin(random_subjects)]

# **2️⃣ 直接按 `hadm_id` 匹配 ECG 数据**
merged_df = (
    admissions_sample
    .merge(icustays_sample, on=['subject_id', 'hadm_id'], how='left')  # 住院 & ICU
    .merge(ecg_sample[['subject_id', 'hadm_id', 'ecg_time']], on=['subject_id', 'hadm_id'], how='left')  # 住院 & ECG
)

# **3️⃣ 选取需要的列**
merged_df = merged_df[
    ['subject_id', 'hadm_id', 'admittime', 'dischtime', 'deathtime',
     'edregtime', 'edouttime', 'intime', 'outtime', 'ecg_time']
].rename(columns={'intime': 'icu_admit', 'outtime': 'icu_discharge'})

# **4️⃣ 统一排序，保证时间线正确**
merged_df = merged_df.sort_values(by=['subject_id', 'admittime', 'icu_admit', 'ecg_time'])

# **5️⃣ 优化打印输出，去掉 NaT**
for subject_id, group in merged_df.groupby('subject_id'):
    has_icu = group['icu_admit'].notna().any()
    has_ecg = group['ecg_time'].notna().any()
    has_ed = group['edregtime'].notna().any()
    
    print(f"\n==== Patient {subject_id} Timeline ====")
    
    if not has_icu and not has_ecg and not has_ed:
        print("  - ⚠️ No ICU, ED, or ECG records for this patient.")
    
    for _, row in group.iterrows():
        print(f"  - Hospital Admission: {row['admittime']}")
        if pd.notna(row['edregtime']):
            print(f"  - ED Entry: {row['edregtime']}")
        if pd.notna(row['edouttime']):
            print(f"  - ED Exit: {row['edouttime']}")
        if pd.notna(row['icu_admit']):
            print(f"  - ICU Admission: {row['icu_admit']}")
        if pd.notna(row['icu_discharge']):
            print(f"  - ICU Discharge: {row['icu_discharge']}")
        if pd.notna(row['ecg_time']):
            print(f"  - ECG Recording: {row['ecg_time']}")
        print(f"  - Hospital Discharge: {row['dischtime']}")
        if pd.notna(row['deathtime']):
            print(f"  - Death Time: {row['deathtime']}")
