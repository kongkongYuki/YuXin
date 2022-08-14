"""
-*- coding: utf-8 -*-
@File  : create_repository_crawl.py
@Author: Yuki
@Date  : 13/06/2022
@Software : PyCharm
"""

import os
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import pandas as pd


def crawl_metadata(download_path, link):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Set up chrome core
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': download_path}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)

    # Gather case download urls
    urls = []

    driver.get(link)
    driver.find_element_by_class_name("agree-button").click()
    time.sleep(20)
    table = driver.find_elements_by_xpath("//table[@class='table alfresco-table']/tbody//td[2]")
    for td in table:
        a = td.find_elements_by_tag_name('a')
        for item in a:
            text = item.get_attribute('href')
            if text.endswith('pdf'):
                urls.append(text)

    # Crawl metadata
    dic = {
        'Judgment By': [],
        'Court': [],
        'Date Delivered': [],
        'Status': [],
        'Neutral Citation': [],
        'Date Uploaded': [],
        'Result': [],
        'Composition': [],
        'Title': [],
        'Plaintiff': [],
        'Defendant': [],
        'Case Link': []
    }

    for url in urls:
        driver.get(url)
        try:
            downloaddoc = driver.find_element_by_partial_link_text('.docx')
            downloaddoc.click()
            time.sleep(10)
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
        except:
            continue

        result = []

        title = soup.find("div", {"class": "alfresco-title"}).find("div", recursive=False).text.strip()
        title = title.replace('- v-', ' -v-')

        dic['Title'].append(title)

        try:
            if len(title.split('-v-')) > 2:
                print(dic['Title'].pop())
                continue
            plaintiff, defendant = title.split('-v-')
        except:
            print(dic['Title'].pop())
            continue

        dic['Plaintiff'].append(plaintiff.strip())
        dic['Defendant'].append(defendant.strip())

        details = soup.find("div", {"class": "alfresco-properties"}).findAll("div", recursive=False)
        for detail in details:
            key = detail.find("span", recursive=False).text
            content = detail.text.replace(key, "", 1).strip()

            if key not in list(dic.keys()):
                continue
            if key == 'Neutral Citation':
                content = content.replace('] ', '_')
                content = content.replace('[', '')
                content = content.replace(' ', '_')
            dic[key].append(content)

        if len(dic['Result']) < len(dic['Title']):
            dic['Result'].append(None)

        composition = soup.find("div", {"class": "alfresco-comp"}).find("div", recursive=False)
        if composition:
            com_key = composition.find("span", recursive=False).text
            com_content = composition.text.replace(com_key, "", 1).strip()
            dic['Composition'].append(com_content)
        else:
            dic['Composition'].append(None)

        dic['Case Link'].append(url)

        print(len(dic['Neutral Citation']), ":", dic['Neutral Citation'][-1])

    print(dic)
    crawl = pd.DataFrame(dic)
    crawl = crawl.rename(columns={"Judgment By": "Judge"}, errors="raise")
    return crawl
