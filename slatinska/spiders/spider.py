import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SlatinskaItem
from itemloaders.processors import TakeFirst
import requests
import json

pattern = r'(\xa0)?'

url = "https://www.slatinska-banka.hr/wp-admin/admin-ajax.php"

payload = "action=loadmore&query=%7B%22post_type%22%3A%22post%22%2C%22error%22%3A%22%22%2C%22m%22%3A%22%22%2C%22p%22%3A0%2C%22post_parent%22%3A%22%22%2C%22subpost%22%3A%22%22%2C%22subpost_id%22%3A%22%22%2C%22attachment%22%3A%22%22%2C%22attachment_id%22%3A0%2C%22name%22%3A%22%22%2C%22pagename%22%3A%22%22%2C%22page_id%22%3A0%2C%22second%22%3A%22%22%2C%22minute%22%3A%22%22%2C%22hour%22%3A%22%22%2C%22day%22%3A0%2C%22monthnum%22%3A0%2C%22year%22%3A0%2C%22w%22%3A0%2C%22category_name%22%3A%22%22%2C%22tag%22%3A%22%22%2C%22cat%22%3A%22%22%2C%22tag_id%22%3A%22%22%2C%22author%22%3A%22%22%2C%22author_name%22%3A%22%22%2C%22feed%22%3A%22%22%2C%22tb%22%3A%22%22%2C%22paged%22%3A0%2C%22meta_key%22%3A%22%22%2C%22meta_value%22%3A%22%22%2C%22preview%22%3A%22%22%2C%22s%22%3A%22%22%2C%22sentence%22%3A%22%22%2C%22title%22%3A%22%22%2C%22fields%22%3A%22%22%2C%22menu_order%22%3A%22%22%2C%22embed%22%3A%22%22%2C%22category__in%22%3A%5B%5D%2C%22category__not_in%22%3A%5B%5D%2C%22category__and%22%3A%5B%5D%2C%22post__in%22%3A%5B%5D%2C%22post__not_in%22%3A%5B%5D%2C%22post_name__in%22%3A%5B%5D%2C%22tag__in%22%3A%5B%5D%2C%22tag__not_in%22%3A%5B%5D%2C%22tag__and%22%3A%5B%5D%2C%22tag_slug__in%22%3A%5B%5D%2C%22tag_slug__and%22%3A%5B%5D%2C%22post_parent__in%22%3A%5B%5D%2C%22post_parent__not_in%22%3A%5B%5D%2C%22author__in%22%3A%5B%5D%2C%22author__not_in%22%3A%5B%5D%2C%22ignore_sticky_posts%22%3Afalse%2C%22suppress_filters%22%3Afalse%2C%22cache_results%22%3Atrue%2C%22update_post_term_cache%22%3Atrue%2C%22lazy_load_term_meta%22%3Atrue%2C%22update_post_meta_cache%22%3Atrue%2C%22posts_per_page%22%3A9%2C%22nopaging%22%3Afalse%2C%22comments_per_page%22%3A%2250%22%2C%22no_found_rows%22%3Afalse%2C%22order%22%3A%22DESC%22%7D&page={}"
headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.slatinska-banka.hr',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.slatinska-banka.hr/obavijesti/',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cookie': 'CookieConsent={stamp:%27pK38idPpdOHG0hxuVdWLDFMnS7mn0sBIKDaHtZjkdKNj9BNQafHG8Q==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:false%2Cver:1%2Cutc:1614346709980%2Cregion:%27bg%27}; _ga=GA1.2.173448694.1614346710; _gid=GA1.2.1402636644.1616061915'
}

response = requests.request("POST", url, headers=headers, data=payload)


class SlatinskaSpider(scrapy.Spider):
    name = 'slatinska'
    start_urls = ['https://www.slatinska-banka.hr/obavijesti/']
    page = 0

    def parse(self, response):
        data = requests.request("POST", url, headers=headers, data=payload.format(self.page))
        data = json.loads(data.text)
        for index in range(len(data[0])):
                slug = data[index]['slug']
                links = 'https://www.slatinska-banka.hr/'+slug
                yield response.follow(links, self.parse_post)

        if not len(data) == 0:
            self.page += 1
            yield response.follow(response.url, self.parse, dont_filter=True)

    def parse_post(self, response):
        date = response.xpath('//meta[@property="article:published_time"]/@content').get()
        date = re.findall(r'\d+\-\d+\-\d+',date)
        title = response.xpath('//h2[last()]/text()').get()
        content = response.xpath('//div[@id="content"]//text()[not (ancestor::h2 or ancestor::div[@class="breadcrumb"] or ancestor::div[@class="shareRow"])]').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "",' '.join(content))

        item = ItemLoader(item=SlatinskaItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()
