import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import re
import nltk
#
# df = pd.read_csv("testing_reviews.csv") # this is 13k. THIS SEEMS TOO SMALL! Slightly worrying
#
# print(df.isnull().sum())
# print(len(pd.unique(df["job_location"])))
# print(len(pd.unique(df["company_name"]))) #2.6k unique companies for the larger df
# print(df.columns)


df = pd.read_csv("reviews.csv") # this is 8k



df = df[(df["company_name"]!="*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]") & (df["company_info"].isnull()!=True)]
print((df["company_name"]=="*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]").sum())
print(df["company_info"].isnull().sum())
# print(df["company)info"].contains(">").sum())
print(len(df))
df.dropna()
print(len(df))

print(df.columns.values)
df["company_info"] = df["company_info"].apply(eval)
df["company_info"] = pd.Series([dict(i) for i in df["company_info"]])
df = pd.concat([df.drop('company_info', axis = 1), df["company_info"].apply(pd.Series)], axis = 1)
print(df.columns.values)

df.isnull().sum()
print(len(pd.unique(df["job_location"])))
print(len(pd.unique(df["company_name"]))) #well that isn't a lot
print(len(pd.unique(df["Industry"])))
print(len(pd.unique(df["Type"])))
print(len(pd.unique(df["Size"])))

print(df["Now known as "])

for i in np.where(np.logical_or(df["Part of "] == "",df["Now known as "] == "")):
    df.loc[i, "Founded"] = df.loc[i,"Type"]
    df.loc[i,"Type"] = df.loc[i,"Industry"]
    df.loc[i,"Industry"] = df.loc[i,"Revenue"]
    df.loc[i,"Revenue"] = df.loc[i,"Competitors"]
    df.loc[i, "Part of "] = np.nan
    df.loc[i,"Competitors"] = np.nan

# for i in np.where(df["Now known as "] == ""):
#     df.loc[i, "Founded"] = df.loc[i, "Type"]
#     df.loc[i, "Type"] = df.loc[i, "Industry"]
#     df.loc[i, "Industry"] = df.loc[i, "Revenue"]
#     df.loc[i, "Revenue"] = df.loc[i, "Competitors"]
#     df.loc[i, "Part of "] = np.nan
#     df.loc[i, "Competitors"] = np.nan

print(df.isnull().sum())

df = df.drop(["Now known as ", "Part of ", "post_date"], axis = 1)


df["Type"] = [("Company - Public") if i[:16] == "Company - Public" else i for i in df["Type"]]
df["salary_est"] = [int(i.replace("$","").replace(",","")) for i in df["salary_est"]]
def make_thousands(column):
    column = [int(i.replace("$","").replace("k",""))*1000 for i in column]
    return(column)

df["salary_high"] = make_thousands(df["salary_high"])
df["salary_low"] = make_thousands(df["salary_low"])
print(df.columns)

distinct_df = df.drop_duplicates(["company_name", "description", "job_location", "job_title"])
distinct_df = distinct_df.drop(["company_cons", "company_pros", "outlook", "recommend", "Headquarters"], axis = 1)

numbers = dict({1:"one", 2:"two", 3:"three", 4:"four", 5:"five", 6:"six", 7:"seven", 8:"eight", 9:"nine", 10:"ten", 11:"eleven"})
#reg salary, industry, years_exp, skills, education, job_location, type, rating
re.search("year",distinct_df["description"])-5
print(df.columns)

test = distinct_df["description"].loc[range(6),:]
print(len(df))
#anything with a "" in type should have revenue moved to industry
#type to founded, industry moved to type, competitors moved to revenue

#cahnge revenue into ints, make the high and low thousands instead of k's, get rid of $ for all