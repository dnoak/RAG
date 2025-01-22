from elasticsearch import Elasticsearch
import warnings
import json

warnings.filterwarnings("ignore")

def pprint(data: dict):
    if not isinstance(data, dict):
        data = dict(data)
    print(json.dumps(data, indent=4, ensure_ascii=False))

es = Elasticsearch(
    hosts='https://localhost:9200',
    basic_auth=('elastic', 'yaR=1Y0EOR-1YC_VsxgU'),
    verify_certs=False,
)
client_info = es.info()
# print('Connection to Elasticsearch server successful')
# print(client_info.body)

es.indices.delete(index='test_index')
es.indices.create(
    index='test_index',
    settings={
        'index': {
            'number_of_shards': 3,
            'number_of_replicas': 2
        }
    }
)

mapping = {
    'a': 'keyword',
    'b': 'keyword',
    'c': 'keyword',
    'data': 'text' 
}

document = {
    'a': 'key1',
    'b': 'key2',
    'c': 'key3',
    'data': 'dados do documento' 
}

document = {
    'name': 'John Doe',
    'age': 30,
    'city': 'New York',
    'created_at': '2022-01-01T00:00:00'
}

response = es.index(index='test_index', body=document)
print(response)
print()

index_mapping = es.indices.get_mapping(index='test_index')
pprint(index_mapping['test_index']['mappings']['properties'])