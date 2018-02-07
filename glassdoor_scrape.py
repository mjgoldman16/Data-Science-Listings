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

index = 1

while index < 2:
    try:
        print("Scraping Page number " + str(index))
        index += 1

        listings = driver.find_elements_by_xpath('//ul[@class="jlGrid hover"]//li')

        for listing in listings:
            # this is a way to make sure that if anything is null unexpectedly, it will error out (if i don't already
            #  have a try except for it.)
            job_title = comp_loc = salary_range = post_date = None
            job_title = listing.find_element_by_xpath('.//*[@class="flexbox"]/div/a').text
            comp_loc = listing.find_element_by_xpath('.//div[@class="flexbox empLoc"]/div').text
            # salary_range = listing.find_element_by_xpath('.//span[@class="green small"]').text
            # text = listing.find_element_by_xpath("./div[2]/div[3]/div/span").text
            try:
                salary_range = listing.find_element_by_xpath('.//span[@class="green small"]').text
                salary_range = salary_range[:-16]
                salary_range = salary_range.split("-")
                salary_low = salary_range[0]
                salary_high = salary_range[1]
            except:
                pass
            try:
                post_date = listing.find_element_by_xpath('.//span[@class="hideHH nowrap"]/span').text
            except:
                pass

            # [@class ='green small']

            #####CLEANING SCRAPPED DATA#####
            # This is not a normal " - ". It is a special character from the website.  Will have to look for instances
            # where a company name might be space weird-hyphen space
            comp_loc = comp_loc.split(" – ")
            company_name = comp_loc[0]
            job_loc = comp_loc[1]

            ################################

            print("job:",job_title)
            print("company:",company_name)
            print("job location:",job_loc)
            if(salary_range!=None):
                print("salary range est:", salary_range)
                print("salary low est:", salary_low)
                print("salary high est:", salary_high)
            else:
                print("salary range est: N/A")
            if(post_date!=None):
                print("post date:", post_date)
            else:
                print("post date: N/A")
            print("-"*50)
        # for listing in listings:
        #     title = listing.text
        #     company_name = company_names.text
        #
        #     print(company_name)

    except Exception as e:
        print(e)
        driver.close()
        break
#print(len(listings))
#for job in listings:
#    title = job.find_element_by_xpath('.//div[@class="flexbox"]/div/a').text
#    print(title)
#

##What do I want with my life
#Basic goal: gather a bunch of information to find out basic information about a company and what candidates they are looking for
#what is 'basic info'?

###-potentially look up cost of living based on city and see the salary/ratio
##-Location of the HQ
##-Industry of the company
##-Rating of the company (overall, recommend to a friend, approve of CEO, CEO Name)
##-Competitors
##-Size of the company
##-type of company (private, public, non-profit, etc.)
##-revenue of the company
##-Job description/requirements
###-With this information, look up word frequency of important skills such as python, r, java, sql, C, C++ etc.
###-look up frequency of phd, master, asdvanced degree,
###-look up years experience

#DONE TASKS
##-Name of the position (likely data scientist) -DONE
##-Name of the company - DONE
##-estimate salary range -DONE
###-low of salary estimate -DONE
###-high of salary estimate -DONE
##-Location of the job posting - DONE
##-when was the job posted -DONE