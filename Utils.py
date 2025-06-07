import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import re
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("Utils.py is loaded")

# Generate SHA-256 hash IDs for each document text
def generate_sha256_id(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_page_source_Selenium(url):
    options = Options()
    options.headless = True 
    driver = webdriver.Chrome(options=options)
    driver.get(url)  # Replace this with the URL of your RSS feed

    page_source = driver.page_source
    driver.quit()

    return page_source

def get_page_source_Requests(url):
    # Fetch the raw XML content
    response = requests.get(url)
    return response


def get_soup_from_url_html(url):    
    page_source = get_page_source_Selenium(url)    
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

def get_soup_from_html(html):    
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_soup_from_url_xml(url):
    response = get_page_source_Requests(url)
    soup = BeautifulSoup(response.content, 'xml')
    return soup

def get_edn_article_dict(html_soup):
    try:
        # Find title
        title_elem = html_soup.find('h1', class_='entry-title') or \
                    html_soup.find('h1', class_='post-title') or \
                    html_soup.find('h1') or \
                    html_soup.find('title')
        title = title_elem.text.strip() if title_elem else "No title found"
        
        # Find author
        author_elem = html_soup.find('span', class_='author') or \
                     html_soup.find('div', class_='author') or \
                     html_soup.find('a', attrs={'rel': 'author'}) or \
                     html_soup.select_one('.byline .author') or \
                     html_soup.select_one('[class*="author"]')
        author = author_elem.text.strip() if author_elem else "Unknown Author"
        
        # Find date
        date_elem = html_soup.find('time') or \
                   html_soup.find('span', class_='date') or \
                   html_soup.find('div', class_='date') or \
                   html_soup.select_one('[class*="date"]')
        
        if date_elem:
            date_text = date_elem.get('datetime') or date_elem.text.strip()
            try:
                if ',' in date_text:
                    date = datetime.strptime(date_text.strip(), '%B %d, %Y')
                else:
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            date = datetime.strptime(date_text[:10], fmt)
                            break
                        except:
                            continue
                    else:
                        date = datetime.now()
                date = date.strftime('%m-%d-%Y')
            except:
                date = datetime.now().strftime('%m-%d-%Y')
        else:
            date = datetime.now().strftime('%m-%d-%Y')

        # Find the main article content
        article_content = html_soup.find('div', class_='entry-content') or \
                         html_soup.find('div', class_='post-content') or \
                         html_soup.find('article') or \
                         html_soup.find('div', class_='content')
        
        if article_content:
            # Remove ads
            for unwanted in article_content.find_all(['script', 'style', 'nav', 'footer', 'header']):
                unwanted.decompose()
            for unwanted in article_content.find_all('div', class_=lambda x: x and any(
                term in x.lower() for term in ['social', 'share', 'ad', 'advertisement', 'sidebar'])):
                unwanted.decompose()
            article_text = article_content.get_text(separator=' ', strip=True)
        else:
            article_text = "Content not found"

        return {
            'title': title, 
            'author': author, 
            'date': date, 
            'text': article_text, 
            'sha256': generate_sha256_id(title + ': ' + article_text)
        }
    except Exception as e:
        print(f"Error extracting article data: {e}")
        return {
            'title': "Error extracting title", 
            'author': "Unknown", 
            'date': datetime.now().strftime('%m-%d-%Y'), 
            'text': "Error extracting content", 
            'sha256': generate_sha256_id("error")
        }

def get_edn_article_links_list_from_search(url):
    try:
        page_source = get_page_source_Selenium(url)
        soup = BeautifulSoup(page_source, 'html.parser')
        
        ret_list = []
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href', '')
            if 'edn.com' in href and any(pattern in href for pattern in ['/20', 'article', 'news']):
                if any(skip in href.lower() for skip in ['#', 'javascript:', 'mailto:', 'tel:']):
                    continue
                if href.startswith('/'):
                    href = 'https://www.edn.com' + href
                elif not href.startswith('http'):
                    href = 'https://www.edn.com/' + href
                ret_list.append(href)
        return list(set(ret_list))
    except Exception as e:
        print(f"Error extracting links from search: {e}")
        return []

def filter_articles_by_date(article_links, cutoff_date="2025-04-01"):
    filtered_links = []
    cutoff = datetime.strptime(cutoff_date, "%Y-%m-%d")
    
    for link in article_links:
        try:
            soup = get_soup_from_url_html(link)
            article_dict = get_edn_article_dict(soup)
            # Parse the article date
            article_date = datetime.strptime(article_dict['date'], '%m-%d-%Y')
            if article_date >= cutoff:
                filtered_links.append(link)
                print(f"Including article from {article_dict['date']}: {article_dict['title']}")
            else:
                print(f"Skipping article from {article_dict['date']}: {article_dict['title']}")
        except Exception as e:
            print(f"Error checking date for {link}: {e}")
            filtered_links.append(link)
    return filtered_links



