"""
-*- coding: utf-8 -*-
@File  : execute_graph_query.py
@Author: Yuki
@Date  : 25/07/2022
@Software : PyCharm
"""
import datetime
import json

from SPARQLWrapper import SPARQLWrapper, JSON, DIGEST, POST


class Judge:
    def __init__(self, name, link):
        self.name = name
        self.link = link


class Statue:
    def __init__(self, name, link=None):
        self.name = name
        self.link = link


class Citation:
    def __init__(self, name, link=None):
        self.name = name
        self.link = link


class Case:
    def __init__(self, label, title, court, status, link, topic, result=None, ):
        self.label = label
        self.title = title
        self.court = court
        self.status = status
        self.link = link
        self.result = result
        self.topic = topic


class SPARQLquery:
    def __init__(self, localhost):
        self.sparql = SPARQLWrapper(localhost)
        self.sparql.setReturnFormat(JSON)

    def query_case_exist(self, neutral_citation):
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?id WHERE { 
                ?case a ono:Case.
                ?case rdfs:label ?case_name.
                FILTER (?case_name = '""" + neutral_citation + """')
                FILTER EXISTS { ?case ono:hasLink ?link . }
                ?case ono:hasCitationID ?id.
        }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            if len(result) == 0:
                return False
            else:
                for r in result:
                    r_ = r['id']['value']
                    if str(r_).startswith('p'):
                        return r_
        except Exception as e:
            print(e)

    def query_recommendation(self, recommend_list):
        dic = {}
        for item in recommend_list:
            if str(item).startswith('p'):
                dic[item] = self.query_case_info(item)
            elif str(item).startswith('c'):
                dic[item] = self.query_statue_info_by_id(item)
        return dic

    def query_case_info(self, neutral_citation):
        dic = {}
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?label ?title ?court ?result ?status ?topic ?link WHERE { 
                ?case a ono:Case.
                ?case ono:hasCitationID ?id.
                ?case rdfs:label ?label.
                ?case ono:title ?title.
                ?case ono:jurisdiction ?c.
                ?c rdfs:label ?court.
                ?case ono:status ?status.
                ?case ono:topic ?topic.
                ?case ono:hasLink ?link.
                OPTIONAL {?case ono:result ?result}
                FILTER (?id = '""" + neutral_citation + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            r = ret["results"]["bindings"][0]
            if 'result' in r.keys():
                case = Case(r['label']['value'], r['title']['value'], r['court']['value'], r['status']['value'],
                            r['link']['value'], r['topic']['value'], r['result']['value'], )
            else:
                case = Case(r['label']['value'], r['title']['value'], r['court']['value'], r['status']['value'],
                            r['link']['value'], r['topic']['value'])
            dic['Label'] = case.label
            dic['Title'] = case.title
            dic['Court'] = case.court
            dic['Result'] = case.result
            dic['Status'] = case.status
            dic['Link'] = case.link
            dic['Topic'] = case.topic
        except Exception as e:
            print(e)

        dic['Judge'] = self.query_judge_info(neutral_citation)
        dic['Citation'] = self.query_citation_info(neutral_citation)
        dic['Statue'] = self.query_statue_info(neutral_citation)
        return dic

    def query_judge_info(self, neutral_citation):
        judge_list = []
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?name ?link WHERE { 
                ?case a ono:Case.
                ?case ono:hasCitationID ?id.
                ?case ono:judgedBy ?judge.
                ?judge rdfs:label ?name.
                OPTIONAL { ?judge ono:hasLink ?link }
                FILTER (?id = '""" + neutral_citation + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            for r in result:
                judge = Judge(r['name']['value'], r['link']['value'])
                judge_list.append(judge.__dict__)
        except Exception as e:
            print(e)
        return judge_list

    def query_statue_info(self, neutral_citation):
        statue_list = []
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?name ?link WHERE { 
                ?case a ono:Case.
                ?case ono:hasCitationID ?id.
                ?case ono:cite ?statue.
                ?statue a ono:Statue;rdfs:label ?name.
                OPTIONAL{?statue ono:hasLink ?link}
                FILTER (?id = '""" + neutral_citation + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            for r in result:
                if 'link' in r.keys():
                    statue = Statue(r['name']['value'], r['link']['value'])
                else:
                    statue = Statue(r['name']['value'])
                statue_list.append(statue.__dict__)
        except Exception as e:
            print(e)
        return statue_list

    def query_statue_info_by_id(self, statue_id):
        statue_list = []
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?name ?link WHERE { 
                ?statue a ono:Statue;rdfs:label ?name;ono:hasInstrumentID ?id
                OPTIONAL{?statue ono:hasLink ?link}
                FILTER (?id = '""" + statue_id + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            for r in result:
                if 'link' in r.keys():
                    statue = Statue(r['name']['value'], r['link']['value'])
                else:
                    statue = Statue(r['name']['value'])
                statue_list.append(statue.__dict__)
        except Exception as e:
            print(e)
        return statue_list

    def query_citation_info(self, neutral_citation):
        citation_list = []
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?name ?link WHERE { 
                ?case a ono:Case.
                ?case ono:hasCitationID ?id.
                ?case ono:citeCase ?citation.
                ?citation rdfs:label ?name.
                OPTIONAL{?citation ono:hasLink ?link}
                FILTER (?id = '""" + neutral_citation + """')
        }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            for r in result:
                if 'link' in r.keys():
                    citation = Citation(r['name']['value'], r['link']['value'])
                else:
                    citation = Citation(r['name']['value'])
                citation_list.append(citation.__dict__)
        except Exception as e:
            print(e)
        return citation_list

    def query_statue_id_by_name(self, name):
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?id WHERE { 
                ?instrument a ono:Statue;rdfs:label ?name;ono:hasStatueID ?id.
                FILTER (?name = '""" + name + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            if len(result) == 0:
                return False
            else:
                return result[0]['id']['value']
        except Exception as e:
            print(e)

    def query_judge_id_by_name(self, name):
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?id WHERE { 
                ?judge a ono:Judge;rdfs:label ?name;ono:hasJudgeID ?id.
                FILTER (?name = '""" + name + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            if len(result) == 0:
                return False
            else:
                return result[0]['id']['value']
        except Exception as e:
            print(e)

    def query_citation_id_by_name(self, name):
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?id WHERE { 
                ?case a ono:Case;rdfs:label ?name;ono:citedBy ?c;ono:hasCitationID ?id.
                FILTER (?name = '""" + name + """')
            }
        """
        self.sparql.setQuery(query_str)
        try:
            ret = self.sparql.queryAndConvert()
            result = ret["results"]["bindings"]
            if len(result) == 0:
                return False
            else:
                return result[0]['id']['value']
        except Exception as e:
            print(e)

    def insert_new_case_info(self, dic):
        case_url = "<http://www.yuxin.com/law/Case/{}>".format(dic['Neutral Citation'][0])
        date_d = datetime.datetime.strptime(dic['Date Delivered'][0], '%d %B %Y').strftime('%Y-%m-%d')
        date_u = datetime.datetime.strptime(dic['Date Uploaded'][0], '%d %B %Y').strftime('%Y-%m-%d')
        state = case_url + ' ono:judgedBy "' + dic['Judgment By'][0] + '".' + \
                case_url + ' ono:jurisdiction "' + dic['Court'][0] + '".' + \
                case_url + ' ono:result "' + dic['Result'][0] + '".' + \
                case_url + ' ono:title "' + dic['Title'][0] + '".' + \
                case_url + ' ono:plaintiff "' + dic['Plaintiff'][0] + '".' + \
                case_url + ' ono:defendant "' + dic['Defendant'][0] + '".' + \
                case_url + ' ono:deliverDate "' + date_d + '"^^xsd:date.' + \
                case_url + ' ono:deliverDate "' + date_u + '"^^xsd:date.' + \
                case_url + ' ono:hasLink "' + dic['Case Link'][0] + '".'
        print(state)
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA{ """ + state + """ }
        """
        self.sparql.setHTTPAuth(DIGEST)
        self.sparql.setCredentials("admin", "13802870556")
        self.sparql.setMethod(POST)
        self.sparql.setQuery(query_str)
        try:
            results = self.sparql.query()
            return results.info()
        except Exception as e:
            print(e)

    def delete_new_case_info(self, dic):
        case_url = "<http://www.yuxin.com/law/Case/{}>".format(dic['Neutral Citation'][0])
        date_d = datetime.datetime.strptime(dic['Date Delivered'][0], '%d %B %Y').strftime('%Y-%m-%d')
        date_u = datetime.datetime.strptime(dic['Date Uploaded'][0], '%d %B %Y').strftime('%Y-%m-%d')
        state = case_url + ' ono:judgedBy "' + dic['Judgment By'][0] + '".' + \
                case_url + ' ono:jurisdiction "' + dic['Court'][0] + '".' + \
                case_url + ' ono:result "' + dic['Result'][0] + '".' + \
                case_url + ' ono:title "' + dic['Title'][0] + '".' + \
                case_url + ' ono:plaintiff "' + dic['Plaintiff'][0] + '".' + \
                case_url + ' ono:defendant "' + dic['Defendant'][0] + '".' + \
                case_url + ' ono:deliverDate "' + date_d + '"^^xsd:date.' + \
                case_url + ' ono:deliverDate "' + date_u + '"^^xsd:date.' + \
                case_url + ' ono:hasLink "' + dic['Case Link'][0] + '".'
        print(state)
        query_str = """
            PREFIX ono: <http://www.yuxin.com/law/ontologies/2022/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE DATA{ """ + state + """ }
        """

        self.sparql.setHTTPAuth(DIGEST)
        self.sparql.setCredentials("admin", "13802870556")
        self.sparql.setMethod(POST)
        self.sparql.setQuery(query_str)
        try:
            results = self.sparql.query()
            return results.info()
        except Exception as e:
            print(e)
