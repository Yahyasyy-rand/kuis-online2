"""Galat aturan bisnis. Tidak tahu HTTP: pemetaan ke status ada di rute/."""


class GalatBisnis(Exception):
    def __init__(self, pesan):
        super().__init__(pesan)
        self.pesan = pesan


class KuisTidakDitemukan(GalatBisnis):
    def __init__(self):
        super().__init__("Kuis tidak ditemukan")


class NimTidakValid(GalatBisnis):
    def __init__(self, panjang_nim):
        super().__init__("NIM harus " + str(panjang_nim) + " digit angka")


class BatasPercobaanHabis(GalatBisnis):
    def __init__(self, maks_percobaan):
        super().__init__("Batas percobaan (" + str(maks_percobaan) + "x) sudah habis")
