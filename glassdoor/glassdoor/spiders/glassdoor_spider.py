from glassdoor.items import GlassdoorItem
from scrapy import Spider, Request
# boston         -1154532 -https://www.glassdoor.com/Job/boston-data-scientist-jobs-SRCH_IL.0,6_IC1154532_KO7,21_IP2.htm
# new-york       -1132348 -https://www.glassdoor.com/Job/new-york-data-scientist-jobs-SRCH_IL.0,8_IC1132348_KO9,23.htm
# washington  dc -1138213 -https://www.glassdoor.com/Job/washington-data-scientist-jobs-SRCH_IL.0,10_IC1138213_KO11,25.htm
# san-jose       -1147436 -https://www.glassdoor.com/Job/san-jose-data-scientist-jobs-SRCH_IL.0,8_IC1147436_KO9,23.htm
# los-angeles    -1146821 -https://www.glassdoor.com/Job/los-angeles-data-scientist-jobs-SRCH_IL.0,11_IC1146821_KO12,26.htm
# chicago        -1128808 -https://www.glassdoor.com/Job/chicago-data-scientist-jobs-SRCH_IL.0,7_IC1128808_KO8,22.htm
# austin         -1139761 -https://www.glassdoor.com/Job/austin-data-scientist-jobs-SRCH_IL.0,6_IC1139761_KO7,21.htm
# huntsville     -1127653 -https://www.glassdoor.com/Job/huntsville-data-scientist-jobs-SRCH_IL.0,10_IC1127653_KO11,25.htm (ONLY 58 JOBS, DROP??)
# seattle        -1150505 -https://www.glassdoor.com/Job/seattle-data-scientist-jobs-SRCH_IL.0,7_IC1150505_KO8,22.htm
# Denver         -1148170
# san francisco  -1147401
# miami          -1154170
# tampa          -1154429 -https://www.glassdoor.com/Job/tampa-data-scientist-jobs-SRCH_IL.0,5_IC1154429_KO6,20.htm
# palo alto      -1147434
# houston        -1140171
# atlanta        -1155583

