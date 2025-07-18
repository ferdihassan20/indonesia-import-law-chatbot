import os
import pickle
import faiss
import numpy as np
from scripts.embedding_and_indexing.embed_decomposed import DecomposedEmbedder
from scripts.caching.semantic_cache import SemanticCache

class RetrievalPipeline:
    def __init__(self,
                 faiss_index_path='datasets/embeddings/faiss_index.index',
                 metadata_path='datasets/embeddings/metadata.pkl',
                 semantic_cache_index='datasets/semantic_cache/faiss_cache.index',
                 semantic_cache_metadata='datasets/semantic_cache/metadata.pkl',
                 embedding_model_name="sentence-transformers/LaBSE"):
        
        self.embedder = DecomposedEmbedder(model_name=embedding_model_name)

        self.semantic_cache = SemanticCache(index_path=semantic_cache_index,
                                            metadata_path=semantic_cache_metadata)

        self.faiss_index_path = faiss_index_path
        self.metadata_path = metadata_path
        self.faiss_index = None
        self.metadata = []

        if os.path.exists(faiss_index_path) and os.path.exists(metadata_path):
            self.faiss_index = faiss.read_index(faiss_index_path)
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            raise FileNotFoundError("FAISS index or metadata file not found for dataset embeddings.")

    def search_faiss(self, embedding, top_k=3):
        """
        Search the FAISS index with the given embedding and return top_k results.
        """
        if self.faiss_index is None:
            raise ValueError("FAISS index not loaded.")

        embedding = embedding.reshape(1, -1)
        distances, indices = self.faiss_index.search(embedding, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    "distance": dist,
                    "metadata": meta
                })
        return results

    def query(self, decomposed_str, cache_threshold=0.85, top_k=3):
        """
        Given a decomposed string input, perform semantic cache check and fallback FAISS retrieval.
        Returns a dict mapping each decomposed question to either cached response or FAISS results.
        """
        results = {}
        texts, embeddings = self.embedder.embed_decomposed(decomposed_str)

        for text, embedding in zip(texts, embeddings):
            cached_response = self.semantic_cache.search(text, threshold=cache_threshold)
            if cached_response is not None:
                results[text] = {
                    "source": "cache",
                    "response": cached_response
                }
            else:
                faiss_results = self.search_faiss(embedding, top_k=top_k)
                results[text] = {
                    "source": "faiss",
                    "results": faiss_results
                }
        return results


if __name__ == "__main__":
    example_decomposed = """1. Apa saja ketentuan baru yang diatur dalam Permendag Nomor 16 Tahun 2024?
2. Apakah ada perubahan terkait barang larangan dan pembatasan (lartas) dalam Permendag Nomor 16 Tahun 2024?
3. Apakah Permendag Nomor 16 Tahun 2024 menggantikan Permendag sebelumnya?"""

    pipeline = RetrievalPipeline()
    output = pipeline.query(example_decomposed)
    for question, result in output.items():
        print(f"Question: {question}")
        if result["source"] == "cache":
            print(f"Cached Response: {result['response']}")
        else:
            print("FAISS Results:")
            for res in result["results"]:
                print(f" - Distance: {res['distance']}, Metadata: {res['metadata']}")
        print()
