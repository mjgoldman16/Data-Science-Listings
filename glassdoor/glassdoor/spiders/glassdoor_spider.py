from scrapy import Spider, Request
from glassdoor.items import GlassdoorItem
from scrapy_splash import SplashRequest

class GlassDoorSpider(Spider):
    name = "glassdoor_spider"
    allowed_urls = ["https://www.glassdoor.com/Job/"]
    start_urls = ["https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=true&clickSource=searchBtn&typedKeyword=Data+Sc&sc.keyword=Data+Scientist&locT=&locId=&jobType="]

    def parse(self, response):
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
        company_id = response.xpath('//div[@id="EmpBasicInfo"]/@data-emp-id').extract_first()
        overview_link = "https://www.glassdoor.com/Job/overview/companyOverviewBasicInfoAjax.htm?employerId=" + company_id + "&title=+Overview&linkCompetitors=true"

        print("*** JOB TITLE   ***", job_title)
        print("*** COMPANY     ***", company_name)
        print("*** LOCATION    ***", job_location)
        print("*** RATING      ***", rating)
        print("*** SALARY      ***", salary_est)
        print("*** SALARY LOW  ***", salary_low)
        print("*** SALARY HIGH ***", salary_high)
        #print("*** DESCRIPTION ***", description)
        print("~" * 50)

        yield Request(overview_link, callback=self.parse_overview, meta ={"company_id": company_id})


    def parse_overview(self, response):
        print("Break the first trojan wall - OVERVIEW")
        company_id = response.meta['company_id']
        labels = response.xpath('//div[@class = "info flexbox row col-hh"]/div/label/text()').extract()
        values = response.xpath('//div[@class = "info flexbox row col-hh"]/div/span/text()').extract()
        values = list(map(str.strip, values))
        company_info = list(zip(labels,values))
        print(company_info)
        print("+"*50)


        review_link = "https://www.glassdoor.com/Job/reviews/module.htm?employerId="+company_id
        yield Request(review_link, callback=self.parse_review)

    def parse_review(self,response):
        print("Golen apple is in sight - REVIEWS")
        print("="*50)



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
            # friend_percent = scrapy.Field()
            # ceo_approval = scrapy.Field()
            # ceo_name = scrapy.Field()
            # competitors = scrapy.Field()
        # date_posted = scrapy.Field()