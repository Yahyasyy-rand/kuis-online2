"""INTEGRATION TEST alur login lewat Flask: daftar -> login -> kerjakan kuis -> riwayat/statistik.
Menghubungkan fitur baru (rute/akun, layanan/akun, akun_repo) dengan file lama (kirim_jawaban, json_repo, laporan)."""
from app_login import buat_app_login
from tests.helpers_akun import AkunDatabaseTestCase

NIM = "2310100001"
DATA_DAFTAR = {"nim": NIM, "nama": "Yahya", "password": "rahasia1"}
JAWABAN_BENAR = {"jawaban": {"1": "B", "2": "Jakarta"}}


class AlurLoginTestCase(AkunDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = buat_app_login().test_client()

    def daftar_dan_login(self, nim=NIM, nama="Yahya", password="rahasia1"):
        self.client.post("/akun/daftar", json={"nim": nim, "nama": nama, "password": password})
        return self.client.post("/akun/masuk", json={"nim": nim, "password": password})


class TestDaftarDanLogin(AlurLoginTestCase):
    def test_daftar_sukses_201(self):
        res = self.client.post("/akun/daftar", json=DATA_DAFTAR)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json(), {"nim": NIM, "nama": "Yahya"})

    def test_daftar_nim_tidak_valid_400(self):
        res = self.client.post("/akun/daftar", json={**DATA_DAFTAR, "nim": "123"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json(), {"error": "NIM harus 10 digit angka"})

    def test_daftar_nim_ganda_409(self):
        self.client.post("/akun/daftar", json=DATA_DAFTAR)
        res = self.client.post("/akun/daftar", json=DATA_DAFTAR)
        self.assertEqual(res.status_code, 409)

    def test_login_sukses(self):
        res = self.daftar_dan_login()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get("/akun/saya").get_json(), {"nim": NIM, "nama": "Yahya"})

    def test_login_password_salah_401(self):
        self.client.post("/akun/daftar", json=DATA_DAFTAR)
        res = self.client.post("/akun/masuk", json={"nim": NIM, "password": "salah123"})
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.get_json(), {"error": "NIM atau password salah"})
        self.assertEqual(self.client.get("/akun/saya").status_code, 401)

    def test_login_nim_belum_terdaftar_401(self):
        res = self.client.post("/akun/masuk", json={"nim": NIM, "password": "rahasia1"})
        self.assertEqual(res.status_code, 401)

    def test_logout_menghapus_sesi(self):
        self.daftar_dan_login()
        self.client.post("/akun/keluar")
        self.assertEqual(self.client.get("/akun/saya").status_code, 401)


class TestHarusLogin(AlurLoginTestCase):
    def test_riwayat_tanpa_login_401(self):
        res = self.client.get("/akun/riwayat")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.get_json(), {"error": "Silakan login terlebih dahulu"})

    def test_kerjakan_kuis_tanpa_login_401_dan_tidak_ada_hasil_tersimpan(self):
        res = self.client.post("/akun/kuis/T01/jawab", json=JAWABAN_BENAR)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(self.client.get("/api/kuis/T01/statistik").get_json(), {"peserta": 0})


class TestLoginTerhubungKeKuis(AlurLoginTestCase):
    def test_nim_hasil_kuis_diambil_dari_akun_yang_login(self):
        self.daftar_dan_login()
        res = self.client.post("/akun/kuis/T01/jawab", json=JAWABAN_BENAR)
        self.assertEqual(res.status_code, 201)
        self.assertEqual((res.get_json()["skor"], res.get_json()["huruf"]), (100.0, "A"))
        # terlihat oleh endpoint lama (tanpa login) dengan NIM yang sama, disamarkan
        peringkat = self.client.get("/api/kuis/T01/peringkat").get_json()
        self.assertEqual(peringkat, [{"peringkat": 1, "nim": "2310****01", "skor": 100.0}])

    def test_riwayat_menampilkan_hasil_sendiri(self):
        self.daftar_dan_login()
        self.client.post("/akun/kuis/T01/jawab", json=JAWABAN_BENAR)
        riwayat = self.client.get("/akun/riwayat").get_json()
        self.assertEqual(len(riwayat), 1)
        self.assertEqual((riwayat[0]["kuis"], riwayat[0]["judul"], riwayat[0]["skor"]),
                         ("T01", "Kuis Uji", 100.0))

    def test_riwayat_tidak_memuat_hasil_milik_orang_lain(self):
        self.daftar_dan_login(nim="2310100002", nama="Budi")
        self.client.post("/akun/kuis/T01/jawab", json=JAWABAN_BENAR)
        self.client.post("/akun/keluar")
        self.daftar_dan_login()  # login sebagai NIM berbeda
        self.assertEqual(self.client.get("/akun/riwayat").get_json(), [])

    def test_batas_percobaan_lama_tetap_berlaku_403(self):
        self.daftar_dan_login()
        body = {"jawaban": {"1": "A"}}
        self.assertEqual(self.client.post("/akun/kuis/T02/jawab", json=body).status_code, 201)
        res = self.client.post("/akun/kuis/T02/jawab", json=body)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json(), {"error": "Batas percobaan (1x) sudah habis"})

    def test_kuis_tidak_ditemukan_404(self):
        self.daftar_dan_login()
        res = self.client.post("/akun/kuis/XXX/jawab", json=JAWABAN_BENAR)
        self.assertEqual(res.status_code, 404)

    def test_endpoint_lama_tetap_berfungsi_di_app_login(self):
        self.assertEqual(self.client.get("/api/kuis").status_code, 200)
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_data_json_dan_akun_json_asli_tidak_tersentuh(self):
        import os
        import config
        self.daftar_dan_login()
        self.client.post("/akun/kuis/T01/jawab", json=JAWABAN_BENAR)
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(config.DATA_FILE), "akun.json")))
