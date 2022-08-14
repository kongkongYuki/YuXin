"""
-*- coding: utf-8 -*-
@File  : create_repository_dict.py
@Author: Yuki
@Date  : 22/07/2022
@Software : PyCharm
"""

import re
import pandas as pd
import uuid

DIGITS = 4


def generate_citation(case_all):
    dic = {'Neutral Citation': [], 'Citation': []}

    for index, row in case_all.iterrows():
        tmp = row['CITATION'].strip('[]').split(',')
        for item in tmp:
            cit = item.strip()[1:-1].replace('[', '').replace(']', '').replace(' ', '_')
            matchObj = re.match(r'\d{4}_[a-zA-z]{4}_\d+', cit)
            if matchObj:
                dic['Neutral Citation'].append(row['Neutral Citation'])
                dic['Citation'].append(matchObj.group())
    citation = pd.DataFrame(dic)
    citation.drop_duplicates(inplace=True)
    return citation


def generate_dict(case_all_with_topic):
    citation = generate_citation(case_all_with_topic)
    case_id = set(list(case_all_with_topic['Neutral Citation']) + list(citation['Citation']))
    case_id_dic = {
        'Case_ID': list(case_id),
        'Graph_ID': [0] * len(case_id)
    }

    case_id_df = pd.DataFrame(case_id_dic)
    original_ids = case_id_df['Case_ID'].unique()
    new_ids = {cid: int(uuid.uuid4().hex[:DIGITS], base=16) for cid in original_ids}
    case_id_df['Graph_ID'] = case_id_df['Case_ID'].map(new_ids)
    case_id_df.set_index('Case_ID', inplace=True)

    citation['Citation ID'] = [None] * len(citation['Neutral Citation'])

    for index, row in citation.iterrows():
        cit = row['Citation']
        row['Citation ID'] = case_id_df.loc[cit, 'Graph_ID']
    for index, row in case_all_with_topic.iterrows():
        cit = row['Neutral Citation']
        case_all_with_topic.loc[index, 'Neutral Citation ID'] = case_id_df.loc[cit, 'Graph_ID']

    case_all_with_topic.drop_duplicates(inplace=True)
    return case_id_df, case_all_with_topic
