"""INTEGRATION TEST layanan/* + repositori/json_repo.py + file JSON (database sementara)."""
import hashlib
import io
import unittest

import config
from layanan.galat import BatasPercobaanHabis, KuisTidakDitemukan, NimTidakValid
from layanan.kuis import ambil_kuis, daftar_ringkasan_kuis, kuis_tanpa_kunci
from layanan.laporan import analisis_butir, peringkat_kuis, statistik_kuis
from layanan.pengerjaan import kirim_jawaban
from repositori import json_repo
from tests.helpers import DatabaseSementaraTestCase

NIM_A = "2310100001"
NIM_B = "2310100002"
JAWABAN_BENAR = {"1": "B", "2": "Jakarta"}
JAWABAN_SEPARUH = {"1": "B", "2": "bandung"}
JAWABAN_SALAH = {"1": "A", "2": "bandung"}


class TestKirimJawaban(DatabaseSementaraTestCase):
    def test_sukses_hasil_tersimpan_ke_file(self):
        hasil = kirim_jawaban("T01", NIM_A, JAWABAN_BENAR)
        self.assertEqual(hasil, {"id": "H001", "skor": 100.0, "huruf": "A", "lulus": True,
                                 "benar": 2, "total_soal": 2, "percobaan": 1})
        tersimpan = json_repo.ambil_hasil_kuis("T01")
        self.assertEqual(len(tersimpan), 1)
        self.assertEqual(tersimpan[0]["nim"], NIM_A)

    def test_id_hasil_bertambah_berurutan_lintas_kuis(self):
        self.assertEqual(kirim_jawaban("T01", NIM_A, JAWABAN_BENAR)["id"], "H001")
        self.assertEqual(kirim_jawaban("T02", NIM_A, {"1": "A"})["id"], "H002")
        self.assertEqual(json_repo.hitung_semua_hasil(), 2)

    def test_percobaan_kedua_tercatat(self):
        kirim_jawaban("T01", NIM_A, JAWABAN_SALAH)
        hasil = kirim_jawaban("T01", NIM_A, JAWABAN_BENAR)
        self.assertEqual(hasil["percobaan"], 2)

    def test_gagal_kuis_tidak_ditemukan(self):
        with self.assertRaises(KuisTidakDitemukan) as ctx:
            kirim_jawaban("XXX", NIM_A, JAWABAN_BENAR)
        self.assertEqual(ctx.exception.pesan, "Kuis tidak ditemukan")

    def test_gagal_nim_tidak_valid_dan_tidak_ada_yang_tersimpan(self):
        with self.assertRaises(NimTidakValid) as ctx:
            kirim_jawaban("T01", "123", JAWABAN_BENAR)
        self.assertEqual(ctx.exception.pesan, "NIM harus 10 digit angka")
        self.assertEqual(json_repo.hitung_semua_hasil(), 0)

    def test_gagal_batas_percobaan_habis(self):
        kirim_jawaban("T02", NIM_A, {"1": "A"})  # maks_percobaan T02 = 1
        with self.assertRaises(BatasPercobaanHabis) as ctx:
            kirim_jawaban("T02", NIM_A, {"1": "A"})
        self.assertEqual(ctx.exception.pesan, "Batas percobaan (1x) sudah habis")
        self.assertEqual(json_repo.hitung_semua_hasil(), 1)

    def test_batas_percobaan_berlaku_per_nim(self):
        kirim_jawaban("T02", NIM_A, {"1": "A"})
        hasil = kirim_jawaban("T02", NIM_B, {"1": "A"})  # NIM lain tetap boleh
        self.assertEqual(hasil["percobaan"], 1)


class TestDataKuis(DatabaseSementaraTestCase):
    def test_daftar_ringkasan(self):
        ringkasan = daftar_ringkasan_kuis()
        self.assertEqual(ringkasan[0], {"id": "T01", "judul": "Kuis Uji", "jumlah_soal": 2, "nilai_lulus": 50})
        self.assertEqual(len(ringkasan), 2)

    def test_soal_dikirim_tanpa_kunci_jawaban(self):
        kuis = kuis_tanpa_kunci("T01")
        self.assertEqual(kuis["maks_percobaan"], 2)
        for soal in kuis["soal"]:
            self.assertNotIn("kunci", soal)

    def test_menyajikan_soal_tanpa_kunci_tidak_menghapus_kunci_di_data(self):
        kuis_tanpa_kunci("T01")
        self.assertIn("kunci", ambil_kuis("T01")["soal"][0])

    def test_kuis_tidak_ditemukan(self):
        with self.assertRaises(KuisTidakDitemukan):
            kuis_tanpa_kunci("XXX")


class TestLaporan(DatabaseSementaraTestCase):
    def setUp(self):
        super().setUp()
        kirim_jawaban("T01", NIM_A, JAWABAN_SALAH)    # 0
        kirim_jawaban("T01", NIM_A, JAWABAN_BENAR)    # 100 (terbaik NIM_A)
        kirim_jawaban("T01", NIM_B, JAWABAN_SEPARUH)  # 50 -> lulus (batas 50), huruf D

    def test_statistik_memakai_nilai_terbaik_per_nim(self):
        stat = statistik_kuis("T01")
        self.assertEqual(stat["peserta"], 2)  # 3 percobaan, tapi 2 NIM
        self.assertEqual(stat["rata_rata"], 75.0)
        self.assertEqual(stat["tertinggi"], 100.0)
        self.assertEqual(stat["terendah"], 50.0)
        self.assertEqual(stat["persen_lulus"], 100.0)
        self.assertEqual(stat["distribusi"], {"A": 1, "B": 0, "C": 0, "D": 1, "E": 0})

    def test_statistik_kuis_tanpa_hasil(self):
        self.assertEqual(statistik_kuis("T02"), {"peserta": 0})

    def test_peringkat_urut_dan_nim_disamarkan(self):
        peringkat = peringkat_kuis("T01")
        self.assertEqual([p["nim"] for p in peringkat], ["2310****01", "2310****02"])
        self.assertEqual([p["peringkat"] for p in peringkat], [1, 2])

    def test_analisis_butir(self):
        # soal 1: benar di 2 dari 3 percobaan (66.7 sedang); soal 2: benar di 1 dari 3 (33.3 sulit)
        self.assertEqual(analisis_butir("T01"), [
            {"no": 1, "persen_benar": 66.7, "tingkat": "sedang"},
            {"no": 2, "persen_benar": 33.3, "tingkat": "sulit"},
        ])

    def test_analisis_butir_kuis_tidak_ditemukan(self):
        with self.assertRaises(KuisTidakDitemukan):
            analisis_butir("XXX")


class TestDataAsliTidakTersentuh(unittest.TestCase):
    """Bukti @patch/DATA_FILE sementara bekerja: data.json asli tidak berubah oleh test."""

    @staticmethod
    def _sidik_jari():
        with open(config.DATA_FILE, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def test_data_json_asli_utuh_setelah_transaksi(self):
        sebelum = self._sidik_jari()

        class _Uji(DatabaseSementaraTestCase):
            def runTest(self):
                kirim_jawaban("T01", NIM_A, JAWABAN_BENAR)

        hasil = unittest.TextTestRunner(stream=io.StringIO()).run(_Uji())
        self.assertTrue(hasil.wasSuccessful())
        self.assertEqual(self._sidik_jari(), sebelum)


if __name__ == "__main__":
    unittest.main()
