# tallylib/scraper.py
import requests
from requests import Session
from lxml import html
import ssl
from concurrent.futures import ThreadPoolExecutor as Executor
import pandas as pd
from datetime import datetime
import time
import random
## Local imports
from tallylib.proxy import proxylist
from tallylib.locks import lock_yelpscraper


###########################################################################################
# Yelp Scraping
###########################################################################################
# 2020-01-17 Added review_id, user_id
def yelpScrapePage(business_id, 
                   page=0, # page
                   date_range=None # date range
                   ): 
    ''' 
    This function will scrape one Yelp page.
    CAUTION: Do NOT use multi-threading to avoid getting blocked.
    '''
    status_code, results, total_pages, keep_scraping = None, [], 0, True

    base_url = "https://www.yelp.com/biz/" # add business id
    api_url = "/review_feed?sort_by=date_desc&start=" # add number
    url = base_url + business_id + api_url + str(page*20)

    with Session() as s:
        for i in range(1000): # try many times until find a working proxy
            proxy = proxylist.getProxy() # get a new proxy IP
            try:
                with s.get(url, timeout=5, proxies=proxy) as r:
                    status_code = r.status_code
                    if status_code == 200:
                        response = r.json()
                        break
                    elif status_code == 503: # Proxy IP got blocked
                        # proxylist.removeProxy()
                        print(f"{i} status code {status_code}")
                    else:
                        print(f"{i} status code {status_code}")
            except Exception as e:
                # proxylist.removeProxy()
                print(i, e)
                continue

        if status_code != 200:
            return status_code, [], 0, False

        # get total pages 
        _html = html.fromstring(response['pagination'])
        text = _html.xpath("//div[@class='page-of-pages arrange_unit arrange_unit--fill']/text()")
        try:
            total_pages = int(text[0].strip().split(' ')[-1])
        except:
            total_pages = 0
        if page+1 >= total_pages:
            keep_scraping = False
        if page+1 > total_pages or total_pages == 0:
            return status_code, results, total_pages, keep_scraping

        # get content
        _html = html.fromstring(response['review_list'])
        dates, stars, texts, review_ids, user_ids = [], [], [], [], []
        dates = _html.xpath("//div[@class='review-content']/descendant::span[@class='rating-qualifier']/text()")
        '''
        Remove this line you will get "ValueError: time data '' does not match format '%m/%d/%Y'".
        Some reviews have been linked with preview reviews left by the same user.
        Those extra dates somehow would be scraped as blank values. Hence we would need to remove them.
        e.g. https://www.yelp.com/biz/coconut-hut-gilbert?sort_by=date_desc
        '''
        dates = [d.strip() for d in dates if d.strip() != '']
        dates = [datetime.strptime(d.strip(), format("%m/%d/%Y")) for d in dates]
        stars = _html.xpath("//div[@class='review-content']/descendant::div[@class='biz-rating__stars']/div/@title")
        stars = [float(s.split(' ')[0]) for s in stars]
        texts = [e.text for e in _html.xpath("//div[@class='review-content']/p")]
        review_ids = _html.xpath("//div[@class='review review--with-sidebar']/@data-review-id")
        user_ids = [s.split(':')[1] for s in _html.xpath("//div[@class='review review--with-sidebar']/@data-signup-object")]
        results = [[date, star, text, review_id, user_id] 
                    for date, star, text, review_id, user_id 
                    in zip(dates, stars, texts, review_ids, user_ids)]

        # filter by date
        try: 
            if date_range is not None:
                idx0, idx1 = None, None
                for i in range(len(dates)):
                    if dates[i] <= date_range[1]:
                        idx0 = i
                        break
                for i in range(len(dates)):
                    if dates[len(dates)-1-i] >= date_range[0]:
                        idx1 = len(dates)-1-i
                        break

                if idx0 is None or idx1 is None or idx1 < idx0: 
                    results = []
                else:
                    results = results[idx0:idx1+1]

                if idx1 is None or idx1 < len(dates):
                    keep_scraping = False

        except Exception as e:
            print(e)
            return status_code, [], total_pages, False

    return status_code, results, total_pages, keep_scraping


def yelpScraper(business_id,
                date_range=None):
    '''
    Scrape Yelp pages
    2020-01-22 If there is not a date range set, could scrape the first page,
        get the total_pages, then for the rest pages, utilize multi-threading.
        But I don't have time to do it. And sometimes it is not a bad idea to 
        keep it simple...
    '''    
    # check whether other session(s) is web scraping the same business ID
    if lock_yelpscraper.isLocked(business_id):
        print(f"Some other session(s) is web scraping {business_id}.")
        return None, []
    else:
        lock_yelpscraper.lockBusinessID(business_id)
  
    results, keep_scraping = [], True

    for i in range(1000): # assume no business has more than 1000 pages of reivews
        if keep_scraping==False:
            break
        status_code, result, total_pages, keep_scraping = \
            yelpScrapePage(business_id, 
                           page=i, 
                           date_range=date_range)
        if status_code != 200:
            lock_yelpscraper.unlockBusinessID(business_id)
            return status_code, []

        print(f"page {i}, reivews {len(result)} scraped, \
total pages {total_pages}, keep scraping {keep_scraping}")

        results = results + result

        ## scrape page by page of a business slowly to avoid being blocked
        # time.sleep(random.uniform(2, 4))

    lock_yelpscraper.unlockBusinessID(business_id)
    return status_code, results


# Do NOT use this function for its multi-threading execution could 
# easily get the AWS IPs blocked.
def yelpScraperAsync(business_id, 
                     total_pages=10):
    '''
    Takes a Yelp business id, scrape site for reviews
    '''
    base_url = "https://www.yelp.com/biz/" # add business id
    api_url = "/review_feed?sort_by=date_desc&start=" # add number

    class Scraper():
        def __init__(self):
            self.data = pd.DataFrame()

        def get_data(self, page, business_id=business_id):
            with Session() as s:
                url = base_url + business_id + api_url + str(page*20)
                with s.get(url, timeout=5) as r: 
                    if r.status_code==200:
                        response = dict(r.json()) 
                        _html = html.fromstring(response['review_list']) 
                        dates = _html.xpath("//div[@class='review-content']/descendant::span[@class='rating-qualifier']/text()")
                        # dates = [d.strip() for d in dates]
                        dates = [d.strip() for d in dates if d.strip() != '']
                        reviews = [e.text for e in _html.xpath("//div[@class='review-content']/p")]
                        ratings = _html.xpath("//div[@class='review-content']/descendant::div[@class='biz-rating__stars']/div/@title")
                        df = pd.DataFrame([dates, reviews, ratings]).T
                        self.data = pd.concat([self.data, df])

        def scrape(self): 
            # multithreaded execution
            with Executor(max_workers=40) as e:
                list(e.map(self.get_data, range(total_pages)))

    s = Scraper()
    s.scrape()
    return s.data