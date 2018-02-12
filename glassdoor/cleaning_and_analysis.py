import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import re
import spicy
import plotly
from plotly.graph_objs import Figure, Bar, Histogram, Layout, Scatter
import time
#
# df = pd.read_csv("./Scraped-data/testing_reviews.csv") # this is 13k
#
# print(df.isnull().sum())
# print(len(pd.unique(df["job_location"])))
# print(len(pd.unique(df["company_name"]))) #2.6k unique companies for the larger df
# print(df.columns)

# df = df[(df["company_name"]!="*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]") & (df["company_info"].isnull()!=True)]
# print((df["company_name"]=="*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]").sum())
# print(df["company_info"].isnull().sum())
# # print(df["company)info"].contains(">").sum())
# print(len(df))
# df.dropna()
# print(len(df))

###CLEANING DATA
df = pd.read_csv("./Scraped-data/reviews.csv") # this is 8k and has all rows filled in so do not need to drop "ERROR"s

print(df.columns.values)
# Company info is a string of a list of tuples, so we need to extract the first element and set that as the variable
# name and take the second element and put it at the variable name. First make it into a list of tuples
df["company_info"] = df["company_info"].apply(eval)
# turn that into a dictionary
df["company_info"] = pd.Series([dict(i) for i in df["company_info"]])
# flatten it and apply it to the proper columns
df = pd.concat([df.drop('company_info', axis = 1), df["company_info"].apply(pd.Series)], axis = 1)
# confirm that columns are correct
print(df.columns.values)

df.isnull().sum()
print("locations", len(pd.unique(df["job_location"])))   # 216 unique locations (this seems too high, likely due to typing errors in the data)
print("companies", len(pd.unique(df["company_name"])))   # 1.7k unique companies (makes sense, 5 reviews per company, making it 8.5k)
print("industries", len(pd.unique(df["Industry"])))
print("types", len(pd.unique(df["Type"])))           # formatting is off, hence the huge number of different types
print("sizes", len(pd.unique(df["Size"])))

# rearranging columsn that were messed up due to Ajax formatting in glassdoor.
# Occured when they contained links (not that many, so doesn't warrant a rescrape).
for i in np.where(np.logical_or(df["Part of "] == "",df["Now known as "] == "")):
    df.loc[i, "Founded"] = df.loc[i,"Type"]
    df.loc[i,"Type"] = df.loc[i,"Industry"]
    df.loc[i,"Industry"] = df.loc[i,"Revenue"]
    df.loc[i,"Revenue"] = df.loc[i,"Competitors"]
    df.loc[i, "Part of "] = np.nan
    df.loc[i,"Competitors"] = np.nan

print(df.isnull().sum())



df["Type"] = [("Company - Public") if i[:16] == "Company - Public" else i for i in df["Type"]]
print(df["Type"].unique())

df["salary_est"] = [int(i.replace("$","").replace(",","")) for i in df["salary_est"]]

# Objective: Turn columns that are in the thousands via strings "$93k" into the proper int format
# input: dataframe column filled with string ints with $ signs and k representing thousands
# output: dataframe column filled with ints
def make_thousands(column):
    column = [int(i.replace("$","").replace("k",""))*1000 for i in column]
    return(column)

# convert into ints
df["salary_high"] = make_thousands(df["salary_high"])
df["salary_low"] = make_thousands(df["salary_low"])

# For future analysis, we need unique jobs, so filtering on company names, description, location, and the title itself
distinct_df = df.drop_duplicates(["company_name", "description", "job_location", "job_title"])
# dropping columns that are person unique or unneeded in potential analyses
distinct_df = distinct_df.drop(["company_cons", "company_pros", "outlook", "recommend", "Headquarters"], axis = 1)

#reg salary, industry, years_exp, skills, education, job_location, type, rating
print(df.columns)

desc_col = distinct_df["description"]
desc_col = desc_col.reset_index(drop=True)
df = df.drop(["Now known as ", "Part of ", "post_date"], axis = 1)

