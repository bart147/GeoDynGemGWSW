# %%
import pandas as pd
# %%
df = pd.read_excel(r"G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\inp_fields.xlsx", engine="openpyxl")
df.to_csv(r"G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\inp_fields.csv", sep=";")
print ('done!')
# %%