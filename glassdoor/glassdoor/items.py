# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GlassdoorItem(scrapy.Item):
    # define the fields for your item here like:
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    industry = scrapy.Field()
    salary_est = scrapy.Field()
    salary_high = scrapy.Field()
    salary_low = scrapy.Field()
    job_location = scrapy.Field()
    hq_location = scrapy.Field()
    company_size = scrapy.Field()
    description = scrapy.Field()
    overall_rating = scrapy.Field()
    friend_percent = scrapy.Field()
    ceo_approval = scrapy.Field()
    ceo_name = scrapy.Field()
    competitors = scrapy.Field()
    date_posted = scrapy.Field()



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

    # DONE TASKS
    ##-Name of the position (likely data scientist) -DONE
    ##-Name of the company - DONE
    ##-estimate salary range -DONE
    ###-low of salary estimate -DONE
    ###-high of salary estimate -DONE
    ##-Location of the job posting - DONE
    ##-when was the job posted -DONE


#job_title = comp_loc = salary_range = post_date = None

# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re

# Windows users need to specify the path to chrome driver you just downloaded.
# You need to unzip the zipfile first and move the .exe file to any folder you want.

        #listings = driver.find_elements_by_xpath('//ul[@class="jlGrid hover"]//li')


        #for listing in listings:
            # this is a way to make sure that if anything is null unexpectedly, it will error out (if i don't already
            #  have a try except for it.)
            #job_title = listing.find_element_by_xpath('.//*[@class="flexbox"]/div/a').text
            #comp_loc = listing.find_element_by_xpath('.//div[@class="flexbox empLoc"]/div').text
            # comp_loc = comp_loc.split(" – ")
            # company_name = comp_loc[0]
            # job_loc = comp_loc[1]
            #listing_button =  wait_button.until(EC.element_to_be_clickable((By.XPATH,
            #                                                                './/*[@class="flexbox"]/div/a'))
            #salary_range = listing.find_element_by_xpath('.//span[@class="green small"]').text
                #salary_range = salary_range[:-16]
                #salary_range = salary_range.split("-")
                #salary_low = salary_range[0]
                #salary_high = salary_range[1]
            #post_date = listing.find_element_by_xpath('.//span[@class="hideHH nowrap"]/span').text
            #description = driver.find_element_by_xpath('//div[@class="jobDescriptionContent desc"]//div').text

            #####CLEANING SCRAPPED DATA#####
            # This is not a normal " - ". It is a special character from the website.  Will have to look for instances
            # where a company name might be space weird-hyphen space


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

#build regression model to see coefficients on salary range
#text mining as simple as word cloud and generating frequency of word clouds
#big name companies, small array of them and did a word cloud of top companies
#capture how many times it says "years" and exerience
#using old school methods to

##What do I want with my life
#Basic goal: gather a bunch of information to find out basic information about a company and what candidates they are looking for
#what is 'basic info'?


#build regression model to see coefficients on salary range
#text mining as simple as word cloud and generating frequency of word clouds
#big name companies, small array of them and did a word cloud of top companies
#capture how many times it says "years" and exerience
#using old school methods to