class GlassDoorSpider(Spider):
    name = "glassdoor_spider"
    allowed_urls = ["https://www.glassdoor.com/Job/"]
    cities = ["boston", "new-york", "washington", "san-jose", "los-angeles", "chicago", "austin", "huntsville",
              "seattle", "denver", "san-francisco", "miami", "tampa", "palo-alto", "houston", "atlanta"]
    city_ids = [1154532, 1132348, 1138213, 1147436, 1146821, 1128808, 1139761, 1127653, 1150505, 1148170, 1147401,
                1154170, 1154429, 1147434, 1140171, 1155583]
    print("SETTING UP URL")
    cities = list(zip(cities, city_ids))
    start_urls = [("https://www.glassdoor.com/Job/" +
                  str(city[0]) +
                  "-data-scientist-jobs-SRCH_IL.0," +
                  str(len(city[0])) +
                  "_IC" +
                  str(city[1]) +
                  "_KO" +
                  str(len(city[0]) + 1) +
                  "," +
                  str(len(city[0]) + 15) +
                  "_IP" +
                  str(i) +
                  ".htm") for city in cities for i in range(1, 31)]


    def parse(self, response):
        print("%" * 100)
        print("SCRAPING A NEW PAGE")
        print("%" * 100)
        job_ids = response.xpath("//ul[@class='jlGrid hover']/li/@data-id").extract() #an example id: 2220873086
        print(job_ids)
        print("Got the links")
        print("-"*50)
        links = ["https://www.glassdoor.com/job-listing/-JV_IC1146821_KO0,14_KE15,23.htm?jl=" + job_id for job_id in job_ids]

        for url in links:
            yield Request(url, callback=self.parse_job)
            # yield SplashRequest(url, callback=self.parse_job, endpoint = 'render.html')

    def parse_job(self, response):
        print("~"*50)
        print("STARTING PARSING ON JOB")
        job_title = response.xpath('//h2[@class="noMargTop margBotXs strong"]/text()').extract_first()
        try:
            company_name = response.xpath('//span[@class="strong ib"]/text()').extract_first()[1:]
        except:
            company_name = "*** ERROR - NO COMPANY LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]"
        try:
            job_location = response.xpath('//span[@class="subtle ib"]/text()').extract_first()[3:]
        except:
            job_location = "*** ERROR - NO LOCATION LISTED. SEE DESCRIPTION FOR POSSIBLE HINTS *** [XX]"
        try:
            rating = response.xpath('//span[@class="compactStars margRtSm"]/text()').extract_first()[1:]
        except:
            rating = "*** ERROR - NO RATING LISTED. SEE SCRAPING FRONT PAGE *** [XX]"
        description = "\n".join(response.xpath('//div[@class="jobDescriptionContent desc"]//text()').extract())
        salary_est = response.xpath('//h2[@class="salEst"]/text()').extract_first()
        try:
            salary_low = response.xpath('//div[@class="minor cell alignLt"]/text()').extract_first()[1:]
            salary_high = response.xpath('//div[@class="minor cell alignRt"]/text()').extract_first()[1:]
        except:
            salary_high = salary_low = "None"
        try:
            post_date = response.xpath('//span[@class="minor nowrap"]/text()').extract_first()[1:]
        except:
            post_date = "None"
        company_id = response.xpath('//div[@id="EmpBasicInfo"]/@data-emp-id').extract_first()
        overview_link = "https://www.glassdoor.com/Job/overview/companyOverviewBasicInfoAjax.htm?employerId=" + company_id + "&title=+Overview&linkCompetitors=true"

        print("*** JOB TITLE   ***", job_title)
        print("*** COMPANY     ***", company_name)
        print("*** LOCATION    ***", job_location)
        print("*** RATING      ***", rating)
        print("*** SALARY      ***", salary_est)
        print("*** SALARY LOW  ***", salary_low)
        print("*** SALARY HIGH ***", salary_high)
        print("*** POST DATE   ***", post_date)
        #print("*** DESCRIPTION ***", description)
        print("~" * 50)

        yield Request(overview_link, callback=self.parse_overview, meta ={"company_id":company_id,
                                                                          "job_title": job_title,
                                                                          "company_name": company_name,
                                                                          "job_location": job_location,
                                                                          "rating": rating,
                                                                          "salary_est": salary_est,
                                                                          "salary_low": salary_low,
                                                                          "salary_high": salary_high,
                                                                          "post_date": post_date,
                                                                          "description": description})


    def parse_overview(self, response):
        print("+"*50)
        print("Break the first trojan wall - OVERVIEW")
        #Kicking the can down the road
        company_id = response.meta['company_id']
        job_title = response.meta['job_title']
        company_name = response.meta['company_name']
        job_location = response.meta['job_location']
        rating = response.meta['rating']
        salary_est = response.meta['salary_est']
        salary_low = response.meta['salary_low']
        salary_high = response.meta['salary_high']
        post_date = response.meta['post_date']
        description = response.meta['description']
        print(company_name)
        labels = response.xpath('//div[@class = "info flexbox row col-hh"]/div/label/text()').extract()
        values = response.xpath('//div[@class = "info flexbox row col-hh"]/div/span/text()').extract()
        values = list(map(str.strip, values))
        company_info = list(zip(labels,values))
        #a list of tuples, will need to sort them out where first element is var name, 2nd is value
        print(company_info) #Walmart has an error with this
        print("+"*50)




        review_link = "https://www.glassdoor.com/Job/reviews/module.htm?employerId="+company_id
        yield Request(review_link, callback=self.parse_review, meta ={"job_title": job_title,
                                                                      "company_name": company_name,
                                                                      "job_location": job_location,
                                                                      "rating": rating,
                                                                      "salary_est": salary_est,
                                                                      "salary_low": salary_low,
                                                                      "salary_high": salary_high,
                                                                      "post_date": post_date,
                                                                      "description": description,
                                                                      "company_info": company_info})

    def parse_review(self,response):
        job_title = response.meta['job_title']
        company_name = response.meta['company_name']
        job_location = response.meta['job_location']
        rating = response.meta['rating']
        salary_est = response.meta['salary_est']
        salary_low = response.meta['salary_low']
        salary_high = response.meta['salary_high']
        post_date = response.meta['post_date']
        description = response.meta['description']
        company_info = response.meta['company_info']

        reviews = response.xpath('//div[@class="tbl fill"]')
        for review in reviews:
            print("="*50)
            company_pros = "\n".join(review.xpath('.//p[@class=" pros mainText truncateThis wrapToggleStr"]/text()').extract())
            company_cons = "\n".join(review.xpath('.//p[@class=" cons mainText truncateThis  wrapToggleStr"]/text()').extract())
            try:
                recommend = review.xpath('.//div[@class="flex-grid recommends"]//div/span/text()').extract()[0]
                outlook = review.xpath('.//div[@class="flex-grid recommends"]//div/span/text()').extract()[1]
            except:
                recommend = outlook = "Recommendation or Outlook not listed"
            print("MADE IT TO REVIEWS")
            print("COMPANY NAME", company_name)
            print("*** PROS ***", company_pros)
            print("*** CONS ***", company_cons)
            print("RECOMMEND***", recommend)
            print("**OUTLOOK***", outlook)
            print("="*50)

            item = GlassdoorItem()
            item["job_title"] = job_title
            item["company_name"] = company_name
            item["company_pros"] = company_pros
            item["company_cons"] = company_cons
            item["company_info"] = company_info # this contains (if listed by the company) HQ, Size, Founded,
            # Type of Company, Industry Info, Revenue, and Competitors
            item["salary_est"] = salary_est
            item["salary_high"] = salary_high
            item["salary_low"] = salary_low
            item["job_location"] = job_location
            item["description"] = description
            item["rating"] = rating
            item["recommend"] = recommend
            item["outlook"] = outlook
            item["post_date"] = post_date

            yield item

        # This leads to redirects. Onto something though
        # city_ids = [1154532,1132348,1138213,1147436,1146821,1128808,1139761,1127653,1150505,1148170,1147401,1154170,1154429,1147434,1140171,1155583 ]
        # start_urls = [("https://www.glassdoor.com/Job/data-scientist-SRCH_IL.0,0_IC" +
        #                str(city_id) +
        #                "_KO0,14_IP" +
        #                str(i) +
        #                ".htm") for city_id in city_ids for i in range(1, 31)]
        # start_urls = [("https://www.glassdoor.com/Job/new-york-data-scientist-jobs-SRCH_IL.0,8_IC" +
        #               str(city_id) +
        #               "_KO9,23_IP" +
        #               str(i) +
        #               ".htm") for city_id in city_ids for i in range(1,31)]
        # "https://www.glassdoor.com/Job/boston-data-scientist-jobs-SRCH_IL.0,6_IC" \
        # "1154532" \
        # "_KO7,21_IP" \
        # "3.htm"
        # TURN INTO LIST COPREHENSION
        # for city_id in city_ids:
        #     for i in range(1,31):
        #         start_urls = ["https://www.glassdoor.com/Job/new-york-data-scientist-jobs-SRCH_IL.0,8_IC".append(str(city_id) for city_id in city_ids)+"_KO9,23_IP"+str(i) for i in range(1,31) +".htm"]
        # start_urls = [x+".htm" for x in start_urls]




        #once you have all the data in the csv
        #pd.concat([df.drop('col', axis = 1), df['col'].apply(pd.Series)], axis = 1)

        # if (response.xpath('//div[@class="jobDescriptionContent desc"]//div/text()').extract() == []):
        #     description = "\n".join(response.xpath('//div[@class="jobDescriptionContent desc"]/text()').extract())
        # elif (response.xpath('//div[@class="jobDescriptionContent desc"]//div/text()').extract() == []):
        #     description =  "\n".join(response.xpath('//div[@class="jobDescriptionContent desc"]//div/text()').extract())
        # else:
        #Company Overview Ajax page:
        #https://www.glassdoor.com/Job/overview/companyOverviewBasicInfoAjax.htm?employerId=15413&title=+Overview&linkCompetitors=true
        #Company Review Ajax page:
        #https://www.glassdoor.com/Job/reviews/module.htm?employerId=978686


    # job_title = scrapy.Field()
    # company_name = scrapy.Field()
    # industry = scrapy.Field()
    # salary_est = scrapy.Field()
    # salary_high = scrapy.Field()
    # salary_low = scrapy.Field()
    # job_location = scrapy.Field()
    # hq_location = scrapy.Field()
    # company_size = scrapy.Field()
    # description = scrapy.Field()
    # overall_rating = scrapy.Field()
    # Recommend = scrapy.Field()
    # post_date = scrapy.Field()