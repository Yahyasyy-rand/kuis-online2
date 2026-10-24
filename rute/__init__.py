"""Pemetaan galat bisnis (layanan/) ke respons HTTP, dipakai web.py dan api.py."""
from flask import jsonify

from layanan.galat import BatasPercobaanHabis, KuisTidakDitemukan, NimTidakValid

STATUS_GALAT = {KuisTidakDitemukan: 404, NimTidakValid: 400, BatasPercobaanHabis: 403}


def respons_galat(galat, sebagai_json):
    status = STATUS_GALAT.get(type(galat), 400)
    if sebagai_json:
        return jsonify({"error": galat.pesan}), status
    return galat.pesan, status
