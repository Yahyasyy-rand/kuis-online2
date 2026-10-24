# Kuis Online (e-learning): titik masuk aplikasi. Semua logika ada di modul lain.
from flask import Flask

from rute.api import api
from rute.web import web


def create_app():
    app = Flask(__name__)
    app.register_blueprint(web)
    app.register_blueprint(api)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
