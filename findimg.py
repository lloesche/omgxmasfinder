#!/usr/bin/env python3
import logging
import requests
import sys
import shutil
import yaml
from html.parser import HTMLParser
from multiprocessing.pool import ThreadPool

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('__main__').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

categories = ['ubiquiti-networks', 'mikrotik', 'ruckus-wireless', 'siklu', 'mimosa', 'cambium-networks', 'ignitenet',
              'rf-elements', 'cisco-systems', 'kerio-technologies', 'zubehoer', 'bware', 'aktionsartikel']

url_cache_file = 'cache.yaml'


def main(argv):
    try:
        f = open(url_cache_file, 'r')
        url_cache = yaml.load(f.read())
        f.close()
    except Exception:  # if cache file doesn't exist or is malformed we don't care
        url_cache = []

    for category in categories:
        category_url = 'https://shop.omg.de/{}/?ItemSorting=2&setCurrentCategoryView=1&aoff={}'.format(category, '{}')

        product_urls = fetch_product_urls(category_url)
        p = ThreadPool(30)
        xmas_img_urls = list(filter(None, p.map(get_xmas_calender_img, product_urls)))

        if len(xmas_img_urls) > 0:
            url_cache = url_cache + list(set(xmas_img_urls) - set(url_cache))
            try:
                with open(url_cache_file, 'w') as f:
                    yaml.dump(url_cache, f, default_flow_style=False)
            except Exception:  # whatever
                pass

            for xmas_img_url in xmas_img_urls:
                log.info('Found Gewinnspiel image {}'.format(xmas_img_url))
                xmas_img_file = xmas_img_url.split('/')[-1]
                response = requests.get(xmas_img_url, stream=True)
                with open(xmas_img_file, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                log.debug('Wrote image to {}'.format(xmas_img_file))

            break  # no need to look into other categories at this point


def get_xmas_calender_img(product_url):
    omg = OMGShopArticleParser()
    log.debug('Fetching product {}'.format(product_url))
    r = requests.get(product_url)
    omg.feed(r.text)
    if omg.xmasimg is not None:
        return omg.xmasimg
    return None


def fetch_product_urls(category_url):
    omg = OMGShopCategoryParser()
    complete = False
    aoff = 0
    inc = 15
    last_len_product_urls = 0
    log.info('Gathering products')
    while not complete:
        r = requests.get(category_url.format(aoff))
        aoff += inc
        omg.feed(r.text)
        if len(omg.product_urls) == last_len_product_urls:
            complete = True
        last_len_product_urls = len(omg.product_urls)
    log.info('Found {} product URLs'.format(len(omg.product_urls)))
    return omg.product_urls


class OMGShopCategoryParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.product_urls = []
        self.__bullshit = ' online kaufen bei OMG.de'
        super().__init__(*args, **kwargs)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = dict(attrs)
            if 'class' in attrs and 'href' in attrs and attrs['class'] == 'product-link':
                if attrs['href'] not in self.product_urls:
                    self.product_urls.append(attrs['href'])
                    if 'title' in attrs:
                        if attrs['title'].endswith(self.__bullshit):
                            attrs['title'] = attrs['title'][:-len(self.__bullshit)]
                        log.debug('Adding article {}'.format(attrs['title']))
                    else:
                        log.debug('Adding article URL {} with no title'.format(attrs['href']))


class OMGShopArticleParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.xmasimg = None
        super().__init__(*args, **kwargs)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and 'weihnachtsgewinnspiel' in attrs['src']:
            self.xmasimg = attrs['src']


if __name__ == "__main__":
    main(sys.argv[1:])
