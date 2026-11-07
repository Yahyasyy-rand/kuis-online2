"""UNIT TEST fungsi murni di layanan/laporan.py (aturan 8, 9, 10), tanpa file JSON."""
import unittest

from layanan.laporan import (
    distribusi_huruf, hitung_statistik, nilai_terbaik_per_nim,
    persen_benar, susun_peringkat, tentukan_tingkat,
)


def hasil(nim, skor, huruf="A", lulus=True, jawaban=None):
    return {"nim": nim, "skor": skor, "huruf": huruf, "lulus": lulus, "jawaban": jawaban or {}}


class TestNilaiTerbaikPerNim(unittest.TestCase):
    def test_diambil_skor_tertinggi_per_nim(self):
        data = [hasil("1", 50), hasil("1", 80), hasil("2", 60)]
        terbaik = nilai_terbaik_per_nim(data)
        self.assertEqual(terbaik["1"]["skor"], 80)
        self.assertEqual(terbaik["2"]["skor"], 60)

    def test_percobaan_lebih_rendah_tidak_menimpa(self):
        data = [hasil("1", 80), hasil("1", 50)]
        self.assertEqual(nilai_terbaik_per_nim(data)["1"]["skor"], 80)

    def test_kosong(self):
        self.assertEqual(nilai_terbaik_per_nim([]), {})


class TestDistribusiHuruf(unittest.TestCase):
    def test_semua_huruf_ada_walau_nol(self):
        self.assertEqual(distribusi_huruf({}), {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0})

    def test_menghitung_per_huruf(self):
        terbaik = {"1": hasil("1", 90, "A"), "2": hasil("2", 88, "A"), "3": hasil("3", 30, "E")}
        self.assertEqual(distribusi_huruf(terbaik), {"A": 2, "B": 0, "C": 0, "D": 0, "E": 1})


class TestHitungStatistik(unittest.TestCase):
    def test_tanpa_peserta(self):
        self.assertEqual(hitung_statistik({}), {"peserta": 0})

    def test_statistik_lengkap(self):
        terbaik = {
            "1": hasil("1", 100, "A", True),
            "2": hasil("2", 70, "B", True),
            "3": hasil("3", 55, "C", False),
        }
        stat = hitung_statistik(terbaik)
        self.assertEqual(stat["peserta"], 3)
        self.assertEqual(stat["rata_rata"], 75.0)
        self.assertEqual(stat["tertinggi"], 100)
        self.assertEqual(stat["terendah"], 55)
        self.assertEqual(stat["persen_lulus"], 66.7)
        self.assertEqual(stat["distribusi"], {"A": 1, "B": 1, "C": 1, "D": 0, "E": 0})


class TestSusunPeringkat(unittest.TestCase):
    def test_urut_skor_tertinggi_dan_nim_disamarkan(self):
        terbaik = {"2310100001": hasil("2310100001", 70, "B"), "2310100002": hasil("2310100002", 90, "A")}
        hasil_p = susun_peringkat(terbaik)
        self.assertEqual(hasil_p[0], {"peringkat": 1, "nim": "2310****02", "skor": 90, "huruf": "A"})
        self.assertEqual(hasil_p[1]["peringkat"], 2)

    def test_skor_sama_diurutkan_berdasarkan_nim(self):
        terbaik = {"2310100009": hasil("2310100009", 80), "2310100001": hasil("2310100001", 80)}
        self.assertEqual(susun_peringkat(terbaik)[0]["nim"], "2310****01")

    def test_dibatasi_jumlah_peringkat(self):
        terbaik = {"23101000%02d" % i: hasil("23101000%02d" % i, 50 + i) for i in range(8)}
        self.assertEqual(len(susun_peringkat(terbaik)), 5)
        self.assertEqual(len(susun_peringkat(terbaik, jumlah=3)), 3)

    def test_kosong(self):
        self.assertEqual(susun_peringkat({}), [])


class TestPersenBenar(unittest.TestCase):
    SOAL = {"no": 1, "tipe": "pg", "kunci": "B", "bobot": 10}

    def test_belum_ada_hasil_adalah_nol(self):
        self.assertEqual(persen_benar(self.SOAL, []), 0)

    def test_dua_dari_tiga_benar(self):
        semua = [{"jawaban": {"1": "B"}}, {"jawaban": {"1": "b"}}, {"jawaban": {"1": "A"}}]
        self.assertEqual(persen_benar(self.SOAL, semua), 66.7)

    def test_soal_tidak_dijawab_dihitung_salah(self):
        self.assertEqual(persen_benar(self.SOAL, [{"jawaban": {}}]), 0.0)


class TestTentukanTingkat(unittest.TestCase):
    def test_batas_tiap_tingkat(self):
        kasus = [(100, "mudah"), (80, "mudah"), (79.9, "sedang"),
                 (40, "sedang"), (39.9, "sulit"), (0, "sulit")]
        for persen, harapan in kasus:
            with self.subTest(persen=persen):
                self.assertEqual(tentukan_tingkat(persen), harapan)


if __name__ == "__main__":
    unittest.main()
