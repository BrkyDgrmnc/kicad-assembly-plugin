"""
KiCad 10 Dizgi ve Montaj Eklentisi - PCB Board Veri Ayrıştırıcı
"""

import os
from typing import List, Dict, Any, Tuple
from plugin.core.rotation_helper import RotationHelper

class BoardParser:
    """
    pcbnew.BOARD nesnesini (veya Mock veriyi) tarayarak dizgiye uygun bileşen listesini çıkarır.
    KiCad 8, 9 ve 10 Python API sürümleri ile %100 uyumludur.
    """

    def __init__(self, origin_mode: str = "aux", selected_fiducial: str = "", custom_offsets: Dict[str, float] = None):
        self.origin_mode = origin_mode
        self.selected_fiducial = selected_fiducial
        self.rotation_helper = RotationHelper(custom_offsets)

    def parse_board(self, board=None) -> List[Dict[str, Any]]:
        """
        KiCad board nesnesini ayrıştırır. Eğer board None ise mock veri döner.
        """
        if board is None:
            return self.get_mock_components()

        components = []
        try:
            import pcbnew
        except ImportError:
            return self.get_mock_components()

        # Orijin koordinatını hesapla
        origin_x = 0.0
        origin_y = 0.0

        if self.origin_mode == "aux":
            try:
                aux_origin = board.GetDesignSettings().GetAuxOrigin()
                origin_x = pcbnew.ToMM(aux_origin.x)
                origin_y = pcbnew.ToMM(aux_origin.y)
            except Exception:
                pass
        elif self.origin_mode == "fiducial" and self.selected_fiducial:
            try:
                for fp in board.GetFootprints():
                    ref = str(fp.GetReference()) if hasattr(fp, "GetReference") else ""
                    if ref == self.selected_fiducial:
                        pos = fp.GetPosition()
                        origin_x = pcbnew.ToMM(pos.x)
                        origin_y = pcbnew.ToMM(pos.y)
                        break
            except Exception:
                pass

        try:
            footprints = board.GetFootprints()
        except Exception:
            footprints = []

        for fp in footprints:
            # DNP ve Exclude filtreleme
            try:
                if hasattr(fp, "IsDNP") and fp.IsDNP():
                    continue
                attrs = fp.GetAttributes()
                if attrs & pcbnew.FP_EXCLUDE_FROM_BOM or attrs & pcbnew.FP_EXCLUDE_FROM_POS:
                    continue
            except Exception:
                pass

            # 1. Reference & Value
            try:
                ref = str(fp.GetReference())
            except Exception:
                ref = "REF?"

            try:
                val = str(fp.GetValue())
            except Exception:
                val = ""
            
            # 2. Footprint Adı
            fp_id = ""
            try:
                if hasattr(fp, "GetFPID"):
                    fpid = fp.GetFPID()
                    if hasattr(fpid, "GetLibItemName"):
                        item_name = fpid.GetLibItemName()
                        if hasattr(item_name, "AsString"):
                            fp_id = str(item_name.AsString())
                        else:
                            fp_id = str(item_name)
                    elif hasattr(fpid, "GetUniStringLibItemName"):
                        fp_id = str(fpid.GetUniStringLibItemName())
                    else:
                        fp_id = str(fpid)
            except Exception:
                pass

            if not fp_id:
                try:
                    if hasattr(fp, "GetFootprintName"):
                        fp_id = str(fp.GetFootprintName())
                    else:
                        fp_id = str(ref)
                except Exception:
                    fp_id = "UNKNOWN"

            # 3. Pozisyon (Orijine göre bağıl mm)
            pos_x = 0.0
            pos_y = 0.0
            try:
                pos = fp.GetPosition()
                pos_x = round(pcbnew.ToMM(pos.x) - origin_x, 3)
                pos_y = round(pcbnew.ToMM(pos.y) - origin_y, 3)
            except Exception:
                pass

            # 4. Katman
            layer_name = "Top"
            try:
                if fp.GetLayer() == pcbnew.B_Cu:
                    layer_name = "Bottom"
                elif fp.GetLayer() == pcbnew.F_Cu:
                    layer_name = "Top"
                else:
                    layer_name = "Top" if "F." in fp.GetLayerName() else "Bottom"
            except Exception:
                pass

            is_bottom = (layer_name == "Bottom")

            # 5. Dönüş Açısı
            raw_rot = 0.0
            try:
                if hasattr(fp, "GetOrientationDegrees"):
                    raw_rot = float(fp.GetOrientationDegrees())
                elif hasattr(fp, "GetOrientation"):
                    rot_obj = fp.GetOrientation()
                    if hasattr(rot_obj, "AsDegrees"):
                        raw_rot = float(rot_obj.AsDegrees())
                    else:
                        raw_rot = float(rot_obj) / 10.0
            except Exception:
                raw_rot = 0.0

            adjusted_rot = self.rotation_helper.calculate_rotation(raw_rot, fp_id, is_bottom)

            # 6. Özel Alanlar
            properties = {}
            try:
                if hasattr(fp, "GetProperties"):
                    props = fp.GetProperties()
                    for k, v in props.items():
                        properties[str(k)] = str(v)
            except Exception:
                pass

            lcsc_part = properties.get("LCSC", properties.get("LCSC Part #", properties.get("LCSC_PN", "")))
            mpn_part = properties.get("MPN", properties.get("Manufacturer Part Number", properties.get("Part Number", "")))
            mfr_part = properties.get("Manufacturer", properties.get("MFR", ""))

            comp_dict = {
                "Reference": ref,
                "Footprint": fp_id,
                "Type": fp_id,
                "Value": val,
                "Layer": layer_name,
                "X": pos_x,
                "Y": pos_y,
                "Rotation": adjusted_rot,
                "RawRotation": raw_rot,
                "LCSC": lcsc_part,
                "MPN": mpn_part,
                "Manufacturer": mfr_part
            }
            components.append(comp_dict)

        components.sort(key=lambda c: (c["Reference"][:2], len(c["Reference"]), c["Reference"]))
        return components

    def get_fiducial_references(self, board=None) -> List[str]:
        comps = self.parse_board(board)
        fiducials = []
        for c in comps:
            ref = c["Reference"]
            fp = c["Footprint"].upper()
            val = c["Value"].upper()
            if "FIDUCIAL" in fp or "FIDUCIAL" in val or "FID" in ref.upper() or "REF" in ref.upper():
                fiducials.append(ref)
        return fiducials or ["REF1", "REF2", "FID1"]

    @classmethod
    def get_board_project_info(cls, board=None) -> Tuple[str, str]:
        """
        PCB dosyasından Proje Adı ve Revizyon numarasını döner (ProjectName, Revision).
        """
        project_name = "PCB_Project"
        revision = "v1.0"

        if board is not None:
            try:
                file_name = board.GetFileName()
                if file_name:
                    base = os.path.basename(file_name)
                    project_name = os.path.splitext(base)[0]
            except Exception:
                pass

            try:
                title_block = board.GetTitleBlock()
                rev = title_block.GetRevision()
                if rev and str(rev).strip():
                    revision = str(rev).strip()
            except Exception:
                pass

        return project_name, revision

    @staticmethod
    def get_mock_components() -> List[Dict[str, Any]]:
        return [
            {
                "Reference": "REF1",
                "Footprint": "FIDUCIAL",
                "Type": "FIDUCIAL",
                "Value": "{ValUe}",
                "Layer": "Top",
                "X": -155.575,
                "Y": 150.495,
                "Rotation": 180.0,
                "LCSC": "",
                "MPN": "",
                "Manufacturer": ""
            },
            {
                "Reference": "REF2",
                "Footprint": "FIDUCIAL",
                "Type": "FIDUCIAL",
                "Value": "{ValUe}",
                "Layer": "Top",
                "X": 0.000,
                "Y": 1.270,
                "Rotation": 180.0,
                "LCSC": "",
                "MPN": "",
                "Manufacturer": ""
            },
            {
                "Reference": "R55",
                "Footprint": "RC1206",
                "Type": "RC1206",
                "Value": "0R",
                "Layer": "Top",
                "X": -124.267,
                "Y": 20.040,
                "Rotation": 180.0,
                "LCSC": "C17710",
                "MPN": "0603WAF0000T5E",
                "Manufacturer": "Uniroyal"
            },
            {
                "Reference": "R56",
                "Footprint": "RC1206",
                "Type": "RC1206",
                "Value": "0R",
                "Layer": "Top",
                "X": -124.267,
                "Y": 22.580,
                "Rotation": 180.0,
                "LCSC": "C17710",
                "MPN": "0603WAF0000T5E",
                "Manufacturer": "Uniroyal"
            },
            {
                "Reference": "R15",
                "Footprint": "RC0805",
                "Type": "RC0805",
                "Value": "0R",
                "Layer": "Top",
                "X": -57.468,
                "Y": 111.590,
                "Rotation": 90.0,
                "LCSC": "C17414",
                "MPN": "0805W8F0000T5E",
                "Manufacturer": "Uniroyal"
            },
            {
                "Reference": "C1",
                "Footprint": "C0805",
                "Type": "C0805",
                "Value": "100nF",
                "Layer": "Top",
                "X": -42.100,
                "Y": 85.300,
                "Rotation": 0.0,
                "LCSC": "C49656",
                "MPN": "CL21B104KBFNNNE",
                "Manufacturer": "Samsung"
            },
            {
                "Reference": "U1",
                "Footprint": "SOIC-8_3.9x4.9mm_P1.27mm",
                "Type": "SOIC-8",
                "Value": "STM32F030F4P6",
                "Layer": "Top",
                "X": -80.500,
                "Y": 50.250,
                "Rotation": 270.0,
                "LCSC": "C23942",
                "MPN": "STM32F030F4P6",
                "Manufacturer": "STMicroelectronics"
            }
        ]
