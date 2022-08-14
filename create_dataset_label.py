"""
-*- coding: utf-8 -*-
@File  : create_dataset_label.py
@Author: Yuki
@Date  : 16/06/2022
@Software : PyCharm
"""

import pandas as pd

BASE_PATH = '/Users/xinyu/Documents/Dissertation/LegalWeb'


def generate_txt(df, case_id, relation, reverse, obj):
    merge = df.merge(case_id, how='left', left_on='Neutral Citation', right_on='Case_ID')
    if obj == 'Citation ID':
        weight = 3
    elif obj == 'Instrument ID':
        weight = 2
    else:
        weight = 1
    merge["Weight"] = [weight] * len(df["Neutral Citation"])
    merge["Relation"] = [relation] * len(df["Neutral Citation"])
    merge["Relation_"] = [reverse] * len(df["Neutral Citation"])
    df1 = merge.rename(columns={"Graph_ID": "Column1", obj: "Column2", "Relation": "Column3", "Weight": "Column4"})
    df2 = merge.rename(columns={"Graph_ID": "Column2", obj: "Column1", "Relation_": "Column3", "Weight": "Column4"})
    return df1[["Column1", "Column2", "Column3", "Column4"]], df2[["Column1", "Column2", "Column3", "Column4"]]


def generate_label(case):
    case['Neutral Citation ID'] = case['Neutral Citation ID'].astype('string')
    case['Topic'] = case['Topic'].astype('string')
    case['Neutral Citation ID'] = case['Neutral Citation ID'].apply(lambda x: "p" + str(x))
    return case



case_all = pd.read_csv("Output/case_all_with_topic_id.csv")
case_all.astype(str)
case_id = pd.read_csv("Output/case_id_dic.csv")
judge = pd.read_csv("Output/judge_link.csv")
citation = pd.read_csv("Output/citation.csv")
instrument = pd.read_csv("Output/instrument_link.csv")
p_a, p_a_r = generate_txt(judge, case_id, 'p-a', 'a-p', 'Judge ID')
p_t, p_t_r = generate_txt(citation, case_id, 'p-t', 't-p', 'Citation ID')
p_c, p_c_r = generate_txt(instrument, case_id, 'p-c', 'c-p', 'Instrument ID')
dateset = pd.concat([p_a, p_a_r, p_t, p_t_r, p_c, p_c_r])
dateset.to_csv(BASE_PATH + '/OpenHINE/dataset/test/' + 'edge.txt', header=None, index=None, sep='\t')
# label = generate_label(case_all[['Neutral Citation ID', 'Topic']])
# label.to_csv(BASE_PATH + '/OpenHINE/dataset/test/' + 'label.txt', header=None, index=None, sep='\t')

