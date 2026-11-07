"""UNIT TEST validasi akun + INTEGRATION TEST layanan/akun.py dengan repositori/akun_repo.py dan json_repo."""
import json
import unittest

from layanan.akun import daftar_akun, masuk, nama_valid, password_valid, riwayat_nim
from layanan.galat import NimTidakValid
from layanan.galat_akun import LoginGagal, NamaTidakValid, NimSudahTerdaftar, PasswordTidakValid
from layanan.pengerjaan import kirim_jawaban
from tests.helpers_akun import AkunDatabaseTestCase

NIM = "2310100001"


class TestNamaValid(unittest.TestCase):
    def test_nama_diterima(self):
        self.assertTrue(nama_valid("Yahya"))

    def test_spasi_tepi_tidak_dihitung(self):
        self.assertFalse(nama_valid("  ab  "))

    def test_nama_ditolak(self):
        kasus = {"terlalu pendek": "ab", "terlalu panjang": "a" * 51, "kosong": "", "bukan string": 123}
        for ket, nama in kasus.items():
            with self.subTest(ket):
                self.assertFalse(nama_valid(nama))


class TestPasswordValid(unittest.TestCase):
    def test_enam_karakter_diterima(self):
        self.assertTrue(password_valid("123456"))

    def test_password_ditolak(self):
        for ket, pw in {"lima karakter": "12345", "kosong": "", "bukan string": 123456}.items():
            with self.subTest(ket):
                self.assertFalse(password_valid(pw))


class TestDaftarAkun(AkunDatabaseTestCase):
    def test_sukses_akun_tersimpan(self):
        self.assertEqual(daftar_akun(NIM, "Yahya", "rahasia1"), {"nim": NIM, "nama": "Yahya"})
        with open(self.path_akun, encoding="utf-8") as f:
            self.assertIn(NIM, json.load(f)["akun"])

    def test_password_disimpan_sebagai_hash_bukan_teks_asli(self):
        daftar_akun(NIM, "Yahya", "rahasia1")
        with open(self.path_akun, encoding="utf-8") as f:
            tersimpan = f.read()
        self.assertNotIn("rahasia1", tersimpan)
        self.assertIn("password_hash", tersimpan)

    def test_gagal_nim_tidak_valid(self):
        with self.assertRaises(NimTidakValid) as ctx:
            daftar_akun("123", "Yahya", "rahasia1")
        self.assertEqual(ctx.exception.pesan, "NIM harus 10 digit angka")

    def test_gagal_nama_tidak_valid(self):
        with self.assertRaises(NamaTidakValid):
            daftar_akun(NIM, "ab", "rahasia1")

    def test_gagal_password_terlalu_pendek(self):
        with self.assertRaises(PasswordTidakValid) as ctx:
            daftar_akun(NIM, "Yahya", "123")
        self.assertEqual(ctx.exception.pesan, "Password minimal 6 karakter")

    def test_gagal_nim_sudah_terdaftar(self):
        daftar_akun(NIM, "Yahya", "rahasia1")
        with self.assertRaises(NimSudahTerdaftar) as ctx:
            daftar_akun(NIM, "Orang Lain", "password2")
        self.assertEqual(ctx.exception.pesan, "NIM sudah terdaftar")

    def test_gagal_tidak_ada_akun_yang_tersimpan(self):
        with self.assertRaises(PasswordTidakValid):
            daftar_akun(NIM, "Yahya", "123")
        with self.assertRaises(LoginGagal):
            masuk(NIM, "123")


class TestMasuk(AkunDatabaseTestCase):
    def setUp(self):
        super().setUp()
        daftar_akun(NIM, "Yahya", "rahasia1")

    def test_login_sukses(self):
        self.assertEqual(masuk(NIM, "rahasia1"), {"nim": NIM, "nama": "Yahya"})

    def test_gagal_password_salah(self):
        with self.assertRaises(LoginGagal) as ctx:
            masuk(NIM, "salah123")
        self.assertEqual(ctx.exception.pesan, "NIM atau password salah")

    def test_gagal_nim_belum_terdaftar_pesannya_sama(self):
        with self.assertRaises(LoginGagal) as ctx:
            masuk("2310199999", "rahasia1")
        self.assertEqual(ctx.exception.pesan, "NIM atau password salah")

    def test_gagal_password_bukan_string(self):
        with self.assertRaises(LoginGagal):
            masuk(NIM, None)


class TestRiwayatTerhubungKeDataKuis(AkunDatabaseTestCase):
    def test_riwayat_diambil_dari_hasil_kuis_milik_nim_itu_saja(self):
        daftar_akun(NIM, "Yahya", "rahasia1")
        kirim_jawaban("T01", NIM, {"1": "B", "2": "jakarta"})
        kirim_jawaban("T02", NIM, {"1": "A"})
        kirim_jawaban("T01", "2310100002", {"1": "A"})   # milik orang lain
        riwayat = riwayat_nim(NIM)
        self.assertEqual([(r["kuis"], r["skor"]) for r in riwayat], [("T01", 100.0), ("T02", 100.0)])

    def test_riwayat_kosong_jika_belum_pernah_mengerjakan(self):
        self.assertEqual(riwayat_nim(NIM), [])


if __name__ == "__main__":
    unittest.main()
