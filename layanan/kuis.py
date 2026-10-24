"""Mengambil dan menyajikan data kuis (aturan 1: soal tanpa kunci jawaban)."""
from layanan.galat import KuisTidakDitemukan
from repositori import json_repo


def daftar_kuis():
    return json_repo.ambil_semua_kuis()


def ambil_kuis(id_kuis):
    kuis = json_repo.ambil_kuis(id_kuis)
    if kuis is None:
        raise KuisTidakDitemukan()
    return kuis


def ringkasan_kuis(kuis):
    return {"id": kuis["id"], "judul": kuis["judul"], "jumlah_soal": len(kuis["soal"]), "nilai_lulus": kuis["nilai_lulus"]}


def daftar_ringkasan_kuis():
    return [ringkasan_kuis(k) for k in daftar_kuis()]


def soal_tanpa_kunci(kuis):
    hasil = []
    for s in kuis["soal"]:
        salinan = dict(s)
        del salinan["kunci"]
        hasil.append(salinan)
    return hasil


def kuis_tanpa_kunci(id_kuis):
    kuis = ambil_kuis(id_kuis)
    return {"id": kuis["id"], "judul": kuis["judul"], "maks_percobaan": kuis["maks_percobaan"], "soal": soal_tanpa_kunci(kuis)}
