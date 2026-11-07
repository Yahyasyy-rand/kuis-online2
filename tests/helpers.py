"""Bantuan bersama untuk test: database JSON sementara (data asli tidak disentuh)."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from repositori import json_repo

DATA_UJI = {
    "kuis": [
        {
            "id": "T01", "judul": "Kuis Uji", "nilai_lulus": 50, "maks_percobaan": 2,
            "soal": [
                {"no": 1, "tipe": "pg", "pertanyaan": "1+1?", "pilihan": ["A. 1", "B. 2"], "kunci": "B", "bobot": 50},
                {"no": 2, "tipe": "isian", "pertanyaan": "Ibu kota Indonesia?", "kunci": ["jakarta", "dki jakarta"], "bobot": 50},
            ],
        },
        {
            "id": "T02", "judul": "Kuis Sekali Coba", "nilai_lulus": 60, "maks_percobaan": 1,
            "soal": [
                {"no": 1, "tipe": "pg", "pertanyaan": "2+2?", "pilihan": ["A. 4", "B. 5"], "kunci": "A", "bobot": 10},
            ],
        },
    ],
    "hasil": [],
}


class DatabaseSementaraTestCase(unittest.TestCase):
    """Tiap test mulai dengan database kosong; DATA_FILE dialihkan ke file sementara."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(DATA_UJI, f)
        patcher = patch.object(json_repo, "DATA_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(os.remove, self.path)
