from glob import glob
import json
from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
import os
import tiktoken


# Write documents to InMemoryDocumentStore
document_store = InMemoryDocumentStore()

total_tokens = 0
documents = []
for i, path in enumerate(glob('data/metrics-vad/*.json')):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data['transcription_metrics'] is None:
        continue
    if 'transcription' not in data['transcription_metrics']:
        continue

    tokens = tiktoken.get_encoding("o200k_base").encode(data['transcription_metrics']['transcription'])
    total_tokens += len(tokens)

    documents.append(Document(
        id=str(i),
        content=data['transcription_metrics']['transcription']
    ))
document_store.write_documents(documents)

print('-'*40)
print(f"Total documents: {len(documents)}")
print(f"Total tokens: {total_tokens}")
print('-'*40)


# Build a RAG pipeline
prompt_template = """
Dado essas chamadas telefônicas transcritas de um VOIP, responda a pergunta a seguir.
[Chamadas telefônicas]:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{question}}
Answer:
"""

retriever = InMemoryBM25Retriever(document_store=document_store, top_k=2)
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(api_key=Secret.from_token(os.environ['OPENAI_API_KEY']))

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")

# Ask a question
while True:
    question = input('Pergunta: ')
    results = rag_pipeline.run(
        {
            "retriever": {"query": question},
            "prompt_builder": {"question": question},
        }
    )

    print(results['llm']['meta'])
    print()
    print(results["llm"]["replies"])
