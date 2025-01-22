from glob import glob
import json
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from haystack_integrations.components.retrievers.opensearch import OpenSearchBM25Retriever
from haystack_integrations.components.retrievers.opensearch import OpenSearchEmbeddingRetriever

# from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
# from haystack_integrations.components.retrievers.qdrant import QdrantHybridRetriever
from haystack import Document

document_store = OpenSearchDocumentStore(
    hosts="http://localhost:9200", 
    use_ssl=True,
    verify_certs=False,
    http_auth=("admin", "admin")
)

documents = []
for i, path in enumerate(glob('data/metrics-vad/*.json')):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)#['transcription_metrics']['transcription']
    if data['transcription_metrics'] is None:
        continue
    if 'transcription' not in data['transcription_metrics']:
        continue

    documents.append(Document(
        id=str(i),
        content=data['transcription_metrics']['transcription']
    ))
document_store.write_documents(documents)