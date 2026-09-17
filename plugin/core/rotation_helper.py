"""
KiCad 10 Dizgi ve Montaj Eklentisi - Dönüş Açısı (Rotation Offset) Yardımcısı
"""

from typing import Dict
from plugin.config import DEFAULT_ROTATION_OFFSETS

class RotationHelper:
    """
    Dizgi makineleri ve JLCPCB gibi üreticilerin standart kılıf açı yönlendirme farklarını düzeltir.
    """

    def __init__(self, custom_offsets: Dict[str, float] = None):
        self.offsets = dict(DEFAULT_ROTATION_OFFSETS)
        if custom_offsets:
            self.offsets.update(custom_offsets)

    def get_offset(self, footprint_name: str) -> float:
        """
        Footprint adına göre dönüş açısı offsetini bulur.
        Tam eşleşme veya alt dize eşleşmesi kontrol eder.
        """
        if not footprint_name:
            return 0.0

        # Tam eşleşme
        if footprint_name in self.offsets:
            return self.offsets[footprint_name]

        # Alt dize / kalıp eşleşmesi (Örn: Footprint içinde SOT-23 geçiyorsa)
        footprint_upper = footprint_name.upper()
        for pattern, offset in self.offsets.items():
            if pattern.upper() in footprint_upper:
                return offset

        return 0.0

    def calculate_rotation(self, raw_rotation: float, footprint_name: str, is_bottom: bool = False) -> float:
        """
        KiCad hamster dönüş açısını üretici offseti ile toplayıp 0-360 derece aralığına normalize eder.
        """
        offset = self.get_offset(footprint_name)
        final_rot = (raw_rotation + offset) % 360.0
        
        # KiCad'de alt katman (Bottom) komponenlerinin simetri açı mantığı
        if is_bottom:
            final_rot = (360.0 - final_rot) % 360.0

        return round(final_rot, 1)
