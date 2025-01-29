from dataclasses import dataclass
from elasticsearch import Elasticsearch, helpers
import warnings
import json

warnings.filterwarnings("ignore")

@dataclass
class ElasticShark:
    index: str
    hosts: str
    basic_auth: tuple[str, str]
    verify_certs: bool = False

    def __post_init__(self):
        self.es = Elasticsearch(
            hosts=self.hosts,
            basic_auth=self.basic_auth,
            verify_certs=self.verify_certs,
        )

    @property
    def mapping(self):
        return {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "custom_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "order": {"type": "text"},
                    "family": {"type": "text"},
                    "family_common_name": {"type": "text"},
                    "genus": {"type": "text"},
                    "genus_author": {"type": "text"},
                    "species_name": {"type": "text"},
                    "species_author": {"type": "text"},
                    "species_common_name": {"type": "text"}
                }
            }
        }
    
    def delete_index(self):
        self.es.indices.delete(index=self.index)
    
    def create_index(self):
        self.es.indices.create(
            index=self.index,
            settings={
                'index': {
                    'number_of_shards': 3,
                    'number_of_replicas': 2
                }
            },
            body=self.mapping
        )
    
    def insert(self, shark: dict | list[dict]):
        if isinstance(shark, list):
            helpers.bulk(client=self.es, actions=shark, index=self.index) 
        else:
            self.es.index(index=self.index, body=shark)        

    def search(self, filters: dict, size: int = 1):
        should_clauses = []
        for key, value in filters.items():
            should_clauses.append({"match": {key: value}})
            should_clauses.append({"fuzzy": {key: {"value": value, "fuzziness": "AUTO"}}})

        query = {
            "size": size,
            "query": {
                "bool": {
                    "should": should_clauses
                }
            }
        }
        response = self.es.search(index=self.index, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]




# elastic_shark = ElasticShark(
#     index='shark_index',
#     hosts='https://localhost:9200',
#     basic_auth=('elastic', '+bp8O9L5xyjKMDr*KUix'),
#     verify_certs=False,
# )

# with open('data/wiki/sharks/sharks.json', 'r', encoding='utf-8') as file:
#     sharks_data = json.load(file)


# # for shark in sharks_data:
# s = elastic_shark.search(filters={"genus": "squatina"}, size=3)

# [print(json.dumps(shark, indent=2, ensure_ascii=False)) for shark in s]