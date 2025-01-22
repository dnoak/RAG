import openai
import os
import numpy as np

openai.api_key = os.environ['OPENAI_API_KEY']

texto1 = "first example of text to generate sentence embedding."
texto2 = "segundo exemplo textual gerador de embedding de frases."
texto3 = "terceiro exemplo textual gerador de nada a ver com o primeiro"

response1 = openai.embeddings.create(
    input=texto1,
    model="text-embedding-ada-002"
)
response2 = openai.embeddings.create(
    input=texto2,
    model="text-embedding-ada-002"
)
response3 = openai.embeddings.create(
    input=texto3,
    model="text-embedding-ada-002"
)

embedding1 = response1.data[0].embedding
embedding2 = response2.data[0].embedding
embedding3 = response3.data[0].embedding

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print(f"similaridade 1 com 2: {cosine_similarity(embedding1, embedding2)}")
print(f"similaridade 1 com 3: {cosine_similarity(embedding1, embedding3)}")
print(f"similaridade 2 com 3: {cosine_similarity(embedding2, embedding3)}")