from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider
import pandas as pd
import re
import json
from scrapy import Item, Field
from scrapy.utils.project import get_project_settings
import sys
import argparse

print ("This is the name of the script: ", sys.argv[0])
print ("Number of arguments: ", len(sys.argv))
print ("The arguments are: ", str(sys.argv))
print ('version is', sys.version)


parser = argparse.ArgumentParser()
parser.add_argument("x", type=str, help="input file")

args = parser.parse_args()
input_path = args.x


class ItunesItem(Item):
    name = Field()
    app_identifier = Field()
    minimum_ios_version = Field()
    languages = Field()
    price = Field()
    pass


def between(value, a, b):
    pos_a = value.find(a)
    if pos_a == -1: return ""
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a:pos_b]


def writetojson(path, name, data):
    path_local = './' + path + '/' + name + '.json'
    with open(path_local, 'w') as fp:
        json.dump(data, fp)


class AppleSpider(BaseSpider):

    name = "apps"
    allowed_domains = ['itunes.apple.com/us/']
    df = pd.read_csv(input_path)
    app_list = list(df['App Store URL'])
    start_urls = [app for app in app_list]

    def parse(self, response):

            items = []
            item = ItunesItem()
            item['name'] = response.css(".product-header__title::text").extract()
            item['name'] = ''.join(item['name'])
            item['name'] = item['name'].strip()
            languages_list = response.css("div.information-list__item:nth-child(5) > dd:nth-child(2)").extract()
            languages_list = ''.join(languages_list).strip()
            item['languages'] = between(languages_list, "aria-label=", 'class="information-list__item__definition l-column medium-9')
            ios_list = response.css("div.information-list__item:nth-child(4)").extract()
            ios_list = ''.join(ios_list).strip()
            item['minimum_ios_version'] = between(ios_list, 'aria-label=', 'class="information-list__item__definition l-column ')
            item['app_identifier'] = response.request.url
            item['app_identifier'] = re.sub("[^0-9]", "", item['app_identifier'])
            items.append(item)

            yield item


class AppleSpiderFiltered(AppleSpider):

    name = "filtered_apps"

    def parse(self, response):

        items = []
        item = ItunesItem()
        item['name'] = response.css(".product-header__title::text").extract()
        item['name'] = ''.join(item['name'])
        item['name'] = item['name'].strip()
        pattern = r"Insta"

        if re.match(pattern, item['name']):

            languages_list = response.css("div.information-list__item:nth-child(5) > dd:nth-child(2)").extract()

            languages_list = ''.join(languages_list).strip()
            item['languages'] = between(languages_list, "aria-label=",
                                        'class="information-list__item__definition l-column medium-9')

            if 'Spanish' in item['languages']:
                if 'Tagalog' in item['languages']:

                    ios_list = response.css("div.information-list__item:nth-child(4)").extract()
                    ios_list = ''.join(ios_list).strip()
                    item['minimum_ios_version'] = between(ios_list, 'aria-label=', 'class="information-list__item__definition l-column ')
                    item['app_identifier'] = response.request.url
                    item['app_identifier'] = re.sub("[^0-9]", "", item['app_identifier'])
                    items.append(item)

                    yield item


def main():

    process = CrawlerProcess(get_project_settings())
    process.crawl(AppleSpider)
    process.crawl(AppleSpiderFiltered)
    process.start()


if __name__ == "__main__":
    main()

