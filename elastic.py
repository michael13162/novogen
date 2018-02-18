import requests
from elasticsearch import Elasticsearch
import json
import pickle
from model.scrape import Molecule


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
    example1 = Molecule('cancer', 'drug_a', 'test', 'SLFKJDL')
    example2 = Molecule('allgeries', 'drug_b', 'test', 'lLKEJLKEJ')
    example3 = Molecule('cold', 'drug_c', 'test', 'SLLKD')
    pickle.dump([example1, example2, example3], open('test.pkl', 'wb'))


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

            text = molecule.disease + ' ' + molecule.drug_name + ' ' + molecule.smiles.strip() + ' ' + molecule.molecule_name
            insert = '{"text": "' + text + '", "smiles": "' + molecule.smiles.strip() + '", "disease": "' + molecule.disease + '", "drug_name": "' + molecule.drug_name + '", "molecule_name": "' + molecule.molecule_name + '"}'
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

    print('ret' + str(ret))
    hits = {}
    for hit in ret['hits']['hits']:
        print('hit' + str(hit))
        hits[hit['_source']['smiles']] = {'score': hit['_score'],
                                          'disease': hit['_source']['disease'],
                                          'drug_name': hit['_source']['drug_name'],
                                          'molecule_name': hit['_source']['molecule_name']}

    return sorted(hits.iteritems(), key=lambda (k,v): (v['score'],k), reverse=True)


#write_pickle()
#ingest_scrape('RESULT.pkl')
#print(perform_query('cold'))
