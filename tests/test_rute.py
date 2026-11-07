"""INTEGRATION TEST rute Flask -> layanan -> repositori -> file JSON (database sementara)."""
from app import create_app
from tests.helpers import DatabaseSementaraTestCase

JAWABAN_BENAR = {"nim": "2310100001", "jawaban": {"1": "B", "2": "Jakarta"}}


class TestRuteApi(DatabaseSementaraTestCase):
    def setUp(self):
        super().setUp()
        self.client = create_app().test_client()

    def test_daftar_kuis(self):
        res = self.client.get("/api/kuis")
        self.assertEqual(res.status_code, 200)
        self.assertEqual([k["id"] for k in res.get_json()], ["T01", "T02"])

    def test_soal_tanpa_kunci_jawaban(self):
        res = self.client.get("/api/kuis/T01")
        self.assertEqual(res.status_code, 200)
        for soal in res.get_json()["soal"]:
            self.assertNotIn("kunci", soal)

    def test_kuis_tidak_ditemukan_404(self):
        res = self.client.get("/api/kuis/XXX")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.get_json(), {"error": "Kuis tidak ditemukan"})

    def test_analisis_kuis_tidak_ditemukan_404(self):
        self.assertEqual(self.client.get("/api/kuis/XXX/analisis").status_code, 404)

    def test_statistik_kuis_tanpa_peserta(self):
        res = self.client.get("/api/kuis/T01/statistik")
        self.assertEqual(res.get_json(), {"peserta": 0})


class TestRuteJawab(DatabaseSementaraTestCase):
    def setUp(self):
        super().setUp()
        self.client = create_app().test_client()

    def test_jawab_json_sukses_201(self):
        res = self.client.post("/kuis/T01/jawab", json=JAWABAN_BENAR)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual((data["skor"], data["huruf"], data["lulus"]), (100.0, "A", True))

    def test_hasil_muncul_di_statistik_dan_peringkat(self):
        self.client.post("/kuis/T01/jawab", json=JAWABAN_BENAR)
        stat = self.client.get("/api/kuis/T01/statistik").get_json()
        self.assertEqual(stat["peserta"], 1)
        peringkat = self.client.get("/api/kuis/T01/peringkat").get_json()
        self.assertEqual(peringkat, [{"peringkat": 1, "nim": "2310****01", "skor": 100.0}])

    def test_nim_tidak_valid_400(self):
        res = self.client.post("/kuis/T01/jawab", json={"nim": "123", "jawaban": {}})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json(), {"error": "NIM harus 10 digit angka"})

    def test_kuis_tidak_ditemukan_404(self):
        res = self.client.post("/kuis/XXX/jawab", json=JAWABAN_BENAR)
        self.assertEqual(res.status_code, 404)

    def test_batas_percobaan_habis_403(self):
        body = {"nim": "2310100001", "jawaban": {"1": "A"}}
        self.assertEqual(self.client.post("/kuis/T02/jawab", json=body).status_code, 201)
        res = self.client.post("/kuis/T02/jawab", json=body)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json(), {"error": "Batas percobaan (1x) sudah habis"})

    def test_jawab_lewat_form_web_menampilkan_halaman_hasil(self):
        res = self.client.post("/kuis/T01/jawab", data={"nim": "2310100001", "1": "B", "2": "jakarta"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)

    def test_form_web_nim_tidak_valid_mengembalikan_teks_biasa(self):
        res = self.client.post("/kuis/T01/jawab", data={"nim": "abc"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_data(as_text=True), "NIM harus 10 digit angka")


class TestRuteWeb(DatabaseSementaraTestCase):
    def setUp(self):
        super().setUp()
        self.client = create_app().test_client()

    def test_halaman_daftar_kuis(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Kuis Uji", res.get_data(as_text=True))

    def test_halaman_kerjakan_kuis_ada(self):
        self.assertEqual(self.client.get("/kuis/T01").status_code, 200)

    def test_halaman_kerjakan_kuis_tidak_ada_404(self):
        self.assertEqual(self.client.get("/kuis/XXX").status_code, 404)

    def test_halaman_statistik(self):
        self.assertEqual(self.client.get("/kuis/T01/statistik").status_code, 200)
