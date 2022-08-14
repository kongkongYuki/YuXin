"""
-*- coding: utf-8 -*-
@File  : create_repository.py
@Author: Yuki
@Date  : 16/06/2022
@Software : PyCharm
"""
import os

import pandas as pd
import create_repository_crawl
import create_repository_dict
import create_repository_nlp
import create_repository_link
import create_repository_topic

BASE_PATH = '/Users/xinyu/Documents/Dissertation/LegalWeb'
CRAWL_PATH = BASE_PATH + '/SourceData/Crawl/'
NLP_PATH = BASE_PATH + 'SourceData/Nlp/'
OUTPUT_PATH = BASE_PATH + '/Output/'

links_title = [
    "https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22",
    "https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=1",
    "https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=2",
    "https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=3",
    "https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=4",
    "https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.title%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=5"
]

links_text = [
    '',
    '',
    '',
    '',
    '',
    '',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=1',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=2',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=3',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=4',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=5',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=6',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=7',
    'https://www.courts.ie/search/judgments/%22Justice%20type%3AJudgment%22%20AND%20%22filter%3Aalfresco_radio.text%22%20AND%20%22filter%3Aalfresco_Court.High%20court%22%20AND%20%22filter%3Aalfresco_Court.Supreme%20Court%22%20AND%20%22filter%3Aalfresco_Court.Court%20of%20Appeal%22%20AND%20%22filter%3Aalfresco_fromdate.01%20Jan%202019%22%20AND%20%22filter%3Aalfresco_todate.01%20Jul%202022%22?page=8'
]

# Create Crawl CSV
for i in range(0, 15):
    print('-----Loop' + str(i) + '-----')
    if i <= 5:
        crawl = create_repository_crawl.crawl_metadata(BASE_PATH + '/SourceData/CaseFolder/' + str(i), links_title[i])
    else:
        crawl = create_repository_crawl.crawl_metadata(BASE_PATH + '/SourceData/CaseFolder/' + str(i), links_text[i])
    crawl.to_csv(CRAWL_PATH + 'crawl' + str(i) + '.csv', index=False)
print("-----Crawl done-----")
crawl_list = []
for file in os.listdir(CRAWL_PATH):
    if file.startswith('.'):
        continue
    df = pd.read_csv(CRAWL_PATH + str(file))
    crawl_list.append(df)
crawl_all = pd.concat(crawl_list)
crawl_all.drop_duplicates()
crawl_all.to_csv(CRAWL_PATH + 'crawl_all.csv', index=False)

# Create Nlp CSV
for i in range(0, 15):
    print('-----Loop' + str(i) + '-----')
    case = create_repository_nlp.nlp_metadata(BASE_PATH + '/SourceData/CaseFolder/' + str(i),
                                              NLP_PATH + 'nlp' + str(i) + '.csv')
print('-----Nlp done-----')
nlp_list = []
for file in os.listdir(NLP_PATH):
    if file.startswith('.'):
        print(file)
        continue
    df = pd.read_csv(NLP_PATH + str(file))
    nlp_list.append(df)
nlp_all = pd.concat(nlp_list)
nlp_all.drop_duplicates(subset='Neutral Citation', inplace=True)
nlp_all.to_csv(NLP_PATH + 'nlp_all.csv', index=False)

# Merge Two Csv
case_all = pd.merge(crawl_all, nlp_all, how='inner', on=['Neutral Citation', 'Neutral Citation'])
# case_all.to_csv(OUTPUT_PATH+ 'case_all.csv', index=False)

# Generate Judge
judge_link = create_repository_link.judge_link_metadata(case_all)
judge_link.to_csv(OUTPUT_PATH + 'judge_link.csv', index=False)

# Generate Instrument
instrument_all = pd.read_csv(BASE_PATH + '/SourceData/instrument.csv')  # File After Mannual Review
instrument_link = create_repository_link.instrument_link_metadata(instrument_all)
instrument_link.to_csv(OUTPUT_PATH + 'instrument_link.csv', index=False)

# Generate Topic for Evaluation
case_all_with_topic = create_repository_topic.topic_metadata(BASE_PATH + '/SourceData/CaseFolder/', case_all)
# case_all_with_topic.to_csv(OUTPUT_PATH + 'case_all_with_topic.csv', index=False)

# Generate Citation
[case_id_dict, case_all_with_topic_id] = create_repository_dict.generate_dict(case_all_with_topic)
case_id_dict.to_csv(OUTPUT_PATH + 'case_id_dic.csv', index=False)
case_all_with_topic_id.to_csv(OUTPUT_PATH + 'case_all_with_topic_id.csv', index=False)

# Do the mapping
import os
a = os.system("java -jar Tools/r2rml.jar Ontology/config.properties")
print(a)
