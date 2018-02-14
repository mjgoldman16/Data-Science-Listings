import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import re
import plotly
from plotly.graph_objs import Figure, Bar, Layout, Scatter, Box
import time
import spicy
import seaborn as sns
from sklearn import linear_model
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison

# df = pd.read_csv("./Data/testing_reviews.csv") # this is 13k. but same number in terms of salary. not much diff
#
# print(df.isnull().sum())
# print(len(pd.unique(df["company_name"]))) #2.6k unique companies for the larger df
# print(df.columns)
#
# df = df[(df["company_name"]!="*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]") & (df["company_info"].isnull()!=True)]
# print((df["company_name"]=="*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]").sum())
# print(df["company_info"].isnull().sum())
# print(len(df))
# df.dropna()
# print(len(df))
# df = df.reset_index()

###CLEANING DATA
df = pd.read_csv("./Data/reviews.csv") # this is 8k and has all rows filled in so do not need to drop "ERROR"s
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

python_len = len([x for x in python if x])
R_len = len([x for x in R if x])
SQL_len =  len([x for x in SQL if x])
java_len = len([x for x in java if x])
C_len = len([x for x in C if x])
hadoop_len =  len([x for x in hadoop if x])
spark_len = len([x for x in hadoop if x])
excel_len = len([x for x in excel if x])
sas_len = len([x for x in sas if x])
stata_len = len([x for x in stata if x])
matlab_len = len([x for x in matlab if x])
vba_len = len([x for x in vba if x])
scala_len = len([x for x in scala if x])
tableau_len = len([x for x in tableau if x])
h2o_len = len([x for x in h2o if x])
ruby_len = len([x for x in ruby if x])
html_len = len([x for x in html if x])
css_len = len([x for x in css if x])
javascript_len = len([x for x in javascript if x])
hive_len = len([x for x in hive if x])
scrape_len = len([x for x in webscrape if x])

print("Frequency of skills listed for Data Science jobs (1.7k unique postings):")
print("python           :", python_len)
print("R                :", R_len)
print("SQL              :", SQL_len)
print("Java             :", java_len)
print("C, C++, or Csharp:", C_len)
print("Hadoop           :", hadoop_len)
print("Spark            :", spark_len)
print("Excel            :", excel_len)
print("SAS              :", sas_len)
print("Stata            :", stata_len)
print("Matlab           :", matlab_len)
print("VBA              :", vba_len)
print("Scala            :", scala_len)
print("tableau          :", tableau_len)
print("h2o              :", h2o_len)
print("ruby             :", ruby_len)
print("HTML             :", html_len)
print("CSS              :", css_len)
print("javascript       :", javascript_len)
print("hive             :", hive_len)
print("scrape           :", scrape_len)

# print("Java             :", java_len)
# print("C, C++, or Csharp:", C_len)
# print("Hadoop           :", hadoop_len)
# print("Spark            :", spark_len)
# print("Excel            :", excel_len)
# print("SAS              :", sas_len)
# print("Stata            :", stata_len)
# print("Matlab           :", matlab_len)
# print("VBA              :", vba_len)
# print("Scala            :", scala_len)
# print("tableau          :", tableau_len)
# print("h2o              :", h2o_len)
# print("ruby             :", ruby_len)
# print("HTML             :", html_len)
# print("CSS              :", css_len)
# print("javascript       :", javascript_len)
# print("hive             :", hive_len)
# print("scrape           :", scrape_len)
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
distinct_df = distinct_df[distinct_df["state"]!="IN"]
print(len(distinct_df["state"].unique()))
print(distinct_df["state"].unique())

# print(distinct_df['state'].value_counts())
# print(distinct_df["job_location"].value_counts())

#hotones state (drop states that have super little)

################################################### GRAPHING RESULTS ###################################################
# Setting up looping variables for graphing
education = [("Bachelors",sum(distinct_df["bachelors"])),
             ("MBA", sum(distinct_df["mba"])),
             ("Masters", sum(distinct_df["masters"])),
             ("PhD", sum(distinct_df["phd"]))]

