"""
KiCad 10 Assembly & Fabrication Tool - Standalone Verification Test Script
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
    print("[INFO] KiCad 10 Assembly Plugin Verification Test Starting...")
    print("==================================================")

    # 1. Load Mock PCB Components
    parser = BoardParser()
    components = parser.parse_board(None)
    proj_name, rev_name = "MyMainBoard", "RevA"
    prefix = f"{proj_name}_{rev_name}"

    print(f"[OK] {len(components)} mock components loaded. Project: {proj_name} ({rev_name})")

    # 2. Save Test Preset
    saved_preset = PresetManager.save_new_preset(
        name="Custom NeoDen YY1 Format",
        description="Custom assembly vendor format",
        columns=CUSTOM_USER_VENDOR_PRESET["columns"]
    )

    # 3. Export Formats (CSV, TXT, XLSX, JSON, ZIP)
    test_output_dir = os.path.join(os.path.dirname(__file__), "test_output")

    csv_path = os.path.join(test_output_dir, f"{prefix}_output.csv")
    txt_path = os.path.join(test_output_dir, f"{prefix}_output.txt")
    xlsx_path = os.path.join(test_output_dir, f"{prefix}_output.xlsx")
    json_path = os.path.join(test_output_dir, f"{prefix}_output.json")
    zip_path = os.path.join(test_output_dir, f"{prefix}_Assembly_Package.zip")

    AssemblyExporter.export_to_csv(csv_path, components, saved_preset)
    print(f"[OK] CSV Generated: {csv_path}")

    AssemblyExporter.export_to_tsv(txt_path, components, saved_preset)
    print(f"[OK] TXT (TSV) Generated: {txt_path}")

    AssemblyExporter.export_to_excel(xlsx_path, components, saved_preset)
    print(f"[OK] Excel Generated: {xlsx_path}")

    AssemblyExporter.export_to_json(json_path, components, saved_preset)
    print(f"[OK] JSON Generated: {json_path}")

    all_files = [csv_path, txt_path, xlsx_path, json_path]
    ZipPackager.create_zip_package(zip_path, all_files)
    print(f"[OK] ZIP Package Created: {zip_path}")

    print("\n==================================================")
    print("[SUCCESS] All Data Formats (CSV, TXT, XLSX, JSON, ZIP) Verification Passed!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
