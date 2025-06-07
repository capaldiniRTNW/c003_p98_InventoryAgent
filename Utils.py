import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def generate_sha256_id(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


        ret_list.append(link)
    return ret_list

def get_pinkbike_article_links_list_from_trailforks(url):
    page_source = get_page_source_Selenium(url)
    soup = BeautifulSoup(page_source, 'html.parser', parse_only=SoupStrainer('a'))

    pblinks = []
    ignore_links_list = ['news/photo-', 'news/video-']

    #print(soup)
    pbnewslink = 'https://www.pinkbike.com/news/'
    for link in soup:
        if link.has_attr('href'):
            if pbnewslink in link['href']:
                pbnlink = link['href']
                pbnlink = pbnlink[pbnlink.find(pbnewslink):]
                pbnlink = pbnlink.removesuffix('&source=trailforksweb')

                if any(ig in pbnlink for ig in ignore_links_list):
                    print('Ignoring link:', pbnlink)
                    continue

                pblinks.append(pbnlink)
                
    pblinks = list(set(pblinks))     
    
    return list(set(pblinks))

