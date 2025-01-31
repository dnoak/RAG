from elasticsearch import Elasticsearch

def get_top_k_searches(k: int, filters: dict) -> list:
    es = Elasticsearch()

    query = {
        "size": k,
        "query": {
            "bool": {
                "must": [
                    {"match": {key: value}} for key, value in filters.items() 
                    if value is not None
                ]
            }
        }
    }

    response = es.search(index="sharks", body=query)
    return [hit["_source"] for hit in response["hits"]["hits"]]
