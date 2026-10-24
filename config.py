"""Lokasi data dan semua konstanta aturan bisnis Kuis Online."""
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# Aturan 2: NIM
PANJANG_NIM = 10

# Aturan 7: nilai huruf (urut dari batas tertinggi); di bawah batas terakhir = E
BATAS_NILAI_HURUF = [(85, "A"), (70, "B"), (55, "C"), (40, "D")]
HURUF_TERENDAH = "E"
DAFTAR_HURUF = ["A", "B", "C", "D", "E"]

# Aturan 6: skor 0-100 dengan 1 desimal
SKOR_MAKSIMUM = 100
DESIMAL = 1

# Aturan 9: analisis butir soal (% benar)
BATAS_MUDAH = 80
BATAS_SEDANG = 40

# Aturan 10: peringkat dan penyamaran NIM (2310****01)
JUMLAH_PERINGKAT = 5
NIM_AWAL_TAMPIL = 4
NIM_AKHIR_TAMPIL = 2
PENYAMAR_NIM = "****"
