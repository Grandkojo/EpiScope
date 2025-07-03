import pandas as pd

# Load your dataset
df = pd.read_csv("artifacts/csv/health_data_eams_diabetes.csv")

# diabetes
# new_df[0:170]
# new_df[170:278]
# new_df[278:380]
# new_df[380:513]
# new_df[513:573]
# new_df[573:621]
# new_df[621:673]
# new_df[673:740]
# new_df[740:794]
# new_df[794:836]
# new_df[836:886]
# new_df[886:926]

#malaria
# p_df[0:113]
# p_df[113:430]
# p_df[430:563]
# p_df[563:683]
# p_df[683:810]
# p_df[810:992]
# p_df[992:1150]
# p_df[1150:1303]
# p_df[1303:1351]
# p_df[1351:1446]
# p_df[1446:1503]
# p_df[1503:1578]

# Assign collection month based on row index ranges (adjust as needed)
df.loc[0:99, 'CollectionMonth'] = '2022-03'
df.loc[100:199, 'CollectionMonth'] = '2022-06'
df.loc[200:299, 'CollectionMonth'] = '2022-09'
df.loc[300:, 'CollectionMonth'] = '2022-12'

# Save updated dataset
df.to_csv("artifacts/csv/health_data_eams_diabetes_time_stamped.csv", index=False)
