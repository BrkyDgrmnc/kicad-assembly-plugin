"""
KiCad 10 Dizgi ve Montaj Eklentisi - Bağımsız Test Betiği
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin.config import CUSTOM_USER_VENDOR_PRESET
from plugin.core.preset_manager import PresetManager
from plugin.core.board_parser import BoardParser
from plugin.core.exporter import AssemblyExporter
from plugin.core.zip_packager import ZipPackager

def run_tests():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    print("==================================================")
    print("[INFO] KiCad 10 Dizgi Eklentisi Dogrulama Testi Basliyor...")
    print("==================================================")

    # 1. Mock PCB Verilerini Al
    parser = BoardParser()
    components = parser.parse_board(None)
    proj_name, rev_name = "MyMainBoard", "RevA"
    prefix = f"{proj_name}_{rev_name}"

    print(f"[OK] {len(components)} adet mock bilesen yuklendi. Proje: {proj_name} ({rev_name})")

    # 2. Özel Profil
    saved_preset = PresetManager.save_new_preset(
        name="Ahmet Elektronik NeoDen YY1 Formati",
        description="Ahmet Elektronik icin ozel dizgi formati",
        columns=CUSTOM_USER_VENDOR_PRESET["columns"]
    )

    # 3. Çıktı Formatları (CSV, TXT, XLSX, JSON, ZIP)
    test_output_dir = os.path.join(os.path.dirname(__file__), "test_output")

    csv_path = os.path.join(test_output_dir, f"{prefix}_output.csv")
    txt_path = os.path.join(test_output_dir, f"{prefix}_output.txt")
    xlsx_path = os.path.join(test_output_dir, f"{prefix}_output.xlsx")
    json_path = os.path.join(test_output_dir, f"{prefix}_output.json")
    zip_path = os.path.join(test_output_dir, f"{prefix}_Assembly_Package.zip")

    AssemblyExporter.export_to_csv(csv_path, components, saved_preset)
    print(f"[OK] CSV Uretildi: {csv_path}")

    AssemblyExporter.export_to_tsv(txt_path, components, saved_preset)
    print(f"[OK] TXT (TSV) Uretildi: {txt_path}")

    AssemblyExporter.export_to_excel(xlsx_path, components, saved_preset)
    print(f"[OK] Excel Uretildi: {xlsx_path}")

    AssemblyExporter.export_to_json(json_path, components, saved_preset)
    print(f"[OK] JSON Uretildi: {json_path}")

    all_files = [csv_path, txt_path, xlsx_path, json_path]
    ZipPackager.create_zip_package(zip_path, all_files)
    print(f"[OK] Tum veri formatlarini iceren ZIP Paketi Oluşturuldu: {zip_path}")

    print("\n==================================================")
    print("[SUCCESS] Tum Veri Formatlari (CSV, TXT, XLSX, JSON, ZIP) Basariyla Gecti!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
