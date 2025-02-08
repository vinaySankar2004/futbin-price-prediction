import pandas as pd

# Manually list all filenames in the desired order
all_filenames = [
    "futbin_data_final_1_to_9.csv",
    "futbin_data_final_10_to_172.csv",
    "futbin_data_final_173_to_182.csv",
    "futbin_data_final_183_to_344.csv",
    "futbin_data_final_345_to_354.csv",
    "futbin_data_final_355_to_516.csv",
    "futbin_data_final_517_to_527.csv",
    "futbin_data_final_528_to_688.csv",
    "futbin_data_final_689_to_698.csv",
    "futbin_data_final_699_to_859.csv",
    "futbin_data_final_860_to_860.csv"
]

# Combine all files in the list
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

# Export to a single CSV file
combined_csv.to_csv("futbin_data_combined.csv", index=False, encoding='utf-8-sig')
