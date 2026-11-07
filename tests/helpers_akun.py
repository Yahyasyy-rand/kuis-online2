"""Bantuan test fitur login: menambah akun.json sementara di atas database kuis sementara (helpers.py tidak diubah)."""
import os
import tempfile
from unittest.mock import patch

from repositori import akun_repo
from tests.helpers import DatabaseSementaraTestCase


class AkunDatabaseTestCase(DatabaseSementaraTestCase):
    """data.json DAN akun.json dialihkan ke file sementara; akun.json awalnya belum ada."""

    def setUp(self):
        super().setUp()
        self.path_akun = os.path.join(tempfile.mkdtemp(), "akun.json")
        patcher = patch.object(akun_repo, "AKUN_FILE", self.path_akun)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: os.path.exists(self.path_akun) and os.remove(self.path_akun))
