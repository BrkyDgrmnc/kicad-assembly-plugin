"""
KiCad 10 Dizgi ve Montaj Eklentisi Kök Giriş Noktası
"""

import os
import sys

# Eklenti kök dizinini sys.path'e ekle
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    from plugin.action_plugin import AssemblyExporterActionPlugin
    # ActionPlugin'i KiCad PCB Editor'e kaydet
    AssemblyExporterActionPlugin().register()
except Exception as e:
    sys.stderr.write(f"KiCad Assembly Plugin Register Failed: {e}\n")
