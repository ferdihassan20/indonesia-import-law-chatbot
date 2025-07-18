RESPONSE_REFINEMENT_PROMPT = """
Kamu akan menerima dua hal:
1. Sebuah pertanyaan dari pengguna.
2. Sekumpulan dokumen hasil pencarian (dalam format CSV atau representasi vektor), yang kemungkinan relevan menurut sistem pencarian berbasis FAISS. Dokumen-dokumen ini berasal dari regulasi hukum terkait impor di Indonesia.

Tugasmu:
- Susun satu jawaban akhir yang **jelas, padat, dan relevan langsung terhadap pertanyaan pengguna**, berdasarkan informasi dari dokumen yang disediakan.
- **Gunakan hanya dokumen yang benar-benar relevan secara langsung**. Tidak semua dokumen dalam daftar harus digunakan.
- **Jangan menampilkan seluruh isi dokumen atau melakukan analisis per dokumen**.
- Fokus hanya pada penyampaian jawaban akhir secara profesional seperti seorang ahli hukum.

Penting:
- Jangan tampilkan alasan kenapa sebuah dokumen dipilih.
- Jangan tampilkan isi dokumen satu per satu.
- Tampilkan hasil akhir dalam dua bagian: jawaban akhir dan daftar `DOC_ID` dari dokumen yang benar-benar kamu gunakan.

FORMAT OUTPUT:
ANSWER: [Jawaban final kamu di sini, berdasarkan dokumen relevan]
DOC IDS: [DOC_ID1, DOC_ID2, ...]  ← hanya yang benar-benar digunakan

Contoh:
Pertanyaan:
Bagaimana prosedur impor barang konsumsi ke Indonesia?

Dokumen Potensial:
- DOC_ID: DOC1536, judul: Impor Barang Konsumsi, pasal: 37, isi: [isi dokumen]
- DOC_ID: DOC1538, judul: Peraturan Bea Masuk, pasal: 38, isi: [isi lain]
- DOC_ID: DOC1501, judul: Ekspor Barang, pasal: 14, isi: [tidak relevan]

Output yang benar:
ANSWER: Untuk mengimpor barang konsumsi ke Indonesia, importir harus memiliki perizinan dari instansi terkait, melengkapi dokumen kepabeanan, dan memenuhi ketentuan dalam Pasal 37 mengenai syarat dan tata cara impor.

DOC IDS: DOC1536

Sekarang mulailah menjawab berdasarkan dokumen yang diberikan di bawah ini.

Pertanyaan Pengguna:
{user_question}

Dokumen Potensial:
{retrieval_results}
"""
