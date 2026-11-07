"""Rute daftar/login/logout + mengerjakan kuis sebagai peserta yang sudah login (NIM diambil dari sesi)."""
from functools import wraps

from flask import Blueprint, jsonify, request, session

from layanan.akun import daftar_akun, masuk, riwayat_nim
from layanan.galat import GalatBisnis
from layanan.galat_akun import BelumLogin, LoginGagal, NamaTidakValid, NimSudahTerdaftar, PasswordTidakValid
from layanan.pengerjaan import kirim_jawaban
from rute import STATUS_GALAT  # pemetaan galat kuis yang sudah ada dipakai ulang

akun = Blueprint("akun", __name__)

STATUS_GALAT_AKUN = dict(STATUS_GALAT)
STATUS_GALAT_AKUN.update({NamaTidakValid: 400, PasswordTidakValid: 400, NimSudahTerdaftar: 409,
                          LoginGagal: 401, BelumLogin: 401})


def _respons_galat(galat):
    return jsonify({"error": galat.pesan}), STATUS_GALAT_AKUN.get(type(galat), 400)


def wajib_login(fungsi):
    @wraps(fungsi)
    def dibungkus(*args, **kwargs):
        if "nim" not in session:
            return _respons_galat(BelumLogin())
        return fungsi(*args, **kwargs)
    return dibungkus


def _isi_json():
    return request.get_json(silent=True) or {}


@akun.route("/akun/daftar", methods=["POST"])
def daftar():
    isi = _isi_json()
    try:
        hasil = daftar_akun(str(isi.get("nim", "")), isi.get("nama", ""), isi.get("password", ""))
    except GalatBisnis as galat:
        return _respons_galat(galat)
    return jsonify(hasil), 201


@akun.route("/akun/masuk", methods=["POST"])
def login():
    isi = _isi_json()
    try:
        hasil = masuk(str(isi.get("nim", "")), isi.get("password", ""))
    except GalatBisnis as galat:
        return _respons_galat(galat)
    session["nim"] = hasil["nim"]
    session["nama"] = hasil["nama"]
    return jsonify(hasil)


@akun.route("/akun/keluar", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"pesan": "Berhasil keluar"})


@akun.route("/akun/saya")
@wajib_login
def saya():
    return jsonify({"nim": session["nim"], "nama": session["nama"]})


@akun.route("/akun/riwayat")
@wajib_login
def riwayat():
    return jsonify(riwayat_nim(session["nim"]))


@akun.route("/akun/kuis/<id_kuis>/jawab", methods=["POST"])
@wajib_login
def jawab(id_kuis):
    jawaban = {str(k): str(v) for k, v in _isi_json().get("jawaban", {}).items()}
    try:
        hasil = kirim_jawaban(id_kuis, session["nim"], jawaban)  # fungsi lama, NIM dari akun yang login
    except GalatBisnis as galat:
        return _respons_galat(galat)
    return jsonify(hasil), 201
