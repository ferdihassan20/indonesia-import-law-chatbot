INPUT_DECOMPOSER_PROMPT = '''
Tugasmu adalah memperbaiki, memperjelas, dan memecah pertanyaan pengguna menjadi beberapa pertanyaan atau pernyataan yang lebih spesifik jika diperlukan. Berikut adalah langkah-langkah yang harus kamu ikuti:

1. Periksa apakah input terlalu pendek atau tidak jelas. Jika iya, perluas dengan asumsi yang masuk akal berdasarkan konteks regulasi impor Indonesia.
2. Jika input mengandung lebih dari satu topik atau pertanyaan, pisahkan menjadi beberapa subpertanyaan yang eksplisit.
3. Gunakan bahasa yang jelas dan profesional, sesuai dengan konteks chatbot hukum/regulasi impor.
4. Jangan mengubah makna pertanyaan, hanya klarifikasi dan pecah jika perlu.

Contoh Input & Output:

Input:
"Apa saja aturan baru dari permendag no 16?"

Output:
1. Apa saja ketentuan baru yang diatur dalam Permendag Nomor 16 Tahun 2024?
2. Apakah ada perubahan terkait barang larangan dan pembatasan (lartas) dalam Permendag Nomor 16 Tahun 2024?
3. Apakah Permendag Nomor 16 Tahun 2024 menggantikan Permendag sebelumnya?

---

Input:
"{user_input}"

Output:
'''.strip()
