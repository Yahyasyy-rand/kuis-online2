"""Aturan 4-7: koreksi jawaban, skor berbobot, nilai huruf, kelulusan."""
from config import BATAS_NILAI_HURUF, DESIMAL, HURUF_TERENDAH, SKOR_MAKSIMUM


def koreksi_pilihan_ganda(jawaban, kunci):
    return jawaban.strip().upper() == kunci


def koreksi_isian(jawaban, daftar_kunci):
    return jawaban.strip().lower() in [k.lower() for k in daftar_kunci]


def jawaban_benar(soal, jawaban):
    """jawaban = dict {no_soal: teks}; soal kosong dianggap salah."""
    teks = jawaban.get(str(soal["no"]), "")
    if soal["tipe"] == "pg":
        return koreksi_pilihan_ganda(teks, soal["kunci"])
    return koreksi_isian(teks, soal["kunci"])


def hitung_poin(kuis, jawaban):
    """Kembalikan (poin, total_bobot, jumlah_benar)."""
    poin = 0
    total_bobot = 0
    benar = 0
    for s in kuis["soal"]:
        total_bobot += s["bobot"]
        if jawaban_benar(s, jawaban):
            poin += s["bobot"]
            benar += 1
    return poin, total_bobot, benar


def hitung_skor(poin, total_bobot):
    return round(poin / total_bobot * SKOR_MAKSIMUM, DESIMAL)


def tentukan_huruf(skor):
    for batas, huruf in BATAS_NILAI_HURUF:
        if skor >= batas:
            return huruf
    return HURUF_TERENDAH


def tentukan_lulus(skor, nilai_lulus):
    return skor >= nilai_lulus


def nilai_kuis(kuis, jawaban):
    poin, total_bobot, benar = hitung_poin(kuis, jawaban)
    skor = hitung_skor(poin, total_bobot)
    return {"skor": skor, "huruf": tentukan_huruf(skor), "lulus": tentukan_lulus(skor, kuis["nilai_lulus"]),
            "benar": benar, "total_soal": len(kuis["soal"])}
