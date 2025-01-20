import pandas as pd

print("Script is starting...")

# Step 1: Load the CSV files into DataFrames
print("Loading CSV files...")
record_list = pd.read_csv("record_list.csv")
print(f"Loaded 'record_list.csv' with {len(record_list)} rows.")
admissions = pd.read_csv("admissions.csv")
print(f"Loaded 'admissions.csv' with {len(admissions)} rows.")

# Step 2: Convert date columns to datetime format for proper comparison
print("Converting date columns to datetime format...")
record_list['ecg_time'] = pd.to_datetime(record_list['ecg_time'], errors='coerce')
admissions['admittime'] = pd.to_datetime(admissions['admittime'], errors='coerce')
admissions['dischtime'] = pd.to_datetime(admissions['dischtime'], errors='coerce')
print("Date columns converted.")

# Step 3: Initialize a new column for hadm_id
print("Initializing 'hadm_id' column...")
record_list['hadm_id'] = None

# Step 4: Match each ECG record to a hospital admission
print("Matching ECG records to hospital admissions...")
for index, ecg in record_list.iterrows():
    if index % 1000 == 0:  # Print progress every 1000 rows
        print(f"Processing row {index}/{len(record_list)}...")

    subject_id = ecg['subject_id']
    ecg_time = ecg['ecg_time']

    # Filter admissions for the same subject_id
    subject_admissions = admissions[admissions['subject_id'] == subject_id]

    # Find the matching admission based on ecg_time
    matching_admission = subject_admissions[
        (subject_admissions['admittime'] <= ecg_time) &
        (subject_admissions['dischtime'] >= ecg_time)
    ]

    # If a match is found, assign the hadm_id
    if not matching_admission.empty:
        record_list.at[index, 'hadm_id'] = matching_admission.iloc[0]['hadm_id']

print("Finished matching ECG records.")

# Step 5: Save the updated record_list to a new CSV file
output_file = "updated_record_list.csv"
print(f"Saving updated record list to '{output_file}'...")
record_list.to_csv(output_file, index=False)
print(f"Updated record list saved to '{output_file}'.")

print("Script completed successfully.")
