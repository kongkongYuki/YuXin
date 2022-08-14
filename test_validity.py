"""
-*- coding: utf-8 -*-
@File  : test_validity.py
@Author: Yuki
@Date  : 09/08/2022
@Software : PyCharm
"""

import pandas as pd

from recommend import recommend

BASE_PATH = '/Users/xinyu/Documents/Dissertation/LegalWeb'
EMBEDDING_PATH = BASE_PATH + "/OpenHINE/output/embedding/MetaGraph2vec/test_node.txt"

citation = pd.read_csv("Output/citation.csv")
case_id = pd.read_csv("Output/case_id_dic.csv")
case = pd.read_csv("Output/case_all_with_topic_id.csv")

tmp = citation.merge(case_id, left_on='Neutral Citation', right_on='Case_ID')
case_id.set_index('Case_ID', inplace=True)

common = [x for x in list(citation['Neutral Citation']) if x in list(citation['Citation'])]  # Common Elements
len(set(common))  # 189

count = 0
invalid = []
for com_case in list(set(common)):
    com_id = case_id.loc[com_case]['Graph_ID']
    embedding = pd.read_table(EMBEDDING_PATH, names=list(range(0, 65, 1)), sep=' ')
    recommendation, evaluation = recommend(embedding, "p" + str(com_id))
    case = [int(item.replace('p', '')) for item in recommendation if item.startswith('p')]
    cit = list(tmp.loc[tmp['Citation ID'] == com_id]['Graph_ID'])
    common = set(case) & set(cit)
    if len(list(common)) > 0:
        count = count + 1
    else:
        invalid.append(com_case)
    print(count)
print(count)
print(invalid)
