"""
-*- coding: utf-8 -*-
@File  : flaskapi.py
@Author: Yuki
@Date  : 28/06/2022
@Software : PyCharm
"""

import os
from flask import Flask, request, jsonify

from execute_graph_query import SPARQLquery
from recommend import recommend
import pandas as pd


BASE_PATH = '/Users/xinyu/Documents/Dissertation/LegalWeb'
EMBEDDING_PATH = BASE_PATH + "/OpenHINE/output/embedding/MetaGraph2vec/test_node.txt"

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/<neutral_citation>', methods=['GET'])
def get_recommendation_by_id(neutral_citation):
    if os.path.exists(EMBEDDING_PATH):
        sql = SPARQLquery("http://localhost:7200/repositories/LegalWeb")
        query_case = sql.query_case_exist(neutral_citation)
        if query_case:
            embedding = pd.read_table(EMBEDDING_PATH, names=list(range(0, 65, 1)), sep=' ')
            recommendation = recommend(embedding, query_case)
            if recommendation:
                info = sql.query_recommendation(recommendation)
                return jsonify(info)
    else:
        return jsonify("Not training yet.")


app.run()

# export FLASK_APP=flaskapi.py
# flask run