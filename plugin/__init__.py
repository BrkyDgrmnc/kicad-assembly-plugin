"""
KiCad 10 Dizgi ve Montaj Eklentisi
"""

try:
    from plugin.action_plugin import AssemblyExporterActionPlugin
    AssemblyExporterActionPlugin().register()
except Exception:
    pass
