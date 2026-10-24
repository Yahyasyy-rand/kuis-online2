import datetime

from config import NIM_AKHIR_TAMPIL, NIM_AWAL_TAMPIL, PENYAMAR_NIM


def samarkan_nim(nim):
    """2310100004 -> 2310****04"""
    return nim[:NIM_AWAL_TAMPIL] + PENYAMAR_NIM + nim[-NIM_AKHIR_TAMPIL:]


def waktu_sekarang():
    return datetime.datetime.now().isoformat(timespec="seconds")
