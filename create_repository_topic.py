"""
-*- coding: utf-8 -*-
@File  : create_repository_topic.py
@Author: Yuki
@Date  : 20/07/2022
@Software : PyCharm
"""

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import os
from create_repository_nlp import getText

NUM_TOPICS = 10


def topic_metadata(case_folder, case_all):
    document_id = []
    document_list = []
    for i in range(0, 15):
        inpath = case_folder + str(i)
        files = os.listdir(inpath)
        for file in files:
            if not file.startswith('.') and not os.path.isdir(file):
                document_id.append(str(file).replace(".docx", ""))
                document = getText(inpath + "/" + file)
                document_list.append(document)
    print('Document List Done')

    vectorizer = CountVectorizer(min_df=5, max_df=0.9,
                                 stop_words='english', lowercase=True,
                                 token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}')
    data_vectorized = vectorizer.fit_transform(document_list)

    # Build a Latent Dirichlet Allocation Model
    lda_model = LatentDirichletAllocation(n_components=NUM_TOPICS, max_iter=10, learning_method='online')

    topic_scores = lda_model.transform(vectorizer.transform(document_list))

    topic_list = []

    for doc in topic_scores:
        temp = doc.tolist()
        topic = temp.index(max(temp)) + 1
        topic_list.append(topic)

    d = {'Citation': document_id, 'Topic': topic_list}
    df = pd.DataFrame(d)
    df['Topic'].astype(int)
    case_topic = pd.merge(case_all, df, how='left', left_on='Neutral Citation', right_on='Citation')
    return case_topic
