
import os
import csv
import re

# Path input dan output
INPUT_FOLDER = "datasets/cleaned_texts"
OUTPUT_FOLDER = "datasets/cleaned_csv"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Pola regex fleksibel
BAB_PATTERN = re.compile(r"^(BAB\s+[IVXLCDM]+.*?)$", re.IGNORECASE)
PASAL_PATTERN = re.compile(r"^(Pasal\s+\d+)(.*)$", re.IGNORECASE)
PASAL_FLEX_PATTERN = re.compile(r"^(?:\d+\.\s*)?Ketentuan Pasal (\d+)\s+diubah.*$", re.IGNORECASE)
ANGKA_PATTERN = re.compile(r"^(\d+)\.\s+(.*)$")
AYAT_PATTERN = re.compile(r"^\((\d+)\)\s+(.*)$")
PENJELASAN_PATTERN = re.compile(r"^(PASAL DEMI PASAL|PENJELASAN ATAS PERATURAN)", re.IGNORECASE)
REMOVE_PATTERN = re.compile(r"(Ditetapkan di|Menimbang|Mengingat|Memutuskan|Lembaran Negara)", re.IGNORECASE)

def extract_structure(text, doc_id, doc_name):
    rows = []
    current_bab = None
    current_bagian = None
    current_pasal = None
    current_angka = None
    in_penjelasan = False

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line or REMOVE_PATTERN.search(line):
            continue

        if PENJELASAN_PATTERN.match(line):
            in_penjelasan = True
            continue

        if BAB_PATTERN.match(line):
            current_bab = line.strip()
            current_bagian = None
            continue

        if PASAL_PATTERN.match(line):
            match = PASAL_PATTERN.match(line)
            current_pasal = match.group(1).strip()
            current_angka = None
            continue

        if PASAL_FLEX_PATTERN.match(line):
            match = PASAL_FLEX_PATTERN.match(line)
            current_pasal = f"Pasal {match.group(1)}"
            continue

        if ANGKA_PATTERN.match(line):
            match = ANGKA_PATTERN.match(line)
            current_angka = match.group(1)
            content = match.group(2)
            rows.append([doc_id, doc_name, current_bab, current_bagian, current_pasal, current_angka, "", content, ""])
            continue

        if AYAT_PATTERN.match(line):
            match = AYAT_PATTERN.match(line)
            ayat = match.group(1)
            isi = match.group(2)
            penjelasan = isi if in_penjelasan else ""
            rows.append([
                doc_id,
                doc_name,
                current_bab,
                current_bagian,
                current_pasal,
                current_angka,
                ayat,
                "" if in_penjelasan else isi,
                penjelasan
            ])
            continue

        # Lanjutan dari isi atau penjelasan sebelumnya
        if rows:
            if in_penjelasan:
                rows[-1][8] += f" {line}"
            else:
                rows[-1][7] += f" {line}"

    return rows

def process_files():
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    for idx, filename in enumerate(sorted(files), start=1):
        doc_id = f"DOC{idx:03d}"
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename.replace(".txt", ".csv"))

        with open(input_path, "r", encoding="utf-8") as file:
            text = file.read()

        rows = extract_structure(text, doc_id, filename)

        with open(output_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["doc_id", "nama_dokumen", "bab", "bagian", "pasal", "angka", "ayat", "isi", "penjelasan"])
            writer.writerows(rows)

        print(f"✅ Berhasil memproses: {filename} → {doc_id}")

if __name__ == "__main__":
    process_files()