## GATHERING INFORMATION BASED ON EDUATION LEVEL
# this is going through the lists extra times which is unnecessary (see below where converting into 1s and 0s.
# go back and clean this
bachelors = [re.findall("(?<![A-Z])B\.?S\.?c?(?![A-Z])|(?<![A-Z])B\.?A\.?(?![A-Z])|BACHELOR|UNDERGRAD.{0,40} DEGREE|ASSOCIATE'?S?.{20}DEGREE",i, re.IGNORECASE) for i in desc_col.values]
mba = [re.findall("([\s|-|/]MBA[\s|-|/]|[\s|-|/]MBUS[\s|-|/]|[\s|-|/]MBS[\s|-|/]|MASTERS? OF BUSINESS)",i,re.IGNORECASE) for i in desc_col.values]
masters = [re.findall("(MASTER'?S?.{0,40}DEGREE|GRADUATE.{0,40}DEGREE|(?<![A-Z])M\.?S\.?(?![A-Z]|\sDYNAMICS|,\sDSC)(?!-?~?\s?OFFICE|\sEXCEL|\sWORD|\sACCESS|-?\s?SQL)|ADVANCED?.{0,40}DEGREE)",i,re.IGNORECASE) for i in desc_col.values]
phd = [re.findall("(PH\.?D|ADVANCED?.{0,40}DEGREE|DOCTORA[TE|L]|POST-?\s?GRADUATE)",i,re.IGNORECASE) for i in desc_col.values]

distinct_df["bachelors"] = [1 if x else 0 for x in bachelors]
distinct_df["mba"] = [1 if x else 0 for x in mba]
distinct_df["masters"] = [1 if x else 0 for x in masters]
distinct_df["phd"] = [1 if x else 0 for x in phd]


## GATHERING INFORMATION BASED ON SKILLS
python = [re.findall("PYTHON",i,re.IGNORECASE) for i in desc_col.values]
R = [re.findall("[\s,\.\-(\[\\\]R[\s,\.\-)\]\\\]",i,re.IGNORECASE) for i in desc_col.values]
SQL = [re.findall("SQL",i,re.IGNORECASE) for i in desc_col.values]
java = [re.findall("JAVA(?!SCRIPT)",i,re.IGNORECASE) for i in desc_col.values]
C = [re.findall("[\s,\.\-(\\\]C([\s,\.\-)\]\\\]|\+\+|SHARP)",i,re.IGNORECASE) for i in desc_col.values]
hadoop = [re.findall("HADOOP",i,re.IGNORECASE) for i in desc_col.values]
spark = [re.findall("SPARK",i,re.IGNORECASE) for i in desc_col.values]
excel = [re.findall("Excel[\s,\.\-)\]\\\)]", i) for i in desc_col.values]
sas = [re.findall("SAS", i) for i in desc_col.values]
stata = [re.findall("STATA", i, re.IGNORECASE) for i in desc_col.values]
matlab = [re.findall("MATLAB", i, re.IGNORECASE) for i in desc_col.values]
scala = [re.findall("SCALA(?![A-Z])", i, re.IGNORECASE) for i in desc_col.values]
vba = [re.findall("VBA", i, re.IGNORECASE) for i in desc_col.values]
tableau = [re.findall("TABLEAU", i, re.IGNORECASE) for i in desc_col.values]
h2o = [re.findall("H2[O|0]", i, re.IGNORECASE) for i in desc_col.values]
ruby = [re.findall("RUBY", i, re.IGNORECASE) for i in desc_col.values]
html = [re.findall("HTML", i, re.IGNORECASE) for i in desc_col.values]
css = [re.findall("CSS", i, re.IGNORECASE) for i in desc_col.values]
javascript = [re.findall("JAVA-?\s?SCRIPT", i, re.IGNORECASE) for i in desc_col.values]
hive = [re.findall("(.{20})(?<!ARC)(HIVE)(.{20})",i,re.IGNORECASE) for i in desc_col.values]
webscrape = [re.findall("SCRAPY|SELENIUM|SCRAPE|SCRAPING|WEB SCRAP",i,re.IGNORECASE) for i in desc_col.values]

distinct_df["Python"] = [1 if x else 0 for x in python]
distinct_df["R"] = [1 if x else 0 for x in R]
distinct_df["SQL"] = [1 if x else 0 for x in SQL]
distinct_df["Java"] = [1 if x else 0 for x in java]
distinct_df["C/C++/C Sharp"] = [1 if x else 0 for x in C]
distinct_df["Hadoop"] = [1 if x else 0 for x in hadoop]
distinct_df["Spark"] = [1 if x else 0 for x in spark]
distinct_df["Excel"] = [1 if x else 0 for x in excel]
distinct_df["SAS"] = [1 if x else 0 for x in sas]
distinct_df["Stata"] = [1 if x else 0 for x in stata]
distinct_df["MatLab"] = [1 if x else 0 for x in matlab]
distinct_df["Scala"] = [1 if x else 0 for x in scala]
distinct_df["VBA"] = [1 if x else 0 for x in vba]
distinct_df["Tableau"] = [1 if x else 0 for x in tableau]
distinct_df["H2O"] = [1 if x else 0 for x in h2o]
distinct_df["Ruby"] = [1 if x else 0 for x in ruby]
distinct_df["HTML"] = [1 if x else 0 for x in html]
distinct_df["CSS"] = [1 if x else 0 for x in css]
distinct_df["Javascript"] = [1 if x else 0 for x in javascript]
distinct_df["Hive"] = [1 if x else 0 for x in hive]
distinct_df["Web Scraping"] = [1 if x else 0 for x in webscrape]

