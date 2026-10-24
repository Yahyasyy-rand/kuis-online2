from flask import Blueprint, jsonify

from layanan.galat import GalatBisnis
from layanan.kuis import daftar_ringkasan_kuis, kuis_tanpa_kunci
from layanan.laporan import analisis_butir, peringkat_kuis, statistik_kuis
from rute import respons_galat

api = Blueprint("api", __name__)


@api.route("/api/kuis")
def daftar():
    return jsonify(daftar_ringkasan_kuis())


@api.route("/api/kuis/<id_kuis>")
def soal(id_kuis):
    try:
        return jsonify(kuis_tanpa_kunci(id_kuis))
    except GalatBisnis as galat:
        return respons_galat(galat, True)


@api.route("/api/kuis/<id_kuis>/statistik")
def statistik(id_kuis):
    return jsonify(statistik_kuis(id_kuis))


@api.route("/api/kuis/<id_kuis>/analisis")
def analisis(id_kuis):
    try:
        return jsonify(analisis_butir(id_kuis))
    except GalatBisnis as galat:
        return respons_galat(galat, True)


@api.route("/api/kuis/<id_kuis>/peringkat")
def peringkat(id_kuis):
    return jsonify([{"peringkat": r["peringkat"], "nim": r["nim"], "skor": r["skor"]} for r in peringkat_kuis(id_kuis)])
