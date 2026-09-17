"""
KiCad 10 Action Plugin Root Entry File
"""

import os
import sys

plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    from plugin.action_plugin import AssemblyExporterActionPlugin
    AssemblyExporterActionPlugin().register()
except Exception as e:
    sys.stderr.write(f"KiCad Assembly Plugin Register Failed: {e}\n")
