import requests
from elasticsearch import Elasticsearch
import json
import pickle


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


def write_pickle():
    example = [['this drug causes cancer', 'LELFJOILW', 'disease A', 'description A'], 
            ['this is also a drug', 'LWLWOJ42', 'disease B', 'description B'],
            ['test druggggg', 'LKJFELKL', 'disease C', 'description C']]
    pickle.dump(example, open('test.pkl', 'wb'))


def ingest_scrape(f):
    with open(f, 'rb') as p:
        molecules = pickle.load(p)

        i = 1
        for molecule in molecules:
            '''
            print(molecule[0])
            print(molecule[1])
            return
            '''
            insert = '{"text": "' + molecule[0] + '", "smiles": "' + molecule[1] + '"}'
            print(insert)
            ret = es.index(index='novogen', doc_type='molecules', id=i, body=json.loads(insert))
            print(ret)
            print('\n')
            i = i + 1


def perform_query(text):
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


#ingest_scrape()
write_pickle()
ingest_scrape('test.pkl')
print(perform_query('drug'))
