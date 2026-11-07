"""UNIT TEST fungsi kecil di layanan/pengerjaan.py (aturan 2 dan 3), tanpa file JSON."""
import unittest

from layanan.pengerjaan import (
    boleh_mencoba, buat_id_hasil, hitung_percobaan_ke, nim_valid, susun_hasil,
)


class TestNimValid(unittest.TestCase):
    def test_nim_10_digit_diterima(self):
        self.assertTrue(nim_valid("2310100004"))

    def test_nim_ditolak(self):
        kasus = {
            "terlalu pendek (9 digit)": "231010000",
            "terlalu panjang (11 digit)": "23101000041",
            "berisi huruf": "231010000a",
            "semua huruf": "abcdefghij",
            "kosong": "",
            "ada spasi": "2310 10004",
        }
        for ket, nim in kasus.items():
            with self.subTest(ket):
                self.assertFalse(nim_valid(nim))


class TestHitungPercobaanKe(unittest.TestCase):
    HASIL = [{"nim": "2310100001"}, {"nim": "2310100002"}, {"nim": "2310100001"}]

    def test_nim_belum_pernah_mencoba_adalah_percobaan_pertama(self):
        self.assertEqual(hitung_percobaan_ke(self.HASIL, "2310100099"), 1)

    def test_hanya_menghitung_milik_nim_yang_sama(self):
        self.assertEqual(hitung_percobaan_ke(self.HASIL, "2310100001"), 3)
        self.assertEqual(hitung_percobaan_ke(self.HASIL, "2310100002"), 2)

    def test_daftar_kosong(self):
        self.assertEqual(hitung_percobaan_ke([], "2310100001"), 1)


class TestBolehMencoba(unittest.TestCase):
    def test_masih_dalam_batas(self):
        self.assertTrue(boleh_mencoba(1, 2))

    def test_tepat_di_batas_masih_boleh(self):
        self.assertTrue(boleh_mencoba(2, 2))

    def test_melebihi_batas_ditolak(self):
        self.assertFalse(boleh_mencoba(3, 2))


class TestBuatIdHasil(unittest.TestCase):
    def test_id_pertama(self):
        self.assertEqual(buat_id_hasil(0), "H001")

    def test_id_berurutan(self):
        self.assertEqual(buat_id_hasil(4), "H005")

    def test_lebih_dari_tiga_digit(self):
        self.assertEqual(buat_id_hasil(99), "H100")


class TestSusunHasil(unittest.TestCase):
    def test_semua_field_terisi_dari_argumen(self):
        nilai = {"skor": 70.0, "huruf": "B", "lulus": True}
        hasil = susun_hasil("H001", "K01", "2310100004", {"1": "B"}, nilai, 1, "2026-11-07T10:00:00")
        self.assertEqual(hasil, {
            "id": "H001", "kuis": "K01", "nim": "2310100004", "jawaban": {"1": "B"},
            "skor": 70.0, "huruf": "B", "lulus": True, "percobaan": 1, "waktu": "2026-11-07T10:00:00",
        })


if __name__ == "__main__":
    unittest.main()
