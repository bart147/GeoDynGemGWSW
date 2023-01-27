# %%
import pandas as pd
# %%
df = pd.read_excel(r"..\inp_fields.xlsx", engine="openpyxl")
df.to_csv(r"..\inp_fields.csv", sep=";")
print ('done!')
# %%