skills = [("SQL", SQL_len),
          ("Python", python_len),
          ("R", R_len),
          ("Java", java_len),
          ("Hadoop", hadoop_len),
          ("Spark", spark_len),
          ("Excel", excel_len),
          ("Tableau", tableau_len),
          ("SAS", sas_len),
          ("C, C++, or C Sharp", C_len),
          ("Scala", scala_len),
          ("MatLab", matlab_len),
          ("Hive", hive_len),
          ("Javascript", javascript_len),
          ("Ruby", ruby_len),
          ("HTML", html_len),
          ("VBA", vba_len),
          ("Stata", stata_len),
          ("H2O", h2o_len),
          ("CSS", css_len),
          ("Scrapy or Selenium", scrape_len)]

## Count v Education
data = [Bar(x=[val[0] for val in education],
            y=[val[1] for val in education])]
layout = Layout(title = "Data Science Job Offerings Based on Education Requirements",
                xaxis = dict(title = "Education Levels"),
                yaxis = dict(title = "Number of Job Postings"))
fig = Figure(data=data, layout=layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

# Count v Skills
data = [Bar(x = [val[0] for val in skills],
            y = [val[1] for val in skills])]
layout = Layout(title = "Data Science Job Offerings Based on Skill Requirements",
                xaxis = dict(title = "Skills"),
                yaxis = dict(title = "Number of Job Postings"))
fig = Figure(data = data, layout= layout)
plotly.offline.plot(fig,show_link=False)
time.sleep(.5)

## Count v State
distinct_df = distinct_df.sort_values("state")
loc_cat = distinct_df["state"].unique()
# print(type(loc_cat))
loc_count = distinct_df.groupby("state")["state"].count()
# print(loc_count)
data = [Bar(x=loc_cat, y = loc_count)]
# location_df = distinct_df.groupby("job_location").count()
layout = Layout(title="Data Science Job Offerings Based on Location",
                xaxis = dict(title = "States"),
                yaxis = dict(title = "Number of Job Postings"))
fig = Figure(data=data, layout=layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)


## Count v Salary by Industry
distinct_df = distinct_df.sort_values("Industry")
ind_count = distinct_df.groupby("Industry")["Industry"].count()
ind_sal = distinct_df.groupby("Industry")["salary_est"].agg("median")
data = [Scatter(x=ind_sal,
                y=ind_count,
                mode = 'markers',
                text = distinct_df["Industry"].unique())]
layout = Layout(title="Data Science Job Median Salary Compared to Number of Postings Based on Industry",
                xaxis = dict(title = "Median Salary"),
                yaxis = dict(title = "Number of Job Postings"))
fig = Figure(data=data, layout=layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

# LOOK INTO INFORMATION TECHNOLOGY JOBS SINCE SUCH AN OUTLIER [XX] ***
# CHECK SKILLS AND EDUCATION LEVEL
median_rent = pd.read_csv("D:/NYC-Data-Science/Projects/Webscrapping-Project/glassdoor/Data/Top 25 DS cities median rent.csv")
top25_median = distinct_df.merge(median_rent,how = "inner", left_on = "job_location", right_on = "Location", sort = True)
top25_median["Median Yearly 1 BB rent"]= top25_median["Median Yearly 1 BB rent"].astype(int)
top25_median["sal_ratio"] = top25_median["salary_est"]/top25_median["Median Yearly 1 BB rent"]

## ATTEMPT AT SORTING BASED ON MEDIAN OF DATAPOINTS RATHER THAN ALPHABETICALLY XX***
# top25_median["sorted_med"] = top25_median.groupby("job_location")["salary_est"].agg("median")
# top25_median = top25_median.sort_values("sorted_med")
# top25_median = top25_median.sort_values(top25_median.sal_ratio[top25_median.job_location].agg("median")).reset_index()

#SEABORN NOT JITTERING XX ***
# sns.stripplot(x = distinct_df["salary_est"]/1000,
#               y = distinct_df["rating"],
#               jitter = True,
#               edgecolor= "none").set_title("Data Science Salaries Compared to Company Rating")
# plt.xlabel("Job Salary (in Thousands)")
# plt.ylabel("Company Rating")
# plt.show()

#PLOTLY DOESN'T HAVE A JITTER FOR SCATTERPLOTS
data = Scatter(x = distinct_df["salary_est"],
                y = distinct_df["rating"],
                mode = "markers",
                text = distinct_df["company_name"],
               name = "Companies")

## Regression
regr = linear_model.LinearRegression()
x = distinct_df.iloc[:,[3,5]]
regr.fit(distinct_df[["salary_est"]], distinct_df["rating"])
# The coefficients
print('Coefficients: \n', regr.coef_)
# The mean squared error
print("Mean squared error: %.2f"
      % np.mean((regr.predict(distinct_df[["salary_est"]]) - distinct_df["rating"]) ** 2))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % regr.score(distinct_df[["salary_est"]], distinct_df["rating"]))
print(regr.predict((distinct_df[["salary_est"]])))

reg_line = Scatter(x = distinct_df["salary_est"],
                    y = regr.predict(distinct_df[["salary_est"]]),
                    mode = "lines",
                    line = dict(color = "black", width = 3),
                   name = "OLS Regression")

layout = Layout(title = "Data Science Salaries Compared to Company Rating",
                xaxis = dict(title = "Job Salaries"),
                yaxis = dict(title = "Company Rating"),
                showlegend = False)

x = sm.add_constant(distinct_df[["salary_est"]])
model = sm.OLS(distinct_df["rating"], x)
results = model.fit()
print(results.summary())


fig = Figure(data=[data,reg_line], layout = layout)

plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

# Median salary vs. location
data = [{"y": top25_median.salary_est[top25_median.job_location == i],
         "name": i,
         "type": "box",
         "boxmean": True} for i in top25_median.job_location.unique()]
time.sleep(.5)

layout = Layout(title = "Data Science Salaries Range Based on Location",
                xaxis = dict(title = "Cities"),
                yaxis = dict(title = "Salary Range"))
fig = Figure(data = data, layout = layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

# Median Salary/Rent vs location
data = [{"y": top25_median.sal_ratio[top25_median.job_location == i],
         "name": i,
         "type": "box",
         "boxmean": True} for i in top25_median["job_location"].unique()]

layout = Layout(title = "Ratio of Data Science Salaries Over Median Cost of a One Bed Room Apartment",
                xaxis = dict(title = "Cities"),
                yaxis = dict(title = "Ratio of Salaries over Median Cost of a One Bed Room Apartment"))
fig = Figure(data = data, layout = layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

# salary vs size
# def sort_df(df, column_idx, key):
#     '''Takes dataframe, column index and custom function for sorting,
#     returns dataframe sorted by this column using this function'''
#
#     col = df.ix[:, column_idx]
#     temp = np.array(col.values.tolist())
#     order = sorted(range(len(temp)), key=lambda j: key(temp[j]))
#     return df.ix[order]
sizes = ['1 to 50 employees', '51 to 200 employees',  '201 to 500 employees', '501 to 1000 employees',
         '1001 to 5000 employees', '5001 to 10000 employees', '10000+ employees', 'Unknown']

distinct_df["Size"] = pd.Categorical(
    distinct_df["Size"],
    categories=sizes,
    ordered = True
)
distinct_df = distinct_df.sort_values("Size")


data = [{"y": distinct_df.salary_est[distinct_df.Size == i],
         "name": i,
         "type": "box",
         "boxmean": True} for i in distinct_df["Size"].unique()]

layout = Layout(title = "Data Science Salaries Based on Company Size",
                xaxis = dict(title = "Size of the Company"),
                yaxis = dict(title = "Salary Range"))
fig = Figure(data = data, layout = layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

# Education v salary range
bachelors_sal = Box(y = distinct_df.salary_est[distinct_df.bachelors == 1],
                    name = "Bachelor's Degree",
                    boxmean = True)
mba_sal = Box(y = distinct_df.salary_est[distinct_df.mba == 1],
              name = "MBA Degree",
              boxmean=True)
masters_sal = Box(y = distinct_df.salary_est[distinct_df.masters == 1],
                  name = "Master's Degree",
                  boxmean=True)
phd_sal = Box(y = distinct_df.salary_est[distinct_df.phd == 1],
              name = "Doctorate Degree",
              boxmean=True)
data = [bachelors_sal, mba_sal, masters_sal, phd_sal]
layout = Layout(title = "Data Science Salaries Based on Education Level",
                xaxis = dict(title = "Level of Education"),
                yaxis = dict(title = "Salary Range"))
fig = Figure(data = data, layout = layout)
plotly.offline.plot(fig, show_link=False)
time.sleep(.5)

regr = linear_model.LinearRegression()
regr.fit(distinct_df[["bachelors","mba","masters","phd"]], distinct_df["salary_est"])
# The coefficients
print('Coefficients: \n', regr.coef_)
# The mean squared error
print("Mean squared error: %.2f"
      % np.mean((regr.predict(distinct_df[["bachelors","mba","masters","phd"]]) - distinct_df["salary_est"]) ** 2))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % regr.score(distinct_df[["bachelors","mba","masters","phd"]], distinct_df["salary_est"]))
print(regr.predict((distinct_df[["bachelors","mba","masters","phd"]])))

edu_df = distinct_df[["bachelors","mba","masters","phd"]].values.reshape(-1,1)
x = sm.add_constant(edu_df)
model = sm.OLS(edu_df, x)
results = model.fit()
# print(results.summary())
## XX *** ERRORS OUT

## XX *** ASK TAs FOR HELP IN LUNCH
mc = MultiComparison(distinct_df.salary_est[distinct_df.bachelors==1],
                     distinct_df.salary_est[distinct_df.mba == 1],
                     distinct_df.salary_est[distinct_df.masters == 1],
                     distinct_df.salary_est[distinct_df.phd == 1],
                     distinct_df["salary_est"])

result = mc.tukeyhsd()
print(result)
print(mc.groupsunique)
# x = sm.add_constant(distinct_df[["salary_est"]])
# model = sm.OLS(distinct_df["rating"], x)
# results = model.fit()
# print(results.summary())
############################################## XX *** TO DO: REGRESSION, SALARY AND SIZE, BOXPLOT EDUC AND SALARY. MEASURE VIF

# Objective: display the correlations between all the variables
# Input: a data frame
# output: display of correlations between every variable combination

corr = distinct_df.corr()
f, ax = plt.subplots(figsize=(10, 8))
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
sns.heatmap(corr, mask=mask, cmap=sns.diverging_palette(220, -10, as_cmap=True),
            square=True, ax=ax)
plt.show()
print(distinct_df[distinct_df.company_name=="HBO"])
## Regression
# regr = linear_model.LinearRegression()
# # x = distinct_df.iloc[:,[3,5]]
# regr.fit(distinct_df[["salary_est"]], distinct_df["rating"])
# # The coefficients
# print('Coefficients: \n', regr.coef_)
# # The mean squared error
# print("Mean squared error: %.2f"
#       % np.mean((regr.predict(distinct_df[["salary_est"]]) - distinct_df["rating"]) ** 2))
# # Explained variance score: 1 is perfect prediction
# print('Variance score: %.2f' % regr.score(distinct_df[["salary_est"]], distinct_df["rating"]))
# print(regr.predict((distinct_df[["salary_est"]])))



#
# # generate an array of rainbow colors by fixing the saturation and lightness of the HSL representation of colour
# # and marching around the hue.
#
# c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, N)]
#
# #loading the data with filters
# data = [{
#     'y': gamedf.starrating[gamedf.gamecategory == j],
#     'name': j,
#     'type':'box',
#     'marker':{'color': c[i]}
#     } for i, j in enumerate(totalgamecategory)]
#
#
# # format the layout
# layout = {'xaxis': {'showgrid':False,'zeroline':False, 'tickangle':60,'showticklabels':False},
#           'yaxis': {'zeroline':False,'gridcolor':'white'},
#           'paper_bgcolor': 'rgb(233,233,233)',
#           'plot_bgcolor': 'rgb(233,233,233)',
#           }
#
# py.offline.iplot(data)


### GOT TO SORT ON MEDIUM FOR BAR PLOT AND TOTAL COUNTS FOR SKILLS XX ***

#count based on location - done better
#count based on degree - done
#count based on skills - done
#count based on industry -doneish with the salary/jobcount
#look up living cost per state - done
#x = salary, y = job count for industry -done
#x = salary, y = rating for company - a bit ugly
#x = salary, y = size - done
#regression - check linearity and normality check homo/hetro skedastic. - Will implement later XX ***
# check correlation between education. partial f tests
# do a correlation matrix - done
# get years of experience to work? - WIll implement later XX ***
# boxplot for educaiton and salary range

#nested anova - all the stats in an anova and the salary ranges?
# regression for west vs east instead of all?

#show