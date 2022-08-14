"""
-*- coding: utf-8 -*-
@File  : recommend.py
@Author: Yuki
@Date  : 16/06/2022
@Software : PyCharm
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse


def sortSparseMatrix(m, rev=True, only_indices=True):
    """ Sort a sparse matrix and return column index dictionary
    """
    col_dict = dict()
    for i in range(m.shape[0]):  # assume m is square matrix.
        d = m.getrow(i)
        s = zip(d.indices, d.data)
        sorted_s = sorted(s, key=lambda v: v[1], reverse=True)
        if only_indices:
            col_dict[i] = [element[0] for element in sorted_s]
        else:
            col_dict[i] = sorted_s
    return col_dict


def recommend(embedding, query_case):
    embedding.set_index(0, inplace=True)
    index_list = list(embedding.index)
    index = index_list.index(query_case)
    A_sparse = sparse.csr_matrix(embedding)
    similarities_sparse = cosine_similarity(A_sparse, dense_output=False)
    # print('pairwise sparse output:\n {}\n'.format(similarities_sparse))
    rec = sortSparseMatrix(similarities_sparse)[index]
    recommendation = []
    for i in rec:
        if 'p' in index_list[i] or 'c' in index_list[i] and i != index:
            recommendation.append(index_list[i])
    evaluation = [item for item in recommendation if item.startswith('p')]
    return recommendation[0:8], evaluation[0:10]
