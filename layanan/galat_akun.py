"""Galat aturan bisnis akun. Turunan GalatBisnis, jadi bisa ditangkap dengan cara yang sama seperti galat kuis."""
from layanan.galat import GalatBisnis


class NamaTidakValid(GalatBisnis):
    def __init__(self):
        super().__init__("Nama harus 3-50 karakter")


class PasswordTidakValid(GalatBisnis):
    def __init__(self, panjang_minimal):
        super().__init__("Password minimal " + str(panjang_minimal) + " karakter")


class NimSudahTerdaftar(GalatBisnis):
    def __init__(self):
        super().__init__("NIM sudah terdaftar")


class LoginGagal(GalatBisnis):
    """Pesan sengaja sama untuk NIM tak terdaftar dan password salah (tidak membocorkan NIM mana yang ada)."""
    def __init__(self):
        super().__init__("NIM atau password salah")


class BelumLogin(GalatBisnis):
    def __init__(self):
        super().__init__("Silakan login terlebih dahulu")
