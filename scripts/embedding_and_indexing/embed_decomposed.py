from sentence_transformers import SentenceTransformer
import re

class DecomposedEmbedder:
    def __init__(self, model_name="sentence-transformers/LaBSE"):
        """
        Initialize the embedder with the specified SentenceTransformer model.
        """
        self.embedder = SentenceTransformer(model_name)

    def parse_decomposed_text(self, decomposed_str):
        """
        Parse the decomposed string output into a list of individual texts.
        Assumes the decomposed output is numbered or newline separated.
        """
        # Split by lines and remove empty lines
        lines = [line.strip() for line in decomposed_str.splitlines() if line.strip()]
        # Remove numbering prefixes like "1. ", "2. ", etc.
        texts = [re.sub(r'^\d+\.\s*', '', line) for line in lines]
        return texts

    def embed_texts(self, texts):
        """
        Embed a list of texts using the SentenceTransformer model.
        Returns a numpy array of embeddings.
        """
        embeddings = self.embedder.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        return embeddings

    def embed_decomposed(self, decomposed_str):
        """
        Full pipeline: parse decomposed string and embed the resulting texts.
        Returns tuple (texts, embeddings).
        """
        texts = self.parse_decomposed_text(decomposed_str)
        embeddings = self.embed_texts(texts)
        return texts, embeddings


if __name__ == "__main__":
    # Example usage
    example_decomposed = """1. Apa saja ketentuan baru yang diatur dalam Permendag Nomor 16 Tahun 2024?
2. Apakah ada perubahan terkait barang larangan dan pembatasan (lartas) dalam Permendag Nomor 16 Tahun 2024?
3. Apakah Permendag Nomor 16 Tahun 2024 menggantikan Permendag sebelumnya?"""

    embedder = DecomposedEmbedder()
    texts, embeddings = embedder.embed_decomposed(example_decomposed)
    print("Parsed texts:")
    for t in texts:
        print("-", t)
    print(f"Generated embeddings shape: {embeddings.shape}")
