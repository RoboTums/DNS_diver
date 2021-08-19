#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urlparse
 
def getURLs(url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    urls = {}
    for link in soup.find_all('img'):
        hostname = urlparse(link.get('src')).netloc
        urls[hostname] = 1
    print (urls)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch web page and extract img urls')
    parser.add_argument('--url', type=str, default="https://www.amazon.com", help="enter a url to extract the image tags from")
    args = parser.parse_args()    
    getURLs(args.url)