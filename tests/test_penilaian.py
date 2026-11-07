"""UNIT TEST layanan/penilaian.py (aturan 4-7), tanpa file JSON dan tanpa Flask."""
import unittest

from layanan.penilaian import (
    hitung_poin, hitung_skor, jawaban_benar, koreksi_isian,
    koreksi_pilihan_ganda, nilai_kuis, tentukan_huruf, tentukan_lulus,
)

SOAL_PG = {"no": 1, "tipe": "pg", "kunci": "B", "bobot": 10}
SOAL_ISIAN = {"no": 2, "tipe": "isian", "kunci": ["print", "print()"], "bobot": 20}
KUIS = {"nilai_lulus": 50, "soal": [SOAL_PG, SOAL_ISIAN]}


class TestKoreksiPilihanGanda(unittest.TestCase):
    def test_jawaban_benar(self):
        self.assertTrue(koreksi_pilihan_ganda("B", "B"))

    def test_tidak_peka_huruf_besar_kecil_dan_spasi(self):
        self.assertTrue(koreksi_pilihan_ganda(" b ", "B"))

    def test_jawaban_salah(self):
        self.assertFalse(koreksi_pilihan_ganda("A", "B"))

    def test_jawaban_kosong_salah(self):
        self.assertFalse(koreksi_pilihan_ganda("", "B"))


class TestKoreksiIsian(unittest.TestCase):
    def test_jawaban_benar(self):
        self.assertTrue(koreksi_isian("print", ["print", "print()"]))

    def test_spasi_tepi_dan_huruf_besar_diabaikan(self):
        self.assertTrue(koreksi_isian("  PRINT()  ", ["print", "print()"]))

    def test_boleh_lebih_dari_satu_kunci(self):
        self.assertTrue(koreksi_isian("print()", ["print", "print()"]))

    def test_jawaban_salah(self):
        self.assertFalse(koreksi_isian("echo", ["print", "print()"]))

    def test_jawaban_kosong_salah(self):
        self.assertFalse(koreksi_isian("", ["print"]))


class TestJawabanBenar(unittest.TestCase):
    def test_soal_pg_dikoreksi_sebagai_pilihan_ganda(self):
        self.assertTrue(jawaban_benar(SOAL_PG, {"1": "b"}))

    def test_soal_isian_dikoreksi_sebagai_isian(self):
        self.assertTrue(jawaban_benar(SOAL_ISIAN, {"2": "Print"}))

    def test_soal_tidak_dijawab_dianggap_salah(self):
        self.assertFalse(jawaban_benar(SOAL_PG, {}))

    def test_kunci_jawaban_dicari_berdasarkan_nomor_soal(self):
        # jawaban untuk soal nomor lain tidak boleh terpakai
        self.assertFalse(jawaban_benar(SOAL_PG, {"2": "B"}))


class TestHitungPoin(unittest.TestCase):
    def test_semua_benar(self):
        self.assertEqual(hitung_poin(KUIS, {"1": "B", "2": "print"}), (30, 30, 2))

    def test_sebagian_benar_memakai_bobot(self):
        self.assertEqual(hitung_poin(KUIS, {"1": "A", "2": "print"}), (20, 30, 1))

    def test_semua_kosong(self):
        self.assertEqual(hitung_poin(KUIS, {}), (0, 30, 0))


class TestHitungSkor(unittest.TestCase):
    def test_skor_penuh(self):
        self.assertEqual(hitung_skor(30, 30), 100.0)

    def test_skor_nol(self):
        self.assertEqual(hitung_skor(0, 30), 0.0)

    def test_dibulatkan_satu_desimal(self):
        self.assertEqual(hitung_skor(1, 3), 33.3)


class TestTentukanHuruf(unittest.TestCase):
    def test_batas_atas_dan_bawah_tiap_huruf(self):
        kasus = [
            (100, "A"), (85, "A"), (84.9, "B"),
            (70, "B"), (69.9, "C"),
            (55, "C"), (54.9, "D"),
            (40, "D"), (39.9, "E"), (0, "E"),
        ]
        for skor, harapan in kasus:
            with self.subTest(skor=skor):
                self.assertEqual(tentukan_huruf(skor), harapan)


class TestTentukanLulus(unittest.TestCase):
    def test_tepat_di_batas_lulus(self):
        self.assertTrue(tentukan_lulus(70, 70))

    def test_di_bawah_batas_tidak_lulus(self):
        self.assertFalse(tentukan_lulus(69.9, 70))


class TestNilaiKuis(unittest.TestCase):
    def test_semua_benar(self):
        hasil = nilai_kuis(KUIS, {"1": "B", "2": "print"})
        self.assertEqual(hasil, {"skor": 100.0, "huruf": "A", "lulus": True, "benar": 2, "total_soal": 2})

    def test_semua_salah(self):
        hasil = nilai_kuis(KUIS, {})
        self.assertEqual(hasil, {"skor": 0.0, "huruf": "E", "lulus": False, "benar": 0, "total_soal": 2})

    def test_sebagian_benar_tidak_lulus(self):
        # hanya soal bobot 10 dari 30 -> 33.3, di bawah nilai_lulus 50
        hasil = nilai_kuis(KUIS, {"1": "B"})
        self.assertEqual(hasil["skor"], 33.3)
        self.assertEqual(hasil["huruf"], "E")
        self.assertFalse(hasil["lulus"])


if __name__ == "__main__":
    unittest.main()
