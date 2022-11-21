# %%
import csv
# %%
INP_FIELDS_CSV = r"G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\inp_fields.csv"
d_velden = {}
f = open(INP_FIELDS_CSV, encoding="ISO-8859-1")
input_file = csv.DictReader(f, delimiter=";")

for srow in input_file:
    if not srow["fieldname"]:
        continue

    fld = {}

    # verplichte keys
    fld["order"] = int(srow["order"])
    fld["field_type"] = srow["type"]
    fld["field_alias"] = srow["alias"]
    fld["add_fld"] = srow["stap_toevoegen"]
    # optionele keys
    if str(srow["mag_niet_0_zijn"]) != "nan": # np.nan, df.notna() werkt niet en np.isnan() not supported
        fld["mag_niet_0_zijn"] = str(srow["mag_niet_0_zijn"]).split(";")
    #else:
        # fix_print_with_import
        #print((type(srow["mag_niet_0_zijn"]),srow["mag_niet_0_zijn"]))
    if str(srow["lengte"]) not in ["nan", ""," "]:
        fld["field_length"] = int(srow["lengte"])
    if str(srow["expression"]) not in ["nan", ""," "]:
        fld["expression"] = srow["expression"]
    if str(srow["stap_bereken"]) not in ["nan", ""," "]:
        fld["bereken"] = srow["stap_bereken"]
    d_velden[srow["fieldname"]] = fld
f.close()
# %%
