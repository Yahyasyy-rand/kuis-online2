"""UNIT TEST utils/format.py"""
import datetime
import unittest

from utils.format import samarkan_nim, waktu_sekarang


class TestSamarkanNim(unittest.TestCase):
    def test_nim_disamarkan_tengahnya(self):
        self.assertEqual(samarkan_nim("2310100004"), "2310****04")

    def test_contoh_pada_aturan_10(self):
        self.assertEqual(samarkan_nim("2310100001"), "2310****01")

    def test_panjang_hasil_tetap_sama_dengan_nim_normal(self):
        self.assertEqual(len(samarkan_nim("2310100004")), 10)


class TestWaktuSekarang(unittest.TestCase):
    def test_format_iso_tanpa_pecahan_detik(self):
        waktu = waktu_sekarang()
        self.assertEqual(len(waktu), 19)  # YYYY-MM-DDTHH:MM:SS
        datetime.datetime.fromisoformat(waktu)  # error jika formatnya salah


if __name__ == "__main__":
    unittest.main()
