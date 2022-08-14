"""
-*- coding: utf-8 -*-
@File  : process_input_caseid.py
@Author: Yuki
@Date  : 16/06/2022
@Software : PyCharm
"""
import re
import copy
import zlib

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from execute_graph_query import SPARQLquery

from create_repository_nlp import getText, get_results

BASE_PATH = '/Users/xinyu/Documents/Dissertation/LegalWeb'
OUTPUT_PATH = BASE_PATH + '/Output/'
DATASET_PATH = BASE_PATH + "/OpenHINE/dataset/test/edge.txt"


def process_id(neutral_citation):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', {
        "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
        "download.default_directory": "/Users/xinyu/Documents/Dissertation/LegalWeb/Input",
        # Change default directory for downloads
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
    })

    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)
    neutral_citation = neutral_citation.replace("_", "%20")

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

    driver.get(
        "https://www.courts.ie/search/judgments/%22%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22"
        "%20AND%20%22filter%3Aalfresco_NeutralCitation." + neutral_citation + "%22")
    time.sleep(5)
    driver.find_element_by_class_name("agree-button").click()
    time.sleep(5)
    table = driver.find_elements_by_xpath("//table[@class='table alfresco-table']/tbody//td[2]")
    for td in table:
        a = td.find_elements_by_tag_name('a')
        for item in a:
            text = item.get_attribute('href')
            if text.endswith('pdf'):
                driver.get(text)
                dic['Case Link'].append(text)
                try:
                    downloaddoc = driver.find_element_by_partial_link_text('.docx')
                    # downloaddoc.click()
                    # time.sleep(10)
                except Exception as e:
                    print("No Docx File. This case do not support.")
                    return

    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')

    title = soup.find("div", {"class": "alfresco-title"}).find("div", recursive=False).text.strip()
    title = title.replace('- v-', ' -v-')
    dic['Title'].append(title)

    try:
        plaintiff, defendant = title.split('-v-')
    except:
        print(dic['Title'].pop())

    dic['Plaintiff'].append(plaintiff)
    dic['Defendant'].append(defendant)

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


    neutral_citation = neutral_citation.replace('%20', '_')
    nlp_results = get_results(getText(BASE_PATH + "/Input/" + neutral_citation + ".docx"), neutral_citation)

    sql = SPARQLquery("http://localhost:7200/repositories/LegalWeb")

    judge_id = sql.query_judge_id_by_name(dic['Judgment By'][0])
    case_id = sql.query_citation_id_by_name(neutral_citation)

    nlp_results['INSTRUMENT ID'] = []
    for ins in nlp_results['INSTRUMENT']:
        ins_id = sql.query_statue_id_by_name(ins)
        if not ins_id:
            nlp_results['INSTRUMENT'].remove(ins)
        else:
            nlp_results['INSTRUMENT ID'].append(ins_id)

    nlp_results['CITATION ID'] = []
    for cit in nlp_results['CITATION']:
        if not re.match(r'\[\d{4}\] [A-Z]{4} \d+', cit):
            nlp_results['CITATION'].remove(cit)
        else:
            cit_id = sql.query_citation_id_by_name(cit)
            if cit_id:
                nlp_results['CITATION ID'].append(cit_id)
            else:
                nlp_results['CITATION ID'].append(zlib.crc32(bytes(cit, 'utf-8')))

    with open(DATASET_PATH, 'a') as file:
        for ins_id in nlp_results['INSTRUMENT ID']:
            file.write(str(case_id[1:]) + '\t' + str(ins_id[1:]) + '\t' + 'p-c' + '\t' + str(2) + '\n')
            file.write(str(ins_id[1:]) + '\t' + str(case_id[1:]) + '\t' + 'c-p' + '\t' + str(2) + '\n')
        for cit_id in nlp_results['CITATION ID']:
            if str(cit_id).startswith('t'):
                cit_id = str(cit_id)[1:]
            file.write(str(case_id[1:]) + '\t' + str(cit_id) + '\t' + 'p-t' + '\t' + str(3) + '\n')
            file.write(str(cit_id) + '\t' + str(case_id[1:]) + '\t' + 't-p' + '\t' + str(3) + '\n')
        file.write(str(case_id[1:]) + '\t' + str(judge_id[1:]) + '\t' + 'p-a' + '\t' + str(1) + '\n')
        file.write(str(judge_id[1:]) + '\t' + str(case_id[1:]) + '\t' + 'a-p' + '\t' + str(1) + '\n')

    return case_id, dic, nlp_results
