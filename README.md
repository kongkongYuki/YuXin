# YuXin's Dissertation Project

This is the repository for Yu Xin postgraduate dissertaion project. Used to store all source files, intermediate files, output files, code, ontologies, and mappings covered in the paper.

## Table of Contents

- [Dependencies](#dependencies)
- [Tools](#tool)
- [API](#api)
- [Project Description](#description)
- [Demo](#demo)

## Dependencies
According to the requirements.txt

## Tools
R2RML: https://github.com/chrdebru/r2rml

GraphDB: https://graphdb.ontotext.com/

Protégé: https://protege.stanford.edu/

Widoco: https://github.com/dgarijo/Widoco

## API
```
export FLASK_APP=flaskapi.py
python -m flask run
```
example request: http://127.0.0.1:5000/api/2022_IEHC_83

## Project Description
Input - the case of user input. Download from courts.ie according to neutral citation.


Ontology - Ontology design and mapping

* Ontology/CSVFiles: the source file for Statue mapping.

* Ontology/myDocumentation: documentation generated by WIDOCO.
 
* Ontology/ono.owl: ontology file

* Ontology/mapping.ttl: mapping file

* Ontology/config.properties: r2rml config to state where source files


OpenHINE - Graph Embedding(MetaGraph2Vec) implementation

* OpenHINE/dataset/test/edge.txt: dataset

* OpenHINE/dataset/test/label.txt: label

* OpenHINE/output/embedding/MetaGraph2vec/test_node.txt: embedding matrix

* OpenHINE/output/temp/MetaGraph2vec/graph_rw.txt: metapath generated by random walk


Output - System temp output for further processing

* Output/Recommendation: sample recommendation results

* Output/mapping.output.ttl: mapping output

* Output/\*.csv: tabular structured data gathered by create_repository.py


SourceData - Unstructured and semi-structured data

* SourceData/CaseFolder: docx files

* SourceData/Crawl: merged information from crawler

* SourceData/Nlp: merged information from nlp

* SourceData/instrument.csv: after human screening


All the python files explanation see Chapter 4 of the dissertation

## Demo
Pipeline Demo:

https://drive.google.com/file/d/1gYsTZYxpVuk6bMqGW56P1ilt86e5PnL6/view?usp=sharing


Ontology Demo:

https://drive.google.com/file/d/1P67YDemJdSwStz9wQOaCWBwWeFSzvxsk/view?usp=sharing
