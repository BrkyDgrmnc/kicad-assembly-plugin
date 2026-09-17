"""
KiCad 10 Dizgi ve Montaj Eklentisi - Dinamik Şablon ve Etiket Çözücü
"""

import re
from typing import Dict, Any, List

class TemplateEngine:
    """
    Kullanıcının tanımladığı sütun şablonlarındaki etiketleri ({Reference}, {Footprint}-{Value} vb.)
    bileşenin gerçek verileri ile birleştiren şablon motoru.
    """

    TAG_PATTERN = re.compile(r'\{([A-Za-z0-9_]+)\}')

    @classmethod
    def resolve_template(cls, template_str: str, component_data: Dict[str, Any]) -> str:
        """
        Örnek template_str: "{Footprint}-{Value}"
        component_data: {'Footprint': 'RC1206', 'Value': '0R', ...}
        Döndürülen: "RC1206-0R"
        """
        if not template_str:
            return ""

        # Case-insensitive eşleşme için component_data anahtarlarının küçük harfli haritasını çıkarıyoruz
        lower_map = {k.lower(): v for k, v in component_data.items()}

        def replace_tag(match):
            tag_name = match.group(1)
            lower_tag = tag_name.lower()
            
            # Etiket takma adları (Aliases)
            if lower_tag in ["ref", "refdes", "reference"]:
                lower_tag = "reference"
            elif lower_tag in ["patternname", "pattern", "package", "footprint"]:
                lower_tag = "footprint"
            elif lower_tag in ["val", "value"]:
                lower_tag = "value"
            elif lower_tag in ["locx", "locationx", "midx", "centerx", "x"]:
                lower_tag = "x"
            elif lower_tag in ["locy", "locationy", "midy", "centery", "y"]:
                lower_tag = "y"
            elif lower_tag in ["rot", "rotation", "angle"]:
                lower_tag = "rotation"
            elif lower_tag in ["layer", "side"]:
                lower_tag = "layer"

            if lower_tag in lower_map:
                val = lower_map[lower_tag]
                return str(val) if val is not None else ""
            else:
                # Eşleşmeyen etiket bulunursa olduğu gibi tut veya boş dön
                return f"{{{tag_name}}}"

        result = cls.TAG_PATTERN.sub(replace_tag, template_str)
        return result

    @classmethod
    def process_components(cls, components: List[Dict[str, Any]], column_definitions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Bileşen listesini alır ve verilen sütun tanımlarına göre çıktı satırlarını oluşturur.
        column_definitions: [ {"header": "RefDes", "template": "{Reference}"}, {"header": "smd value", "template": "{Footprint}-{Value}"} ]
        """
        output_rows = []
        for comp in components:
            row = {}
            for col_def in column_definitions:
                header = col_def.get("header", "Column")
                template = col_def.get("template", "")
                resolved_value = cls.resolve_template(template, comp)
                row[header] = resolved_value
            output_rows.append(row)
        return output_rows
