"""Daftar dan login peserta. NIM yang dipakai login = NIM yang dicatat di hasil kuis (data.json),
sehingga akun otomatis tersambung ke riwayat dan statistik yang sudah ada."""
from werkzeug.security import check_password_hash, generate_password_hash

from config import PANJANG_NIM
from layanan.galat_akun import LoginGagal, NamaTidakValid, NimSudahTerdaftar, PasswordTidakValid
from layanan.galat import NimTidakValid
from layanan.pengerjaan import nim_valid
from repositori import akun_repo, json_repo

PASSWORD_MINIMAL = 6
NAMA_MINIMAL = 3
NAMA_MAKSIMAL = 50


def nama_valid(nama):
    return isinstance(nama, str) and NAMA_MINIMAL <= len(nama.strip()) <= NAMA_MAKSIMAL


def password_valid(password):
    return isinstance(password, str) and len(password) >= PASSWORD_MINIMAL


def daftar_akun(nim, nama, password):
    if not isinstance(nim, str) or not nim_valid(nim):   # memakai aturan 2 milik layanan/pengerjaan.py
        raise NimTidakValid(PANJANG_NIM)
    if not nama_valid(nama):
        raise NamaTidakValid()
    if not password_valid(password):
        raise PasswordTidakValid(PASSWORD_MINIMAL)
    if akun_repo.ambil_akun(nim) is not None:
        raise NimSudahTerdaftar()
    akun_repo.tambah_akun(nim, {"nama": nama.strip(), "password_hash": generate_password_hash(password)})
    return {"nim": nim, "nama": nama.strip()}


def masuk(nim, password):
    akun = akun_repo.ambil_akun(nim) if isinstance(nim, str) else None
    if akun is None or not isinstance(password, str) or not check_password_hash(akun["password_hash"], password):
        raise LoginGagal()
    return {"nim": nim, "nama": akun["nama"]}


def riwayat_nim(nim):
    """Semua hasil kuis milik NIM ini, dari data.json (lintas kuis)."""
    riwayat = []
    for kuis in json_repo.ambil_semua_kuis():
        for h in json_repo.ambil_hasil_kuis(kuis["id"]):
            if h["nim"] == nim:
                riwayat.append({"id": h["id"], "kuis": kuis["id"], "judul": kuis["judul"], "skor": h["skor"],
                                "huruf": h["huruf"], "lulus": h["lulus"], "percobaan": h["percobaan"]})
    return riwayat
