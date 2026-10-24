"""Aturan 2 dan 3 + alur mengirim jawaban (dipakai oleh form web DAN API)."""
import re

from config import PANJANG_NIM
from layanan.galat import BatasPercobaanHabis, NimTidakValid
from layanan.kuis import ambil_kuis
from layanan.penilaian import nilai_kuis
from repositori import json_repo
from utils.format import waktu_sekarang


def nim_valid(nim):
    return re.fullmatch(r"\d{%d}" % PANJANG_NIM, nim) is not None


def hitung_percobaan_ke(hasil_kuis, nim):
    """Percobaan ke-berapa untuk NIM ini (hasil_kuis = hasil milik satu kuis)."""
    return len([h for h in hasil_kuis if h["nim"] == nim]) + 1


def boleh_mencoba(percobaan, maks_percobaan):
    return percobaan <= maks_percobaan


def buat_id_hasil(jumlah_hasil):
    return "H" + str(jumlah_hasil + 1).zfill(3)


def susun_hasil(id_hasil, id_kuis, nim, jawaban, nilai, percobaan, waktu):
    return {"id": id_hasil, "kuis": id_kuis, "nim": nim, "jawaban": jawaban, "skor": nilai["skor"], "huruf": nilai["huruf"],
            "lulus": nilai["lulus"], "percobaan": percobaan, "waktu": waktu}


def kirim_jawaban(id_kuis, nim, jawaban):
    kuis = ambil_kuis(id_kuis)
    if not nim_valid(nim):
        raise NimTidakValid(PANJANG_NIM)
    percobaan = hitung_percobaan_ke(json_repo.ambil_hasil_kuis(id_kuis), nim)
    if not boleh_mencoba(percobaan, kuis["maks_percobaan"]):
        raise BatasPercobaanHabis(kuis["maks_percobaan"])
    nilai = nilai_kuis(kuis, jawaban)
    id_hasil = buat_id_hasil(json_repo.hitung_semua_hasil())
    json_repo.tambah_hasil(susun_hasil(id_hasil, id_kuis, nim, jawaban, nilai, percobaan, waktu_sekarang()))
    return {"id": id_hasil, "skor": nilai["skor"], "huruf": nilai["huruf"], "lulus": nilai["lulus"],
            "benar": nilai["benar"], "total_soal": nilai["total_soal"], "percobaan": percobaan}
