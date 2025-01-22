from haystack.dataclasses import Document
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

# Criação do document store com Qdrant
document_store = QdrantDocumentStore(
    location=":memory:",
    index="empresa_vendedor_vendas",
    embedding_dim=768,  # Tamanho do embedding
    use_sparse_embeddings=False,
)

# Exemplo de dados de vendas
venda1 = Document(
    content="Venda 1: Detalhes sobre a venda",
    embedding=[1.23]*768,  # Exemplo de embedding da venda
    meta={"venda_id": 1, "vendedor_id": 101, "empresa_id": 202}
)

venda2 = Document(
    content="Venda 2: Detalhes sobre a venda",
    embedding=[2.34]*768,  # Exemplo de embedding da venda
    meta={"venda_id": 2, "vendedor_id": 101, "empresa_id": 202}
)

# Gravando documentos no document store
document_store.write_documents([venda1, venda2])

# Realizando uma busca com a empresa_id e vendedor_id
query_embedding = [2.34]*768  # Exemplo de embedding da consulta

# Buscando vendas associadas a uma empresa e vendedor específicos
retriever = QdrantEmbeddingRetriever(
    document_store=document_store,
    filters={"empresa_id": "202", "vendedor_id": "101"},
    top_k=5  # Retorna as 5 melhores correspondências
)

# Exibindo resultados
print("Resultados da busca:")
print(retriever.run(query_embedding=query_embedding))
