LEGAL_DOC_CLEANING_PROMPT = '''
- Di bawah ini merupakan hasil ekstraksi teks dari dokumen peraturan dan/atau undang-undang terkait impor di Indonesia.  
- Hasil ekstraksi ini mungkin mengandung:  
  1. Kesalahan ejaan yang perlu diperbaiki agar sesuai dengan ejaan yang benar dalam bahasa Indonesia.  
  2. Susunan kata atau kalimat yang tidak sesuai urutan, sehingga perlu disusun kembali agar mudah dipahami dan sesuai dengan struktur aslinya.  
  3. Simbol atau karakter asing yang tidak relevan dengan konteks peraturan, sehingga perlu dihapus.  
  4. Format penulisan yang beragam akibat adanya tabel dalam dokumen asli, sehingga perlu disesuaikan agar seragam.  

- Tugas Anda  
  1. Membersihkan dan merapikan teks agar dapat dipahami dengan baik dan mengikuti sistematika baku dalam peraturan perundang-undangan Indonesia.  
  2. Memastikan urutan teks sesuai dengan struktur asli yang umum digunakan dalam peraturan, yaitu:  
     - Pembukaan (DENGAN RAHMAT TUHAN YANG MAHA ESA...)  
     - Menimbang  
     - Mengingat  
     - Memutuskan  
     - Isi pasal-pasal  
  3. Menggunakan huruf kecil untuk seluruh teks kecuali pada bagian yang memang lazim menggunakan huruf kapital, seperti nama lembaga atau istilah hukum tertentu.  
  4. Tidak menambahkan kata-kata baru atau mengubah makna asli, hanya melakukan perbaikan pada tata bahasa, susunan, dan format agar lebih rapi dan mudah dibaca. 
  5. Pastikan bagian kepala peraturan, termasuk judul, frasa keagamaan, dan pejabat yang menetapkan, tetap ada dan ditulis dengan format yang sesuai.
  6. Pastikan semua daftar berformat poin atau numerik (seperti a., b., c. dalam bagian Menimbang) tetap ada dan tersusun dengan benar (jika terdapat kalimat atau baris yang diawali oleh kata 'bahwa' maka tambahkan indeks poin atau numerik)
  7. tidak perlu awalan seperti: "berikut adalah hasil teks"
{legal_paragraph}
'''