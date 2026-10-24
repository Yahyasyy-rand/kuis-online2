"""Satu-satunya modul yang tahu bahwa data disimpan di file JSON."""
import json

from config import DATA_FILE


def _muat():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def _simpan(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ambil_semua_kuis():
    return _muat()["kuis"]


def ambil_kuis(id_kuis):
    """Kembalikan kuis dengan id tersebut, atau None."""
    return next((k for k in _muat()["kuis"] if k["id"] == id_kuis), None)


def ambil_hasil_kuis(id_kuis):
    return [h for h in _muat()["hasil"] if h["kuis"] == id_kuis]


def hitung_semua_hasil():
    return len(_muat()["hasil"])


def tambah_hasil(hasil):
    data = _muat()
    data["hasil"].append(hasil)
    _simpan(data)
