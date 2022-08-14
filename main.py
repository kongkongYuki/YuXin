import argparse
import json
import os
import threading

import pandas as pd

from OpenHINE.train import model_main
from execute_graph_query import SPARQLquery
from process_input_caseid import process_id
from recommend import recommend

BASE_PATH = '/Users/xinyu/Documents/Dissertation/LegalWeb'
EMBEDDING_PATH = BASE_PATH + "/OpenHINE/output/embedding/MetaGraph2vec/test_node.txt"


def init_para():
    parser = argparse.ArgumentParser(description="LegalWeb")
    parser.add_argument('-i', '--input', default='2021_IEHC_683', type=str, help="Input content")
    case_args = parser.parse_args()
    return case_args


if __name__ == '__main__':
    args = init_para()
    # check if the new input in database. If exist: directly recommend; else process and train
    sql = SPARQLquery("http://localhost:7200/repositories/LegalWeb")

    # query_neutral = args.input
    query_neutral = '2020_IECA_184'

    # not exist: 2020_IECA_183 ;
    # exist: 2020_IECA_159 (topic 6)/2022_IEHC_141 (topic 4);
    # 2022_IEHC_393 (topic 3) / 2022_IEHC_83 (topic 2)
    # 2022_IEHC_167 (topic 5)
    # 2020_IECA_184 (topic 8)/2021_IECA_1 (topic 10);
    # 2021_IECA_322 (topic 1); 2021_IECA_248 (topic 9)
    # 2021_IEHC_773 (topic 7)
    query_case = sql.query_case_exist(query_neutral)
    if query_case:
        print('Case exist', query_case)
    else:
        print('Case not exist')

        print('--- Start processing ---')
        query_case, dic_results, nlp_results = process_id(query_neutral)
        print("case id:", query_case)
        print("dic results:", dic_results)
        print("nlp results:", nlp_results)
        print('--- End processing ---\n\n')

        print('--- Start inserting ---')
        sql_ = SPARQLquery("http://localhost:7200/repositories/LegalWeb/statements")
        r = sql_.insert_new_case_info(dic_results)
        # r = sql_.delete_new_case_info(dic_results)
        print(r)
        print('--- End inserting ---\n\n')

        print('--- Start Training ---')
        os.system("python OpenHINE/train.py -m MetaGraph2vec -d test")
        t = threading.Thread(target=model_main)
        t.start()
        t.join()
        print('--- End Training ---\n\n')

    print("--- Start recommending ---")
    with open(EMBEDDING_PATH, mode='r', encoding='utf-8') as f:
        line = f.readlines()
        try:
            if len(line[0].split(" ")) == 2:
                line = line[1:]
                f = open(EMBEDDING_PATH , mode='w', encoding='utf-8')
                f.writelines(line)
                f.close()
        except Exception as e:
            print(e)
    embedding = pd.read_table(EMBEDDING_PATH, names=list(range(0, 65, 1)), sep=' ')
    recommendation, evaluation = recommend(embedding, query_case)
    print(recommendation)
    print(evaluation)
    if recommendation:
        info = sql.query_recommendation(recommendation)
        with open(BASE_PATH + "/recommendation.json", "w") as write_file:
            json.dump(info, write_file, indent=4)
    print('--- End recommending ---\n\n')
