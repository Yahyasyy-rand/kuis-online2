# Titik masuk BARU: aplikasi kuis yang sudah ada (app.py) + fitur daftar/login. app.py tidak diubah.
# Jalankan: python app_login.py
import os

from app import create_app
from rute.akun import akun


def buat_app_login():
    app = create_app()
    app.secret_key = os.environ.get("SECRET_KEY", "ganti-di-produksi")
    app.register_blueprint(akun)
    return app


app = buat_app_login()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
