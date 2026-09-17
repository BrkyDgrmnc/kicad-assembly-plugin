"""
KiCad 10 Dizgi ve Montaj Eklentisi - Profil Yöneticisi (Preset Manager)
"""

import os
import json
from typing import List, Dict, Any
from plugin.config import ALL_PRESETS

class PresetManager:
    """
    Kullanıcıların kendi makine veya firma formatlarını özel isimlerle kaydetmesini,
    yüklemesini, düzenlemesini ve silmesini sağlayan yönetici sınıfı.
    """

    @classmethod
    def get_config_path(cls) -> str:
        """
        Kullanıcı profillerinin saklanacağı varsayılan JSON dosya yolu.
        """
        appdata = os.getenv("APPDATA")
        if appdata and os.path.exists(os.path.join(appdata, "kicad")):
            target_dir = os.path.join(appdata, "kicad", "10.0")
        else:
            target_dir = os.path.expanduser("~")
        
        os.makedirs(target_dir, exist_ok=True)
        return os.path.join(target_dir, "custom_assembly_presets.json")

    @classmethod
    def load_user_presets(cls) -> List[Dict[str, Any]]:
        """
        Kullanıcının kaydettiği özel profilleri yükler.
        """
        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return []

    @classmethod
    def save_user_presets(cls, presets: List[Dict[str, Any]]) -> bool:
        """
        Kullanıcı profillerini JSON dosyasına kaydeder.
        """
        path = cls.get_config_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def get_all_presets(cls) -> List[Dict[str, Any]]:
        """
        Dahili varsayılan profiller ile kullanıcının kaydettiği özel profilleri birleştirir.
        """
        user_presets = cls.load_user_presets()
        # Kullanıcı profillerini başa veya sona ekleyelim
        combined = list(ALL_PRESETS) + user_presets
        return combined

    @classmethod
    def save_new_preset(cls, name: str, description: str, columns: List[Dict[str, str]], delimiter: str = ",", decimal_sep: str = ".") -> Dict[str, Any]:
        """
        Yeni bir özel profili kaydeder.
        """
        user_presets = cls.load_user_presets()
        
        # ID üret
        safe_id = "user_" + "".join(c for c in name.lower() if c.isalnum() or c == '_')
        
        new_preset = {
            "id": safe_id,
            "name": name,
            "description": description or f"Özel Profil: {name}",
            "file_extension": ".csv",
            "delimiter": delimiter,
            "decimal_separator": decimal_sep,
            "include_header": True,
            "is_custom": True,
            "columns": columns
        }

        # Var olan bir profil adı varsa güncelle, yoksa ekle
        existing_index = -1
        for idx, p in enumerate(user_presets):
            if p.get("name") == name or p.get("id") == safe_id:
                existing_index = idx
                break

        if existing_index != -1:
            user_presets[existing_index] = new_preset
        else:
            user_presets.append(new_preset)

        cls.save_user_presets(user_presets)
        return new_preset

    @classmethod
    def delete_preset(cls, preset_id: str) -> bool:
        """
        Kullanıcıya ait özel bir profili siler.
        """
        user_presets = cls.load_user_presets()
        filtered = [p for p in user_presets if p.get("id") != preset_id]
        if len(filtered) != len(user_presets):
            cls.save_user_presets(filtered)
            return True
        return False
