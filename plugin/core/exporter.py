"""
KiCad 10 Dizgi ve Montaj Eklentisi - Çıktı Üretici (Exporter)
"""

import os
import csv
import json
import zipfile
from typing import List, Dict, Any
from plugin.core.template_engine import TemplateEngine

class NativeXlsxWriter:
    """
    Harici kütüphaneye (openpyxl vb.) ihtiyaç duymadan saf Python zlib/zipfile ile 
    %100 yerel Microsoft Excel (.xlsx) dosyası üreten modül.
    """
    @classmethod
    def write_xlsx(cls, filepath: str, headers: List[str], resolved_rows: List[Dict[str, Any]]) -> str:
        def xml_escape(s):
            return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

        sheet_lines = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
            '<sheetData>'
        ]

        sheet_lines.append('<row r="1">')
        for col_idx, h in enumerate(headers, 1):
            col_letter = chr(64+col_idx) if col_idx <= 26 else f"A{chr(64+col_idx-26)}"
            sheet_lines.append(f'<c r="{col_letter}1" t="inlineStr"><is><t>{xml_escape(h)}</t></is></c>')
        sheet_lines.append('</row>')

        for r_idx, row in enumerate(resolved_rows, 2):
            sheet_lines.append(f'<row r="{r_idx}">')
            for c_idx, h in enumerate(headers, 1):
                col_letter = chr(64+c_idx) if c_idx <= 26 else f"A{chr(64+c_idx-26)}"
                val = str(row.get(h, ""))
                sheet_lines.append(f'<c r="{col_letter}{r_idx}" t="inlineStr"><is><t>{xml_escape(val)}</t></is></c>')
            sheet_lines.append('</row>')

        sheet_lines.append('</sheetData>')
        sheet_lines.append('</worksheet>')
        sheet_xml = "\n".join(sheet_lines)

        content_types = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
        rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        workbook_xml = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Assembly Data" sheetId="1" r:id="rId1"/></sheets></workbook>'
        workbook_rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', content_types)
            zf.writestr('_rels/.rels', rels)
            zf.writestr('xl/workbook.xml', workbook_xml)
            zf.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
            zf.writestr('xl/worksheets/sheet1.xml', sheet_xml)

        return filepath


class AssemblyExporter:
    """
    Seçilen şablon konfigürasyonuna göre CSV, TSV/TXT, Excel ve JSON üreticisi.
    """

    @classmethod
    def export_to_csv(cls, file_path: str, components: List[Dict[str, Any]], preset: Dict[str, Any], delimiter: str = None) -> str:
        columns = preset.get("columns", [])
        delim = delimiter or preset.get("delimiter", ",")
        include_header = preset.get("include_header", True)

        resolved_rows = TemplateEngine.process_components(components, columns)
        headers = [col.get("header", "") for col in columns]

        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=delim)
            if include_header:
                writer.writeheader()
            for row in resolved_rows:
                writer.writerow(row)

        return file_path

    @classmethod
    def export_to_tsv(cls, file_path: str, components: List[Dict[str, Any]], preset: Dict[str, Any]) -> str:
        return cls.export_to_csv(file_path, components, preset, delimiter="\t")

    @classmethod
    def export_to_json(cls, file_path: str, components: List[Dict[str, Any]], preset: Dict[str, Any]) -> str:
        columns = preset.get("columns", [])
        resolved_rows = TemplateEngine.process_components(components, columns)

        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump(resolved_rows, f, ensure_ascii=False, indent=2)

        return file_path

    @classmethod
    def export_to_excel(cls, file_path: str, components: List[Dict[str, Any]], preset: Dict[str, Any]) -> str:
        columns = preset.get("columns", [])
        resolved_rows = TemplateEngine.process_components(components, columns)
        headers = [col.get("header", "") for col in columns]

        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Assembly Data"

            ws.append(headers)
            for row in resolved_rows:
                ws.append([row.get(h, "") for h in headers])

            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            wb.save(file_path)
            return file_path
        except Exception:
            return NativeXlsxWriter.write_xlsx(file_path, headers, resolved_rows)
