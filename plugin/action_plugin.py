"""
KiCad 10 Dizgi ve Montaj Eklentisi - ActionPlugin Kayıt Dosyası
"""

import os

try:
    import pcbnew
    import wx
    from plugin.gui.main_dialog import MainAssemblyDialog

    class AssemblyExporterActionPlugin(pcbnew.ActionPlugin):
        def defaults(self):
            self.name = "KiCad 10 Dizgi ve Montaj Eklentisi"
            self.category = "Fabrication / Assembly"
            self.description = "Özel firma şablonları ve dizgi makineleri için BOM & CPL dosyaları üretir."
            self.show_toolbar_button = True
            
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icon.png"))
            if os.path.exists(icon_path):
                self.icon_file_name = icon_path

        def Run(self):
            board = pcbnew.GetBoard()
            dialog = MainAssemblyDialog(parent=None, board=board)
            dialog.ShowModal()
            dialog.Destroy()

except ImportError:
    # Standalone modda veya pcbnew modülü olmadan çalışıyorsa
    pass
