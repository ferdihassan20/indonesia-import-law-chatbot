import os
import pandas as pd
import pickle
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/LaBSE"  
embedder = SentenceTransformer(MODEL_NAME)

DATA_DIR = 'datasets/cleaned_csv'
OUTPUT_INDEX_PATH = 'datasets/embeddings/faiss_index.index'
OUTPUT_METADATA_PATH = 'datasets/embeddings/metadata.pkl'

all_texts = []
all_metadatas = []

for filename in tqdm(os.listdir(DATA_DIR)):
    if filename.endswith('.csv'):
        filepath = os.path.join(DATA_DIR, filename)
        df = pd.read_csv(filepath)

        for idx, row in df.iterrows():
            isi = str(row.get('isi', '')).strip()
            penjelasan = str(row.get('penjelasan', '')).strip()

            if not isi or not penjelasan:
                logger.info(f"Skipping row {idx} in file {filename} due to empty 'isi' or 'penjelasan'")
                continue

            combined_text = isi + '\n' + penjelasan

            all_texts.append(combined_text)
            all_metadatas.append({
                "filename": filename,
                "doc_id": row.get('doc_id', None),
                "nama_dokumen": row.get('nama_dokumen', None),
                "bab": row.get('bab', None),
                "bagian": row.get('bagian', None),
                "pasal": row.get('pasal', None),
                "angka": row.get('angka', None),
                "ayat": row.get('ayat', None),
                "isi": isi,
                "penjelasan": penjelasan
            })

print(f"Embedding {len(all_texts)} entries...")
embeddings = embedder.encode(all_texts, show_progress_bar=True, convert_to_numpy=True)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

os.makedirs('datasets/embeddings', exist_ok=True)
faiss.write_index(index, OUTPUT_INDEX_PATH)
with open(OUTPUT_METADATA_PATH, 'wb') as f:
    pickle.dump(all_metadatas, f)

print(f"Done! Total embedded: {len(all_texts)}")
print(f"FAISS index saved to: {OUTPUT_INDEX_PATH}")
