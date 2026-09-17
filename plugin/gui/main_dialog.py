"""
KiCad 10 Assembly & Fabrication Tool - Main wxPython Dialog
"""

import os
import wx
import wx.grid
from typing import List, Dict, Any

from plugin.config import APP_NAME, APP_VERSION, CUSTOM_USER_VENDOR_PRESET, DEFAULT_ROTATION_OFFSETS
from plugin.core.preset_manager import PresetManager
from plugin.core.board_parser import BoardParser
from plugin.core.exporter import AssemblyExporter
from plugin.core.zip_packager import ZipPackager
from plugin.gui.components.preview_table import PreviewGridTable
from plugin.gui.template_editor import TemplateEditorDialog

class MainAssemblyDialog(wx.Dialog):
    """
    User-friendly multi-tab interface for KiCad 10 Assembly & Fabrication Tool.
    """

    def __init__(self, parent=None, board=None):
        super().__init__(parent, title=f"{APP_NAME} - v{APP_VERSION}", size=(980, 720),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

        self.board = board
        self.origin_mode = "aux"
        self.selected_fiducial = ""
        self.custom_offsets = dict(DEFAULT_ROTATION_OFFSETS)

        # Project Name & Revision Info
        self.project_name, self.revision = BoardParser.get_board_project_info(self.board)

        self.reload_components()
        self.reload_presets()
        self.current_preset = dict(CUSTOM_USER_VENDOR_PRESET)

        self.init_ui()
        self.Centre()

    def reload_components(self):
        self.parser = BoardParser(
            origin_mode=self.origin_mode,
            selected_fiducial=self.selected_fiducial,
            custom_offsets=self.custom_offsets
        )
        self.components = self.parser.parse_board(self.board)
        self.fiducials = self.parser.get_fiducial_references(self.board)

    def reload_presets(self):
        self.presets = PresetManager.get_all_presets()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = wx.Notebook(self)

        # Tab 1: Main Preview & Generation
        self.tab_preview = wx.Panel(self.notebook)
        self.setup_tab_preview()
        self.notebook.AddPage(self.tab_preview, "📊 Assembly Output & Preview")

        # Tab 2: Template & Column Configuration
        self.tab_template = wx.Panel(self.notebook)
        self.setup_tab_template()
        self.notebook.AddPage(self.tab_template, "🛠️ Template & Profile Manager")

        # Tab 3: Machine & Rotation Settings / Origin Selection
        self.tab_settings = wx.Panel(self.notebook)
        self.setup_tab_settings()
        self.notebook.AddPage(self.tab_settings, "⚙️ Rotation & Machine Settings")

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 8)

        # Bottom Action Bar
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.status_text = wx.StaticText(self, label=f"Total {len(self.components)} assembly components loaded.")
        self.status_text.SetForegroundColour(wx.Colour(180, 200, 220))
        bottom_sizer.Add(self.status_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        bottom_sizer.AddStretchSpacer()
        
        self.btn_close = wx.Button(self, wx.ID_CANCEL, "Close")
        self.btn_close.SetToolTip("Close the Assembly Plugin dialog.")
        
        self.btn_export = wx.Button(self, wx.ID_OK, "🚀 Generate Assembly Files")
        self.btn_export.SetToolTip("Export all selected assembly format files to the chosen output directory.")
        self.btn_export.SetBackgroundColour(wx.Colour(0, 120, 215))
        self.btn_export.SetForegroundColour(wx.WHITE)
        font = self.btn_export.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.btn_export.SetFont(font)

        bottom_sizer.Add(self.btn_close, 0, wx.RIGHT, 8)
        bottom_sizer.Add(self.btn_export, 0, wx.RIGHT, 10)

        main_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.SetSizer(main_sizer)

        self.btn_export.Bind(wx.EVT_BUTTON, self.on_export)
        self.update_preview()

    def setup_tab_preview(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Project Info & Format Box
        top_box = wx.StaticBox(self.tab_preview, label="Project Information & Preset Format")
        top_sizer = wx.StaticBoxSizer(top_box, wx.HORIZONTAL)

        lbl_proj = wx.StaticText(self.tab_preview, label="Project Name:")
        top_sizer.Add(lbl_proj, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        
        self.txt_project_name = wx.TextCtrl(self.tab_preview, value=self.project_name, size=(140, -1))
        self.txt_project_name.SetToolTip("Enter project name to prefix exported filenames.")
        top_sizer.Add(self.txt_project_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        lbl_rev = wx.StaticText(self.tab_preview, label="Revision:")
        top_sizer.Add(lbl_rev, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        
        self.txt_revision = wx.TextCtrl(self.tab_preview, value=self.revision, size=(70, -1))
        self.txt_revision.SetToolTip("Enter board revision number (e.g. RevA, v1.0) to prefix exported filenames.")
        top_sizer.Add(self.txt_revision, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        lbl_preset = wx.StaticText(self.tab_preview, label="Preset Profile:")
        top_sizer.Add(lbl_preset, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        
        preset_names = [p["name"] for p in self.presets]
        self.combo_presets = wx.ComboBox(self.tab_preview, choices=preset_names, style=wx.CB_READONLY)
        self.combo_presets.SetToolTip("Select a vendor template or Pick & Place machine preset (e.g. Custom Vendor, JLCPCB, NeoDen, Charmhigh).")
        self.combo_presets.SetSelection(0)
        top_sizer.Add(self.combo_presets, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        lbl_search = wx.StaticText(self.tab_preview, label="🔍 Search:")
        top_sizer.Add(lbl_search, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        
        self.txt_search = wx.TextCtrl(self.tab_preview, style=wx.TE_PROCESS_ENTER, size=(120, -1))
        self.txt_search.SetToolTip("Filter components live by RefDes, Value, Footprint, or LCSC/MPN.")
        top_sizer.Add(self.txt_search, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # Table Grid
        self.grid_preview = PreviewGridTable(self.tab_preview)
        sizer.Add(self.grid_preview, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Export Formats and Directory
        out_box = wx.StaticBox(self.tab_preview, label="Export Formats & Destination Directory")
        out_sizer = wx.StaticBoxSizer(out_box, wx.VERTICAL)

        fmt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_fmts = wx.StaticText(self.tab_preview, label="Output Formats:")
        fmt_sizer.Add(lbl_fmts, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.chk_csv = wx.CheckBox(self.tab_preview, label="CSV (.csv)")
        self.chk_csv.SetToolTip("Export assembly data in Comma-Separated Values (.csv) format.")
        self.chk_csv.SetValue(True)

        self.chk_txt = wx.CheckBox(self.tab_preview, label="Tab Text (.txt)")
        self.chk_txt.SetToolTip("Export assembly data in Tab-Separated Values (.txt) format.")
        self.chk_txt.SetValue(True)

        self.chk_xlsx = wx.CheckBox(self.tab_preview, label="Excel (.xlsx)")
        self.chk_xlsx.SetToolTip("Export assembly data in native Microsoft Excel (.xlsx) spreadsheet format.")
        self.chk_xlsx.SetValue(True)

        self.chk_json = wx.CheckBox(self.tab_preview, label="JSON (.json)")
        self.chk_json.SetToolTip("Export assembly data in JSON (.json) format.")
        self.chk_json.SetValue(False)

        fmt_sizer.Add(self.chk_csv, 0, wx.RIGHT, 15)
        fmt_sizer.Add(self.chk_txt, 0, wx.RIGHT, 15)
        fmt_sizer.Add(self.chk_xlsx, 0, wx.RIGHT, 15)
        fmt_sizer.Add(self.chk_json, 0)

        out_sizer.Add(fmt_sizer, 0, wx.EXPAND | wx.ALL, 6)

        dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_dir = wx.StaticText(self.tab_preview, label="Save Directory:")
        dir_sizer.Add(lbl_dir, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        
        default_dir = os.path.expanduser("~/Desktop")
        self.dir_picker = wx.DirPickerCtrl(self.tab_preview, path=default_dir)
        self.dir_picker.SetToolTip("Choose the destination folder where output files will be saved.")
        dir_sizer.Add(self.dir_picker, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        self.chk_zip = wx.CheckBox(self.tab_preview, label="Archive All into ZIP (.zip)")
        self.chk_zip.SetToolTip("Bundle all generated export files into a single .zip archive.")
        self.chk_zip.SetValue(True)
        dir_sizer.Add(self.chk_zip, 0, wx.ALIGN_CENTER_VERTICAL)

        out_sizer.Add(dir_sizer, 0, wx.EXPAND | wx.ALL, 6)

        sizer.Add(out_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.tab_preview.SetSizer(sizer)

        self.combo_presets.Bind(wx.EVT_COMBOBOX, self.on_preset_changed)
        self.txt_search.Bind(wx.EVT_TEXT, self.on_search_changed)

    def setup_tab_template(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        info_box = wx.StaticBox(self.tab_template, label="Custom Profile & Template Editor")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)

        self.lbl_preset_info = wx.StaticText(self.tab_template, label="")
        info_sizer.Add(self.lbl_preset_info, 0, wx.ALL, 10)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_edit_template = wx.Button(self.tab_template, label="⚙️ Customize Columns & Save As Preset...")
        self.btn_edit_template.SetToolTip("Modify exported column headers, dynamic tags, and save under a new preset name.")
        
        self.btn_delete_preset = wx.Button(self.tab_template, label="🗑️ Delete Selected Preset")
        self.btn_delete_preset.SetToolTip("Delete the currently selected custom preset.")
        self.btn_delete_preset.SetForegroundColour(wx.Colour(200, 0, 0))

        btn_row.Add(self.btn_edit_template, 0, wx.RIGHT, 10)
        btn_row.Add(self.btn_delete_preset, 0)

        info_sizer.Add(btn_row, 0, wx.ALL, 10)

        sizer.Add(info_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.tab_template.SetSizer(sizer)

        self.btn_edit_template.Bind(wx.EVT_BUTTON, self.on_open_template_editor)
        self.btn_delete_preset.Bind(wx.EVT_BUTTON, self.on_delete_selected_preset)
        self.update_template_info()

    def setup_tab_settings(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        box_origin = wx.StaticBox(self.tab_settings, label="Origin & Coordinate System Settings (0,0 Point)")
        origin_sizer = wx.StaticBoxSizer(box_origin, wx.VERTICAL)

        self.rb_origin_aux = wx.RadioButton(self.tab_settings, label="Auxiliary / User Origin (KiCad Grid Origin)", style=wx.RB_GROUP)
        self.rb_origin_aux.SetToolTip("Use the PCB Auxiliary Axis Origin set in KiCad.")
        
        self.rb_origin_abs = wx.RadioButton(self.tab_settings, label="Absolute Board Origin (KiCad Sheet 0,0)")
        self.rb_origin_abs.SetToolTip("Use the absolute top-left sheet origin (0,0).")
        
        fid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rb_origin_fid = wx.RadioButton(self.tab_settings, label="Selected Fiducial Component (Selected Fiducial = 0,0):")
        self.rb_origin_fid.SetToolTip("Set the selected Fiducial component's position as the (0,0) origin for all component coordinates.")
        
        self.combo_fiducial = wx.ComboBox(self.tab_settings, choices=self.fiducials, style=wx.CB_READONLY)
        self.combo_fiducial.SetToolTip("Select the specific Fiducial footprint (e.g. FID1) to act as the (0,0) reference origin.")
        if self.fiducials:
            self.combo_fiducial.SetSelection(0)
            self.selected_fiducial = self.fiducials[0]

        fid_sizer.Add(self.rb_origin_fid, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        fid_sizer.Add(self.combo_fiducial, 0, wx.ALIGN_CENTER_VERTICAL)

        origin_sizer.Add(self.rb_origin_aux, 0, wx.ALL, 6)
        origin_sizer.Add(self.rb_origin_abs, 0, wx.ALL, 6)
        origin_sizer.Add(fid_sizer, 0, wx.ALL, 6)

        sizer.Add(origin_sizer, 0, wx.EXPAND | wx.ALL, 10)

        box_rot = wx.StaticBox(self.tab_settings, label="Standard Footprint Rotation Offset Rules")
        rot_sizer = wx.StaticBoxSizer(box_rot, wx.VERTICAL)

        self.list_offsets = wx.ListCtrl(self.tab_settings, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, size=(-1, 180))
        self.list_offsets.InsertColumn(0, "Footprint Pattern / Family", width=300)
        self.list_offsets.InsertColumn(1, "Rotation Offset Angle", width=220)
        rot_sizer.Add(self.list_offsets, 1, wx.EXPAND | wx.ALL, 6)

        sizer.Add(rot_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.tab_settings.SetSizer(sizer)

        self.rb_origin_aux.Bind(wx.EVT_RADIOBUTTON, self.on_origin_changed)
        self.rb_origin_abs.Bind(wx.EVT_RADIOBUTTON, self.on_origin_changed)
        self.rb_origin_fid.Bind(wx.EVT_RADIOBUTTON, self.on_origin_changed)
        self.combo_fiducial.Bind(wx.EVT_COMBOBOX, self.on_fiducial_selected)

        self.refresh_offset_list()

    def refresh_offset_list(self):
        self.list_offsets.DeleteAllItems()
        for idx, (pattern, offset) in enumerate(self.custom_offsets.items()):
            self.list_offsets.InsertItem(idx, pattern)
            self.list_offsets.SetItem(idx, 1, f"{offset:+.1f}°")

    def on_origin_changed(self, event):
        if self.rb_origin_aux.GetValue():
            self.origin_mode = "aux"
        elif self.rb_origin_abs.GetValue():
            self.origin_mode = "absolute"
        elif self.rb_origin_fid.GetValue():
            self.origin_mode = "fiducial"
            self.selected_fiducial = self.combo_fiducial.GetValue()

        self.reload_components()
        self.update_preview()
        self.status_text.SetLabel(f"Origin updated ({self.origin_mode.upper()}). Total {len(self.components)} components recalculated.")

    def on_fiducial_selected(self, event):
        self.selected_fiducial = self.combo_fiducial.GetValue()
        if self.rb_origin_fid.GetValue():
            self.on_origin_changed(event)

    def on_preset_changed(self, event):
        sel = self.combo_presets.GetSelection()
        if sel != -1:
            self.current_preset = dict(self.presets[sel])
            self.update_preview()
            self.update_template_info()

    def on_search_changed(self, event):
        self.update_preview()

    def update_preview(self):
        q = self.txt_search.GetValue().strip()
        self.grid_preview.update_data(self.components, self.current_preset, q)

    def update_template_info(self):
        desc = self.current_preset.get("description", "")
        cols = [c["header"] for c in self.current_preset.get("columns", [])]
        is_custom = self.current_preset.get("is_custom", False)
        
        info = f"Active Preset: {self.current_preset.get('name')}\n" \
               f"Description: {desc}\n" \
               f"Type: {'Custom User Profile' if is_custom else 'Built-in System Preset'}\n" \
               f"Columns: {', '.join(cols)}"
        self.lbl_preset_info.SetLabel(info)
        self.btn_delete_preset.Enable(is_custom)

    def on_open_template_editor(self, event):
        dlg = TemplateEditorDialog(self, self.current_preset)
        if dlg.ShowModal() == wx.ID_OK:
            self.current_preset = dlg.get_updated_preset()
            self.reload_presets()
            
            preset_names = [p["name"] for p in self.presets]
            self.combo_presets.SetItems(preset_names)
            
            for idx, p in enumerate(self.presets):
                if p.get("name") == self.current_preset.get("name"):
                    self.combo_presets.SetSelection(idx)
                    break

            self.update_preview()
            self.update_template_info()

    def on_delete_selected_preset(self, event):
        if not self.current_preset.get("is_custom", False):
            return
        
        name = self.current_preset.get("name")
        res = wx.MessageBox(f"Are you sure you want to delete the custom preset '{name}'?", "Confirm Preset Deletion", wx.YES_NO | wx.ICON_QUESTION)
        if res == wx.YES:
            PresetManager.delete_preset(self.current_preset.get("id"))
            self.reload_presets()
            
            preset_names = [p["name"] for p in self.presets]
            self.combo_presets.SetItems(preset_names)
            self.combo_presets.SetSelection(0)
            self.current_preset = dict(self.presets[0])
            
            self.update_preview()
            self.update_template_info()

    def on_export(self, event):
        out_dir = self.dir_picker.GetPath()
        if not out_dir or not os.path.exists(out_dir):
            wx.MessageBox("Please select a valid output directory.", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not any([self.chk_csv.GetValue(), self.chk_txt.GetValue(), self.chk_xlsx.GetValue(), self.chk_json.GetValue()]):
            wx.MessageBox("Please select at least one output format to generate.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        proj_name = self.txt_project_name.GetValue().strip() or "PCB_Project"
        rev_name = self.txt_revision.GetValue().strip() or "v1.0"
        
        prefix = f"{proj_name}_{rev_name}"
        safe_prefix = "".join(c for c in prefix if c.isalnum() or c in ('_', '-'))

        exported_files = []

        try:
            is_jlc = self.current_preset.get("is_jlcpcb", False) or "jlcpcb" in self.current_preset.get("id", "").lower()

            if is_jlc and (self.chk_csv.GetValue() or self.chk_xlsx.GetValue()):
                jlc_files = AssemblyExporter.export_jlcpcb_pair(
                    out_dir, safe_prefix, self.components,
                    format_csv=self.chk_csv.GetValue(),
                    format_xlsx=self.chk_xlsx.GetValue()
                )
                exported_files.extend(jlc_files)

                # TXT
                if self.chk_txt.GetValue():
                    p = os.path.join(out_dir, f"{safe_prefix}_CPL_JLCPCB.txt")
                    AssemblyExporter.export_to_tsv(p, self.components, self.current_preset)
                    exported_files.append(p)

                # JSON
                if self.chk_json.GetValue():
                    p = os.path.join(out_dir, f"{safe_prefix}_JLCPCB.json")
                    AssemblyExporter.export_to_json(p, self.components, self.current_preset)
                    exported_files.append(p)
            else:
                # 1. CSV
                if self.chk_csv.GetValue():
                    p = os.path.join(out_dir, f"{safe_prefix}_output.csv")
                    AssemblyExporter.export_to_csv(p, self.components, self.current_preset)
                    exported_files.append(p)

                # 2. TXT / TSV
                if self.chk_txt.GetValue():
                    p = os.path.join(out_dir, f"{safe_prefix}_output.txt")
                    AssemblyExporter.export_to_tsv(p, self.components, self.current_preset)
                    exported_files.append(p)

                # 3. XLSX
                if self.chk_xlsx.GetValue():
                    p = os.path.join(out_dir, f"{safe_prefix}_output.xlsx")
                    AssemblyExporter.export_to_excel(p, self.components, self.current_preset)
                    exported_files.append(p)

                # 4. JSON
                if self.chk_json.GetValue():
                    p = os.path.join(out_dir, f"{safe_prefix}_output.json")
                    AssemblyExporter.export_to_json(p, self.components, self.current_preset)
                    exported_files.append(p)

            # 5. ZIP Packaging
            if self.chk_zip.GetValue() and exported_files:
                zip_path = os.path.join(out_dir, f"{safe_prefix}_JLCPCB_Assembly_Package.zip" if is_jlc else f"{safe_prefix}_Assembly_Package.zip")
                ZipPackager.create_zip_package(zip_path, exported_files)

            files_str = "\n".join([f"• {os.path.basename(f)}" for f in exported_files])
            wx.MessageBox(f"All selected assembly files generated successfully!\n\nProject: {proj_name} ({rev_name})\n\nGenerated Files:\n{files_str}\n\nLocation:\n{out_dir}",
                            "Success", wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)

        except Exception as e:
            wx.MessageBox(f"An error occurred while generating files:\n{str(e)}", "Error", wx.OK | wx.ICON_ERROR)
