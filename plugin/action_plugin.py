"""
KiCad 10 Assembly & Fabrication Tool - ActionPlugin Registration File
"""

import os

try:
    import pcbnew
    import wx
    from plugin.gui.main_dialog import MainAssemblyDialog

    class AssemblyExporterActionPlugin(pcbnew.ActionPlugin):
        def defaults(self):
            self.name = "KiCad 10 Assembly & Fabrication Tool"
            self.category = "Fabrication / Assembly"
            self.description = "Customizable BOM & Pick and Place (CPL) generator for KiCad 10 with custom vendor templates and machine presets."
            self.show_toolbar_button = True
            
            # Load icon (check icon.png or P&P.png)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            icon_path = os.path.join(base_dir, "icon.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(base_dir, "P&P.png")
            if os.path.exists(icon_path):
                self.icon_file_name = icon_path

        def Run(self):
            board = pcbnew.GetBoard()
            dialog = MainAssemblyDialog(parent=None, board=board)
            dialog.ShowModal()
            dialog.Destroy()

except ImportError:
    # Running in standalone mode or without pcbnew
    pass
