import os
import csv
import re

# Path input dan output
INPUT_FOLDER = "datasets/cleaned_texts"
OUTPUT_FOLDER = "datasets/csv"

# Buat folder output jika belum ada
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Pola regex untuk mendeteksi struktur hukum
BAB_PATTERN = re.compile(r"^(BAB\s+[IVXLCDM]+.*?)$", re.IGNORECASE)
PASAL_PATTERN = re.compile(r"^(Pasal\s+\d+.*?)$")  
PASAL_CHANGE_PATTERN = re.compile(r"^(\d+)\. Ketentuan Pasal (\d+) diubah.*$")  
ANGKA_PATTERN = re.compile(r"^(\d+)\..*?$")  
AYAT_PATTERN = re.compile(r"^\((\d+)\)\s+(.*?)$")  
PENJELASAN_PATTERN = re.compile(r"^(PASAL DEMI PASAL|PENJELASAN ATAS PERATURAN)", re.IGNORECASE)
REMOVE_PATTERN = re.compile(r"(Ditetapkan di|Menimbang|Mengingat|Memutuskan)", re.IGNORECASE)

def extract_structure(text, doc_id, doc_name):
    """Ekstrak struktur hukum dari teks"""
    rows = []
    
    current_bab = None
    current_bagian = None
    current_pasal = None
    current_angka = None
    in_penjelasan = False  # Flag untuk mendeteksi apakah sudah masuk ke bagian penjelasan

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line or REMOVE_PATTERN.search(line):
            continue  # Skip teks yang tidak relevan

        if PENJELASAN_PATTERN.match(line):
            in_penjelasan = True
            continue  # Tidak perlu diproses, hanya sebagai indikator

        if BAB_PATTERN.match(line):
            current_bab = line
            current_bagian = None  # Reset bagian
        elif PASAL_PATTERN.match(line):
            current_pasal = line
            current_angka = None  # Reset angka
        elif PASAL_CHANGE_PATTERN.match(line):
            match = PASAL_CHANGE_PATTERN.match(line)
            current_pasal = f"Pasal {match.group(2)}"
            current_angka = match.group(1)
        elif ANGKA_PATTERN.match(line):
            current_angka = re.sub(r"\\.", "", line)  # Hapus titik agar jadi angka murni
        elif AYAT_PATTERN.match(line):
            match = AYAT_PATTERN.match(line)
            ayat = match.group(1)
            isi = match.group(2)
            penjelasan = "" if not in_penjelasan else isi
            rows.append([doc_id, doc_name, current_bab, current_bagian, current_pasal, current_angka, ayat, isi if not in_penjelasan else "", penjelasan])
        else:
            # Jika bukan pola yang dikenali, mungkin ini bagian dari isi sebelumnya
            if rows:
                if in_penjelasan:
                    rows[-1][8] += f" {line}"  # Tambahkan ke penjelasan sebelumnya
                else:
                    rows[-1][7] += f" {line}"  # Tambahkan ke isi sebelumnya
    
    return rows

def process_files():
    """Baca semua file .txt, ekstrak struktur, lalu simpan sebagai CSV"""
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    
    for idx, filename in enumerate(sorted(files), start=1):
        doc_id = f"DOC{idx:03d}"  # Format DOC001, DOC002, dst.
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename.replace(".txt", ".csv"))

        with open(input_path, "r", encoding="utf-8") as file:
            text = file.read()

        rows = extract_structure(text, doc_id, filename)

        # Simpan ke CSV
        with open(output_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["doc_id", "nama_dokumen", "bab", "bagian", "pasal", "angka", "ayat", "isi", "penjelasan"])
            writer.writerows(rows)

        print(f"✅ Berhasil memproses: {filename} → {doc_id}")

if __name__ == "__main__":
    process_files()