print("Frequency of skills listed for Data Science jobs (1.7k unique postings):")
print("python           :",len([x for x in python if x]))
print("R                :", len([x for x in R if x]))
print("SQL              :", len([x for x in SQL if x]))
print("Java             :",len([x for x in java if x]))
print("C, C++, or Csharp:",len([x for x in C if x]))
print("Hadoop           :", len([x for x in hadoop if x]))
print("Spark            :", len([x for x in hadoop if x]))
print("Excel            :",len([x for x in excel if x]))
print("SAS              :", len([x for x in sas if x]))
print("Stata            :",len([x for x in stata if x]))
print("Matlab           :",len([x for x in matlab if x]))
print("VBA              :",len([x for x in vba if x]))
print("Scala            :",len([x for x in scala if x]))
print("tableau          :",len([x for x in tableau if x]))
print("h2o              :",len([x for x in h2o if x]))
print("ruby             :",len([x for x in ruby if x]))
print("HTML             :",len([x for x in html if x]))
print("CSS              :",len([x for x in css if x]))
print("javascript       :",len([x for x in javascript if x]))
print("hive             :",len([x for x in hive if x]))
print("scrape           :",len([x for x in webscrape if x]))

# In order to convert instances where description lists out the number of years experience in word format, we need to
# change these words into ints
numbers = dict({"one":1, "two":2, "three":3, "four":4,"five":5, "six":6, "seven":7, "eight":8, "nine":9, "ten":10,
                "eleven":11, "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15, "sixteen":16, "seventeen":17,
                "eighteen":18, "nineteen":19})

# objective: turn all instances of string numbers to ints. Will be used in yeras regex
# I
ans = []
def numToInt(column):
    for num in numbers.items():
        for desc in column:
            desc = desc.replace(num[0], str(num[1]))
            ans.append(desc)
    return (ans)

temp = numToInt(desc_col)

for i in range(0, len(desc_col) - 1):
    desc_col.values[i] = temp[i]
distinct_df["description"] = desc_col

distinct_df["state"] = distinct_df["job_location"].str[-2:]
print(len(distinct_df["state"].unique()))
print(distinct_df["state"].unique())

print(distinct_df['state'].value_counts())
#hotones state (drop states that have super little)

###GRAPHING RESULTS
education = [("Bachelors",sum(distinct_df["bachelors"])),
             ("MBA", sum(distinct_df["mba"])),
             ("Masters", sum(distinct_df["masters"])),
             ("PhD", sum(distinct_df["phd"]))]

## Count v Education
data = [Bar(x=[val[0] for val in education],
            y=[val[1] for val in education])]
layout = Layout(title = "Data Science Job Offerings Based on Education Requirments")
fig = Figure(data=data, layout=layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(1)
# plt.bar(range(len(education)), [val[1] for val in education], align="center")
# plt.xticks(range(len(education)), [val[0] for val in education])
# plt.show()
# plt.bar()

distinct_df = distinct_df.sort_values("state")
loc_cat = distinct_df["state"].unique()
# print(type(loc_cat))
loc_count = distinct_df.groupby("state")["state"].count()
# print(loc_count)
data = [Bar(x=loc_cat, y = loc_count)]
# location_df = distinct_df.groupby("job_location").count()
layout = Layout(title="Data Science Job Offerings Based on Location")
fig = Figure(data=data, layout=layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(1)

distinct_df = distinct_df.sort_values("Industry")
ind_count = distinct_df.groupby("Industry")["Industry"].count()
ind_sal = distinct_df.groupby("Industry")["salary_est"].agg("median")
data = [Scatter(x=ind_sal, y=ind_count, mode = 'markers', text = distinct_df["Industry"].unique())]
layout = Layout(title="Data Science Job Median Salary Based on Industry")
fig = Figure(data=data, layout=layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(1)

# LOOK INTO INFORMATION TECHNOLOGY JOBS SINCE SUCH AN OUTLIER
# CHECK SKILLS AND EDUCATION LEVEL

#count based on location - done better
#count based on degree - done
#count based on skills
#count based on industry
#x = salary, y = job count for company and industry
#x = salary, y = rating for company
#x = salary, y = size
#regression
#get years of experience to work?
#boxplot for educaiton and s

