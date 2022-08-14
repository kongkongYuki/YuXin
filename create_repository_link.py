"""
-*- coding: utf-8 -*-
@File  : create_repository_link.py
@Author: Yuki
@Date  : 16/06/2022
@Software : PyCharm
"""
import re
import wikipedia
import uuid

from selenium import webdriver
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd

DIGITS = 4  # number of hex digits of the UUID to use

mapdic = {
    'Paul Burns': 'Burns, Paul J.',
    'Mary Irvine': 'Irvine P.',
    'George Birmingham': 'Birmingham P.',
    'John A. Edwards': 'Edwards J.',
    'Patrick J. McCarthy': 'McCarthy J.',
    'Mary Rose Gearty': 'Gearty J.',
    'John MacMenamin': 'Mac Menamin J.',
    "Donal O'Donnell": "O'Donnell J.",
    "Tony O'Connor": "O'Connor, Tony J."
}


def generate_df(page, level):
    judges = []
    judges_links = []
    soup = BeautifulSoup(page.html())
    table = soup.find("table", {"class": "wikitable"})
    judge_links = table.find_all('a', attrs={'title': True}, href=True)

    for judge in judge_links:
        judge_ = judge.text
        if judge_ in list(mapdic.keys()):
            judges.append(mapdic[judge_])
        else:
            tmp = judge_.split(" ")
            judges.append(tmp[1] + " J.")
        judges_links.append('https://en.wikipedia.org/' + judge['href'])
    d = {'Court': [level] * len(judges), 'Judge': judges, 'Link': judges_links}
    return pd.DataFrame(d)


def wiki_judge_link():
    wikipedia.set_lang("en")
    high = wikipedia.page("List_of_judges_of_the_High_Court_(Ireland)")
    supreme = wikipedia.page("List_of_judges_of_the_Supreme_Court_of_Ireland")
    appeal = wikipedia.page("List_of_judges_of_the_Court_of_Appeal_(Ireland)")

    d_high = generate_df(high, 'High Court')
    d_supreme = generate_df(supreme, 'Supreme Court')
    d_appeal = generate_df(appeal, 'Court of Appeal')

    df = pd.concat([d_high, d_supreme, d_appeal])
    return df


def judge_link_metadata(case_all):
    dic = {'Neutral Citation': [], 'Judge': []}

    for index, row in case_all.iterrows():
        if not pd.isna(row['Composition']):
            tmp = row['Composition'].split(';')
            for i in tmp:
                dic['Judge'].append(i.strip())
                dic['Neutral Citation'].append(row['Neutral Citation'])
        else:
            dic['Judge'].append(row['Judge'].strip())
            dic['Neutral Citation'].append(row['Neutral Citation'])

    judge = pd.DataFrame.from_dict(dic)
    jlink = wiki_judge_link()
    judge_link = pd.merge(judge, jlink, how='left', on=['Judge', 'Judge'])
    # Generate Unique ID by Judge
    original_ids = judge_link['Judge'].unique()
    DIGITS = 4  # number of hex digits of the UUID to use
    new_ids = {cid: int(uuid.uuid4().hex[:DIGITS], base=16) for cid in original_ids}
    judge_link['Judge ID'] = judge_link['Judge'].map(new_ids)
    judge_link.drop_duplicates(inplace=True)
    return judge_link


def instrument_link_metadata(instrument_all):
    dic = {'Instrument': list(set(instrument_all['Instrument']))}
    instrument_link = pd.DataFrame(dic)

    statue_list = []
    year_list = []
    detail_list = []

    for index, row in instrument_link.iterrows():
        year = re.match(r'.*([1-3][0-9]{3})', row['Instrument'])
        detail = re.findall(r'\(.*?\)|\d*\/.*', row['Instrument'])
        y = None
        d = None
        statue = row['Instrument']
        if detail is not None:
            d = ','.join([i.strip('()') for i in detail])
            for i in detail:
                statue = statue.replace(" "+i, "").strip()
        if year is not None:
            y = year.group(1)
            statue = statue.replace(y, "").strip()
        detail_list.append(d)
        year_list.append(y)
        statue_list.append(statue)

    instrument_link['Statue'] = statue_list
    instrument_link['Year'] = year_list
    instrument_link['Detail'] = detail_list
    instrument_link['Instrument Link'] = [None] * len(set(instrument_all['Instrument']))

    chrome_options = webdriver.ChromeOptions()
    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)

    for index, row in instrument_link.iterrows():
        inst = row['Instrument']
        year = re.match(r'.*([1-3][0-9]{3})', inst)
        if '/' not in inst and year is not None:
            inst = inst.replace(year.group(1), '').strip().replace(' ', '+')
            url = "https://www.irishstatutebook.ie/eli/ResultsTitle.html?q=" + inst + "&years=" + year.group(1)
            driver.get(url)
            hrefs = driver.find_elements_by_xpath("//div[@class='result']//a")
            for href in hrefs:
                l = href.get_attribute('href')
                row['Instrument Link'] = l
                print(inst)
                break

    original_ids = instrument_link['Instrument'].unique()
    new_ids = {cid: int(uuid.uuid4().hex[:DIGITS], base=16) for cid in original_ids}
    instrument_link['Instrument ID'] = instrument_link['Instrument'].map(new_ids)

    original_ids = instrument_link['Statue'].unique()
    new_ids = {cid: int(uuid.uuid4().hex[:DIGITS], base=16) for cid in original_ids}
    instrument_link['Statue ID'] = instrument_link['Statue'].map(new_ids)

    instrument_link = pd.merge(instrument_all, instrument_link, how='left', on=['Instrument', 'Instrument'])
    return instrument_link