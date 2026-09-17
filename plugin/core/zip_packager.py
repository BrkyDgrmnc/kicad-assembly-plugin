"""
KiCad 10 Dizgi ve Montaj Eklentisi - ZIP Paketleme Modülü
"""

import os
import zipfile
from typing import List

class ZipPackager:
    """
    Üretilen BOM, CPL ve üretim dosyalarını tek bir ZIP arşivi halinde paketler.
    """

    @classmethod
    def create_zip_package(cls, zip_output_path: str, files_to_zip: List[str]) -> str:
        """
        Verilen dosya yollarını ziple bağlayıp hedefe yazar.
        """
        os.makedirs(os.path.dirname(os.path.abspath(zip_output_path)), exist_ok=True)

        with zipfile.ZipFile(zip_output_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    arcname = os.path.basename(file_path)
                    zf.write(file_path, arcname=arcname)

        return zip_output_path
