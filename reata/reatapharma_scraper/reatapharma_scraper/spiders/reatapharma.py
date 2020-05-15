# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor 
from scrapy.spiders import Rule, CrawlSpider
from reatapharma_scraper.items import ReatapharmaScraperItem

class ReatapharmaSpider(CrawlSpider):
    name = 'reatapharma' #name itself
    allowed_domains = ['reatapharma.com'] #main domain stem
    start_urls = ['http://reatapharma.com/'] #root url 

    rules = [Rule(LinkExtractor(canonicalize=True,unique=True),follow=True,callback="parse_items")]

    def start_requests(self):
    	for url in self.start_urls:
    		yield scrapy.Request(url, callback=self.parse,dont_filter=True)

    def parse_items(self, response):
    	#LIST of sublinks in MAIN root link
    	items = []
    	links = LinkExtractor(canonicalize=True,unique=True).extract_links(response)
    	for link in links:
			item = ReatapharmaScraperItem()
			item['url_from'] = response.url
			item['url_to'] = link.url
			items.append(item)
			
    	# return all the found items
    	return items