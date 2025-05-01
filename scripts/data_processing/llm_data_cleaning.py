import os
import re
import logging
import openai
import chardet
import tiktoken
import sys

from tqdm import tqdm
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from models.llm_runtime import LLMRuntime
from utils.prompt.cleaning_prompt import *

# Konfigurasi logging untuk debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LLMDataCleaning(LLMRuntime):

    def detect_encoding(self, file_path):
        """ Mendeteksi encoding file sebelum dibuka """
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # Ambil sebagian data untuk analisis
        result = chardet.detect(raw_data)
        return result["encoding"]

    def fix_file_name(self):
        """ Memperbaiki format nama file agar konsisten """
        root_dir = "datasets/raw_texts"
        list_legal_docs = os.listdir(root_dir)

        num_convert = {f"page_{i}.txt": f"page_0{i}.txt" for i in range(1, 10)}

        for legal_doc in tqdm(list_legal_docs, desc="Fixing file names"):
            list_page = os.listdir(f"{root_dir}/{legal_doc}")

            for old_name in list_page:
                doc_name = "_".join(old_name.split("_")[:-2])
                page_num = "_".join(old_name.split("_")[-2:])

                if page_num in num_convert:
                    new_doc_name = f"{doc_name}_{num_convert[page_num]}"
                    os.rename(f"{root_dir}/{legal_doc}/{old_name}", f"{root_dir}/{legal_doc}/{new_doc_name}")

    # def llm_clean_doc(self, text):
    #     """ Membersihkan teks dengan model OpenAI """
    #     prompt = LEGAL_DOC_CLEANING_PROMPT.format(legal_paragraph=text)
    #     response = self.generate(prompt=prompt)
    #     return response  # Kembalikan hasil cleaning untuk disimpan

    def llm_clean_doc(self, text):
        """ Membersihkan teks dengan LLM dalam bentuk chunk agar tidak melebihi batas token """
        chunks = self.chunk_text(text, chunk_size=4000)  # Bagi teks menjadi beberapa bagian
        cleaned_text = []  

        for i, chunk in enumerate(chunks):
            logging.info(f"🔹 Processing chunk {i+1}/{len(chunks)}")
            prompt = LEGAL_DOC_CLEANING_PROMPT.format(legal_paragraph=chunk)
            response = self.generate(prompt=prompt)
            cleaned_text.append(response)

        return "\n".join(cleaned_text)  # Gabungkan semua hasil cleaning menjadi satu


    def load_dataset(self):
        """ Memproses dan membersihkan seluruh dataset hukum, lalu menyimpan hasilnya """
        self.fix_file_name()
        root_dir = "datasets/raw_texts"
        output_dir = "datasets/cleaned_texts"
        
        # Buat folder output jika belum ada
        os.makedirs(output_dir, exist_ok=True)

        list_legal_docs = os.listdir(root_dir)
        for legal_doc in tqdm(list_legal_docs, desc="Processing documents"):
            output_path = os.path.join(output_dir, f"{legal_doc}.txt")
            
            # Cek apakah file sudah ada, jika iya maka skip
            if os.path.exists(output_path):
                logging.info(f"⏩ {legal_doc} sudah diproses, skipping...")
                continue  # Skip ke dokumen berikutnya

            list_page = os.listdir(f"{root_dir}/{legal_doc}")      
            all_legal_text = ""

            for page_name in list_page:
                file_path = f"{root_dir}/{legal_doc}/{page_name}"
                
                # Deteksi encoding terlebih dahulu
                encoding = self.detect_encoding(file_path)

                with open(file_path, "r", encoding=encoding, errors="replace") as file:
                    legal_text = file.read()
                    all_legal_text += f"{legal_text}\n"

            # Bersihkan teks dengan LLM
            cleaned_text = self.llm_clean_doc(text=all_legal_text)

            # Simpan hasil cleaning dalam directory output
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(cleaned_text)

            logging.info(f"{legal_doc} telah dibersihkan dan disimpan di {output_path}")


    def chunk_text(self, text, chunk_size=4000):
        """ Memecah teks panjang menjadi beberapa bagian agar tidak melebihi batas token """
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoding.encode(text)

        chunks = []
        for i in range(0, len(tokens), chunk_size):
            chunk_tokens = tokens[i:i+chunk_size]  # Ambil sebagian token
            chunk_text = encoding.decode(chunk_tokens)  # Konversi token kembali ke teks
            chunks.append(chunk_text)

        return chunks

    def test_running(self):
        """ Test API OpenAI dengan prompt sederhana """
        response = self.generate(prompt="Can you tell me how to make Asian fried rice?")
        print(response)

if __name__ == '__main__':
    data_cleaning = LLMDataCleaning()
    data_cleaning.load_dataset()
    # data_cleaning.test_running()
