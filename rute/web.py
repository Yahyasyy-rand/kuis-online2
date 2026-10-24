from flask import Blueprint, jsonify, render_template, request

from config import JUMLAH_PERINGKAT
from layanan.galat import GalatBisnis
from layanan.kuis import ambil_kuis, daftar_kuis
from layanan.laporan import peringkat_kuis, statistik_kuis
from layanan.pengerjaan import kirim_jawaban
from rute import respons_galat

web = Blueprint("web", __name__)


def _baca_input_jawaban():
    """Form web atau JSON -> (nim, {no_soal: jawaban})."""
    if request.is_json:
        isi = request.get_json()
        nim = str(isi.get("nim", ""))
        jawaban = {str(k): str(v) for k, v in isi.get("jawaban", {}).items()}
    else:
        nim = request.form.get("nim", "")
        jawaban = {k: v for k, v in request.form.items() if k != "nim"}
    return nim, jawaban


@web.route("/")
def index():
    return render_template("index.html", kuis=daftar_kuis())


@web.route("/kuis/<id_kuis>")
def kerjakan(id_kuis):
    try:
        kuis = ambil_kuis(id_kuis)
    except GalatBisnis as galat:
        return respons_galat(galat, False)
    return render_template("kerjakan.html", kuis=kuis, id_kuis=id_kuis)


@web.route("/kuis/<id_kuis>/jawab", methods=["POST"])
def jawab(id_kuis):
    # dipakai oleh form web DAN oleh API (request JSON)
    nim, jawaban = _baca_input_jawaban()
    try:
        hasil = kirim_jawaban(id_kuis, nim, jawaban)
    except GalatBisnis as galat:
        return respons_galat(galat, request.is_json)
    if request.is_json:
        return jsonify(hasil), 201
    return render_template("hasil.html", **hasil)


@web.route("/kuis/<id_kuis>/statistik")
def statistik_web(id_kuis):
    return render_template("statistik.html", id_kuis=id_kuis, statistik=statistik_kuis(id_kuis),
                           peringkat=peringkat_kuis(id_kuis), jumlah_peringkat=JUMLAH_PERINGKAT)
