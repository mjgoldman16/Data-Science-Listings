from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re

# Windows users need to specify the path to chrome driver you just downloaded.
# You need to unzip the zipfile first and move the .exe file to any folder you want.
driver = webdriver.Chrome("./chromedriver.exe")
driver = webdriver.Chrome()

driver.get("https://www.glassdoor.com/Job/data-scientist-jobs-SRCH_KO0,14.htm?jobType=fulltime")

csv_file = open('company.csv', 'wb')
csv_file = open('company.csv', 'w', newline="")
writer = csv.writer(csv_file)

index = 1
listings = driver.find_elements_by_xpath('//[@class = "flexbox"]/div/a/]').text  #Returns all the titles
print(listings)
print(len(listings))
#print(len(listings))
#for job in listings:
#    title = job.find_element_by_xpath('.//div[@class="flexbox"]/div/a').text
#    print(title)
#

##What do I want with my life
#Basic goal: gather a bunch of information to find out basic information about a company and what candidates they are looking for
#what is 'basic info'?
##-Name of the position (likely data scientist)
##-Name of the company
##-estimate salary range
###-low of salary estimate
###-high of salary estimate
##-Location of the job posting
###-potentially look up cost of living based on city and see the salary/ratio
##-when was the job posted
##-Location of the HQ
##-Industry of the company
##-Rating of the company (overall, recommend to a friend, approve of CEO, CEO Name)
##-Competitors
##-Size of the company
##-type of company (private, public, non-profit, etc.)
##-revenue
##-Job description/requirements
###-With this information, look up word frequency of important skills such as python, r, java, sql, C, C++ etc.
###-look up frequency of phd, master, asdvanced degree,
###-look up years experience
