## Import Packages

from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request

import pandas as pd
import numpy as np


import re
import time

from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager


### Parameters
websiteName = "Auslit Legal Articles"
offsetNumber = 0
offsetCurrent = 0
pagesMaxforSession = 50

webAddress = f"http://www.austlii.edu.au/cgi-bin/sinosrch.cgi?mask_path=au%2Fcases%2Fcth%2FHCATrans;method=auto;query=%22HCATrans%22;results=100;offset={offsetNumber}"

### Start WebDriver

driver = webdriver.Chrome(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

### Webpage Helper Functions
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)
	
### Start Scrape

numberClicks = 0
while numberClicks < pagesMaxforSession:
    print("Current offset is at {}".format(offsetNumber))
    webAddress = f"http://www.austlii.edu.au/cgi-bin/sinosrch.cgi?mask_path=au%2Fcases%2Fcth%2FHCATrans;method=auto;query=%22HCATrans%22;results=100;offset={offsetNumber}"
    driver.get(webAddress)
    time.sleep(5)
    linkListAll = []
    list_links = driver.find_elements_by_tag_name('a')
    for v in list_links:
        linkListAll.append(v.get_attribute('href'))
        #print("Found links for web address {}, number of links is {}".format(websiteName, len(linkListAll)))
        articles = []
        for i in linkListAll:
            if "viewdoc" in i:
                articles.append(i)
            else:
                pass
    print("Number of links in list is {}".format(len(articles)))
    #print(articles)

    for articleLink in articles:
        time.sleep(5)
        try:
            driver.get(articleLink)
            driver.find_element_by_partial_link_text("RTF").click()
            print("Success in getting article")
        except:
            print("Cannot access article")
        driver.get(webAddress)

    time.sleep(10)
    offsetNumber += 100
    numberClicks +=1
    
	
	