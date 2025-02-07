from sentence_transformers import SentenceTransformer
from timeit import default_timer
from tqdm import tqdm

sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

t0 = default_timer()
for i in tqdm(range(100)):
    embeddings = model.encode(sentences)
t1 = default_timer()

print(t1-t0)