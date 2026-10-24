"""Aturan 8, 9, 10: statistik kelas, peringkat, dan analisis butir soal."""
from config import BATAS_MUDAH, BATAS_SEDANG, DAFTAR_HURUF, DESIMAL, JUMLAH_PERINGKAT
from layanan.kuis import ambil_kuis
from layanan.penilaian import jawaban_benar
from repositori import json_repo
from utils.format import samarkan_nim


def nilai_terbaik_per_nim(hasil_kuis):
    terbaik = {}
    for h in hasil_kuis:
        if h["nim"] not in terbaik or h["skor"] > terbaik[h["nim"]]["skor"]:
            terbaik[h["nim"]] = h
    return terbaik


def distribusi_huruf(terbaik):
    distribusi = {huruf: 0 for huruf in DAFTAR_HURUF}
    for h in terbaik.values():
        distribusi[h["huruf"]] += 1
    return distribusi


def hitung_statistik(terbaik):
    nilai = [h["skor"] for h in terbaik.values()]
    if not nilai:
        return {"peserta": 0}
    lulus = len([h for h in terbaik.values() if h["lulus"]])
    return {"peserta": len(nilai), "rata_rata": round(sum(nilai) / len(nilai), DESIMAL), "tertinggi": max(nilai), "terendah": min(nilai),
            "persen_lulus": round(lulus / len(nilai) * 100, DESIMAL), "distribusi": distribusi_huruf(terbaik)}


def susun_peringkat(terbaik, jumlah=JUMLAH_PERINGKAT):
    urut = sorted(terbaik.values(), key=lambda x: (-x["skor"], x["nim"]))[:jumlah]
    return [{"peringkat": i + 1, "nim": samarkan_nim(h["nim"]), "skor": h["skor"], "huruf": h["huruf"]} for i, h in enumerate(urut)]


def statistik_kuis(id_kuis):
    return hitung_statistik(nilai_terbaik_per_nim(json_repo.ambil_hasil_kuis(id_kuis)))


def peringkat_kuis(id_kuis):
    return susun_peringkat(nilai_terbaik_per_nim(json_repo.ambil_hasil_kuis(id_kuis)))


def persen_benar(soal, semua_hasil):
    if not semua_hasil:
        return 0
    benar = len([h for h in semua_hasil if jawaban_benar(soal, h["jawaban"])])
    return round(benar / len(semua_hasil) * 100, DESIMAL)


def tentukan_tingkat(persen):
    if persen >= BATAS_MUDAH:
        return "mudah"
    if persen >= BATAS_SEDANG:
        return "sedang"
    return "sulit"


def analisis_butir(id_kuis):
    kuis = ambil_kuis(id_kuis)
    semua = json_repo.ambil_hasil_kuis(id_kuis)
    hasil = []
    for s in kuis["soal"]:
        persen = persen_benar(s, semua)
        hasil.append({"no": s["no"], "persen_benar": persen, "tingkat": tentukan_tingkat(persen)})
    return hasil
