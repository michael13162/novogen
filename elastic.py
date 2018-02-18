import requests
from elasticsearch import Elasticsearch
import json


es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def test():
    es.index(index='novogen', doc_type='molecules', id=1, body=json.loads('{"text": "this", "smiles": "1234"}'))
    es.index(index='novogen', doc_type='molecules', id=2, body=json.loads('{"text": "this is", "smiles": "5678"}'))

    ret = es.search(index="novogen", body={
        "query": {
            "match" : {
              "text":    "this", 
            }
          }
        })

    hits = {}
    for hit in ret['hits']['hits']:
        hits[hit['_source']['smiles']] = hit['_score']

    for key, value in sorted(hits.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        print "%s: %s" % (key, value)



def ingest_scrape():
    molecules = pickle()

    i = 1
    for molecule in molecules:
        es.index(index='novogen', doc_type='molecules', id=i, body=json.loads('{"text": ' + molecule.first + ', "smiles": ' + molecule.second + '}'))
        i = i + 1


def search(text):
    ret = es.search(index="novogen", body={
        "query": {
            "match" : {
                "text": text, 
            }
          }
        })

    hits = {}
    for hit in ret['hits']['hits']:
        hits[hit['_source']['smiles']] = hit['_score']

    return sorted(hits.iteritems(), key=lambda (k,v): (v,k), reverse=True)


test()

