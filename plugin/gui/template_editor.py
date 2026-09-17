"""
KiCad 10 Assembly & Fabrication Tool - Column and Template Editor Dialog
"""

import wx
from typing import Dict, Any, List
from plugin.core.preset_manager import PresetManager

class TemplateEditorDialog(wx.Dialog):
    """
    wx.Dialog window allowing users to customize column headers, ordering, and dynamic tag expressions
    (e.g., {Footprint}-{Value}) and save as a custom preset.
    """

    def __init__(self, parent, current_preset: Dict[str, Any]):
        super().__init__(parent, title="Column & Format Template Editor", size=(800, 600),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.preset = dict(current_preset)
        self.columns = [dict(c) for c in self.preset.get("columns", [])]

        self.init_ui()
        self.Centre()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top Guide Box
        header_box = wx.StaticBox(self, label="Dynamic Template Engine Guide")
        header_sizer = wx.StaticBoxSizer(header_box, wx.VERTICAL)
        help_lbl = wx.StaticText(self, label=(
            "Supported Tags: You can use {Reference}, {Footprint}, {Value}, {Layer}, {X}, {Y}, {Rotation}, {LCSC}, {MPN} in column templates.\n"
            "Combined Expression Example: '{Footprint}-{Value}' -> generates 'RC1206-0R'."
        ))
        help_lbl.SetForegroundColour(wx.Colour(0, 102, 204))
        header_sizer.Add(help_lbl, 0, wx.ALL, 8)
        main_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Column List & Side Buttons
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Column Header", width=230)
        self.list_ctrl.InsertColumn(1, "Template Expression", width=380)
        content_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.RIGHT, 10)

        # Side Action Buttons
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_add = wx.Button(self, label="➕ Add Column")
        self.btn_add.SetToolTip("Add a new column header and template tag expression.")
        
        self.btn_edit = wx.Button(self, label="✏️ Edit Column")
        self.btn_edit.SetToolTip("Edit the selected column header or template expression.")
        
        self.btn_delete = wx.Button(self, label="🗑️ Delete Column")
        self.btn_delete.SetToolTip("Remove the selected column from the template.")
        
        self.btn_up = wx.Button(self, label="⬆️ Move Up")
        self.btn_up.SetToolTip("Shift the selected column up in the export order.")
        
        self.btn_down = wx.Button(self, label="⬇️ Move Down")
        self.btn_down.SetToolTip("Shift the selected column down in the export order.")

        btn_sizer.Add(self.btn_add, 0, wx.EXPAND | wx.BOTTOM, 6)
        btn_sizer.Add(self.btn_edit, 0, wx.EXPAND | wx.BOTTOM, 6)
        btn_sizer.Add(self.btn_delete, 0, wx.EXPAND | wx.BOTTOM, 16)
        btn_sizer.Add(self.btn_up, 0, wx.EXPAND | wx.BOTTOM, 6)
        btn_sizer.Add(self.btn_down, 0, wx.EXPAND | wx.BOTTOM, 6)

        content_sizer.Add(btn_sizer, 0, wx.ALIGN_TOP)
        main_sizer.Add(content_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Bottom Bar Buttons (Cancel / Save As Preset / Apply Template)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_save_as = wx.Button(self, label="💾 Save As Preset...")
        self.btn_save_as.SetToolTip("Save this column layout under a custom preset name.")
        self.btn_save_as.SetBackgroundColour(wx.Colour(234, 246, 255))
        bottom_sizer.Add(self.btn_save_as, 0, wx.LEFT, 10)

        bottom_sizer.AddStretchSpacer()
        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        self.btn_cancel.SetToolTip("Discard changes and close editor.")
        
        self.btn_save = wx.Button(self, wx.ID_OK, label="✓ Apply Template")
        self.btn_save.SetToolTip("Apply current column modifications to the export template.")

        bottom_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 8)
        bottom_sizer.Add(self.btn_save, 0, wx.RIGHT, 10)
        main_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)

        # Event Bindings
        self.btn_add.Bind(wx.EVT_BUTTON, self.on_add_col)
        self.btn_edit.Bind(wx.EVT_BUTTON, self.on_edit_col)
        self.btn_delete.Bind(wx.EVT_BUTTON, self.on_delete_col)
        self.btn_up.Bind(wx.EVT_BUTTON, self.on_move_up)
        self.btn_down.Bind(wx.EVT_BUTTON, self.on_move_down)
        self.btn_save_as.Bind(wx.EVT_BUTTON, self.on_save_as_preset)

        self.refresh_list()

    def refresh_list(self):
        self.list_ctrl.DeleteAllItems()
        for idx, col in enumerate(self.columns):
            self.list_ctrl.InsertItem(idx, col.get("header", ""))
            self.list_ctrl.SetItem(idx, 1, col.get("template", ""))

    def on_add_col(self, event):
        dlg = ColumnEditDialog(self, "Add New Column", "", "{Value}")
        if dlg.ShowModal() == wx.ID_OK:
            header, template = dlg.get_values()
            if header:
                self.columns.append({"header": header, "template": template})
                self.refresh_list()

    def on_edit_col(self, event):
        sel = self.list_ctrl.GetFirstSelected()
        if sel == -1:
            wx.MessageBox("Please select a column to edit.", "Information", wx.OK | wx.ICON_INFORMATION)
            return
        col = self.columns[sel]
        dlg = ColumnEditDialog(self, "Edit Column", col.get("header", ""), col.get("template", ""))
        if dlg.ShowModal() == wx.ID_OK:
            header, template = dlg.get_values()
            if header:
                self.columns[sel] = {"header": header, "template": template}
                self.refresh_list()

    def on_delete_col(self, event):
        sel = self.list_ctrl.GetFirstSelected()
        if sel == -1:
            return
        del self.columns[sel]
        self.refresh_list()

    def on_move_up(self, event):
        sel = self.list_ctrl.GetFirstSelected()
        if sel > 0:
            self.columns[sel], self.columns[sel - 1] = self.columns[sel - 1], self.columns[sel]
            self.refresh_list()
            self.list_ctrl.Select(sel - 1)

    def on_move_down(self, event):
        sel = self.list_ctrl.GetFirstSelected()
        if sel != -1 and sel < len(self.columns) - 1:
            self.columns[sel], self.columns[sel + 1] = self.columns[sel + 1], self.columns[sel]
            self.refresh_list()
            self.list_ctrl.Select(sel + 1)

    def on_save_as_preset(self, event):
        dlg = wx.TextEntryDialog(self, "Please enter a name for the new custom preset profile:\n(e.g., Custom NeoDen YY1 Format)", "Save Custom Preset Profile")
        if dlg.ShowModal() == wx.ID_OK:
            preset_name = dlg.GetValue().strip()
            if preset_name:
                saved = PresetManager.save_new_preset(preset_name, f"User Preset Profile: {preset_name}", self.columns)
                self.preset = saved
                wx.MessageBox(f"Preset profile '{preset_name}' saved successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
                self.EndModal(wx.ID_OK)

    def get_updated_preset(self) -> Dict[str, Any]:
        self.preset["columns"] = self.columns
        return self.preset


class ColumnEditDialog(wx.Dialog):
    def __init__(self, parent, title, header="", template=""):
        super().__init__(parent, title=title, size=(460, 220))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 2, 10, 10)
        grid.AddGrowableCol(1, 1)

        grid.Add(wx.StaticText(self, label="Column Header:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_header = wx.TextCtrl(self, value=header)
        self.txt_header.SetToolTip("The title header that will appear in the top row of exported files.")
        grid.Add(self.txt_header, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self, label="Template Expression:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_template = wx.TextCtrl(self, value=template)
        self.txt_template.SetToolTip("The dynamic value pattern (e.g., {Reference}, {Footprint}-{Value}, {X}).")
        grid.Add(self.txt_template, 1, wx.EXPAND)

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 15)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 0, wx.RIGHT, 8)
        btn_sizer.Add(wx.Button(self, wx.ID_OK, "OK"), 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Centre()

    def get_values(self):
        return self.txt_header.GetValue().strip(), self.txt_template.GetValue().strip()
