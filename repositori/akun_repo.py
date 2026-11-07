"""Penyimpanan akun di akun.json (file terpisah dari data.json). Satu-satunya modul yang tahu format file akun."""
import json
import os

from config import DATA_FILE

# letaknya sefolder dengan data.json milik aplikasi, supaya data.json tidak tersentuh
AKUN_FILE = os.path.join(os.path.dirname(DATA_FILE), "akun.json")


def _muat():
    if not os.path.exists(AKUN_FILE):
        return {"akun": {}}
    with open(AKUN_FILE, encoding="utf-8") as f:
        return json.load(f)


def _simpan(data):
    with open(AKUN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ambil_akun(nim):
    """Kembalikan akun milik NIM tersebut, atau None."""
    return _muat()["akun"].get(nim)


def tambah_akun(nim, akun):
    data = _muat()
    data["akun"][nim] = akun
    _simpan(data)
