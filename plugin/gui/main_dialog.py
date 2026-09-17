"""
KiCad 10 Dizgi ve Montaj Eklentisi - Ana wxPython Arayüz Dialogu
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
    KiCad 10 Dizgi ve Montaj Eklentisinin kullanıcı dostu ana sekmeli arayüzü.
    """

    def __init__(self, parent=None, board=None):
        super().__init__(parent, title=f"{APP_NAME} - v{APP_VERSION}", size=(960, 700),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

        self.board = board
        self.origin_mode = "aux"
        self.selected_fiducial = ""
        self.custom_offsets = dict(DEFAULT_ROTATION_OFFSETS)

        # Proje Adı ve Revizyon No
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

        # Tab 1: Ana Önizleme ve Üretim
        self.tab_preview = wx.Panel(self.notebook)
        self.setup_tab_preview()
        self.notebook.AddPage(self.tab_preview, "📊 Dizgi Çıktısı & Önizleme")

        # Tab 2: Şablon & Sütun Yapılandırması
        self.tab_template = wx.Panel(self.notebook)
        self.setup_tab_template()
        self.notebook.AddPage(self.tab_template, "🛠️ Şablon & Özel Profil Yöneticisi")

        # Tab 3: Makine & Dönüş Açıları / Orijin Seçimi
        self.tab_settings = wx.Panel(self.notebook)
        self.setup_tab_settings()
        self.notebook.AddPage(self.tab_settings, "⚙️ Açı & Makine Ayarları")

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 8)

        # Alt Bar
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.status_text = wx.StaticText(self, label=f"Toplam {len(self.components)} adet montaj bileşeni yüklendi.")
        self.status_text.SetForegroundColour(wx.Colour(180, 200, 220))
        bottom_sizer.Add(self.status_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        bottom_sizer.AddStretchSpacer()
        
        btn_close = wx.Button(self, wx.ID_CANCEL, "Kapat")
        self.btn_export = wx.Button(self, wx.ID_OK, "🚀 Dizgi Dosyalarını Üret")
        self.btn_export.SetBackgroundColour(wx.Colour(0, 120, 215))
        self.btn_export.SetForegroundColour(wx.WHITE)
        font = self.btn_export.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.btn_export.SetFont(font)

        bottom_sizer.Add(btn_close, 0, wx.RIGHT, 8)
        bottom_sizer.Add(self.btn_export, 0, wx.RIGHT, 10)

        main_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.SetSizer(main_sizer)

        self.btn_export.Bind(wx.EVT_BUTTON, self.on_export)
        self.update_preview()

    def setup_tab_preview(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Proje Adı, Revizyon & Format Seçimi
        top_box = wx.StaticBox(self.tab_preview, label="Proje Bilgileri ve Dizgi Formatı")
        top_sizer = wx.StaticBoxSizer(top_box, wx.HORIZONTAL)

        top_sizer.Add(wx.StaticText(self.tab_preview, label="Proje Adı:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        self.txt_project_name = wx.TextCtrl(self.tab_preview, value=self.project_name, size=(140, -1))
        top_sizer.Add(self.txt_project_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        top_sizer.Add(wx.StaticText(self.tab_preview, label="Revizyon No:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        self.txt_revision = wx.TextCtrl(self.tab_preview, value=self.revision, size=(70, -1))
        top_sizer.Add(self.txt_revision, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        top_sizer.Add(wx.StaticText(self.tab_preview, label="Profil:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        preset_names = [p["name"] for p in self.presets]
        self.combo_presets = wx.ComboBox(self.tab_preview, choices=preset_names, style=wx.CB_READONLY)
        self.combo_presets.SetSelection(0)
        top_sizer.Add(self.combo_presets, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        top_sizer.Add(wx.StaticText(self.tab_preview, label="🔍 Arama:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        self.txt_search = wx.TextCtrl(self.tab_preview, style=wx.TE_PROCESS_ENTER, size=(120, -1))
        top_sizer.Add(self.txt_search, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # Tablo
        self.grid_preview = PreviewGridTable(self.tab_preview)
        sizer.Add(self.grid_preview, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Formatlar ve Çıktı Dizini
        out_box = wx.StaticBox(self.tab_preview, label="Çıktı Formatları ve Kaydetme Seçenekleri")
        out_sizer = wx.StaticBoxSizer(out_box, wx.VERTICAL)

        fmt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fmt_sizer.Add(wx.StaticText(self.tab_preview, label="Üretilecek Formatlar:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.chk_csv = wx.CheckBox(self.tab_preview, label="CSV (.csv)")
        self.chk_csv.SetValue(True)
        self.chk_txt = wx.CheckBox(self.tab_preview, label="Metin (.txt)")
        self.chk_txt.SetValue(True)
        self.chk_xlsx = wx.CheckBox(self.tab_preview, label="Excel (.xlsx)")
        self.chk_xlsx.SetValue(True)
        self.chk_json = wx.CheckBox(self.tab_preview, label="JSON (.json)")
        self.chk_json.SetValue(False)

        fmt_sizer.Add(self.chk_csv, 0, wx.RIGHT, 15)
        fmt_sizer.Add(self.chk_txt, 0, wx.RIGHT, 15)
        fmt_sizer.Add(self.chk_xlsx, 0, wx.RIGHT, 15)
        fmt_sizer.Add(self.chk_json, 0)

        out_sizer.Add(fmt_sizer, 0, wx.EXPAND | wx.ALL, 6)

        dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dir_sizer.Add(wx.StaticText(self.tab_preview, label="Kaydetme Dizini:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        default_dir = os.path.expanduser("~/Desktop")
        self.dir_picker = wx.DirPickerCtrl(self.tab_preview, path=default_dir)
        dir_sizer.Add(self.dir_picker, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        self.chk_zip = wx.CheckBox(self.tab_preview, label="Tümünü ZIP Arşivi Yap (.zip)")
        self.chk_zip.SetValue(True)
        dir_sizer.Add(self.chk_zip, 0, wx.ALIGN_CENTER_VERTICAL)

        out_sizer.Add(dir_sizer, 0, wx.EXPAND | wx.ALL, 6)

        sizer.Add(out_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.tab_preview.SetSizer(sizer)

        self.combo_presets.Bind(wx.EVT_COMBOBOX, self.on_preset_changed)
        self.txt_search.Bind(wx.EVT_TEXT, self.on_search_changed)

    def setup_tab_template(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        info_box = wx.StaticBox(self.tab_template, label="Özel Profil & Şablon Düzenleme Merkezi")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)

        self.lbl_preset_info = wx.StaticText(self.tab_template, label="")
        info_sizer.Add(self.lbl_preset_info, 0, wx.ALL, 10)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_edit_template = wx.Button(self.tab_template, label="⚙️ Sütun Yapısını Düzenle ve İsimle Kaydet...")
        self.btn_delete_preset = wx.Button(self.tab_template, label="🗑️ Seçili Profili Sil")
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
        
        box_origin = wx.StaticBox(self.tab_settings, label="Orijin ve Koordinat Referansı Ayarları (0,0 Noktası)")
        origin_sizer = wx.StaticBoxSizer(box_origin, wx.VERTICAL)

        self.rb_origin_aux = wx.RadioButton(self.tab_settings, label="Yardımcı Orijin (Auxiliary / User Origin)", style=wx.RB_GROUP)
        self.rb_origin_abs = wx.RadioButton(self.tab_settings, label="Mutlak Kart Orijini (Absolute Board Origin 0,0)")
        
        fid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rb_origin_fid = wx.RadioButton(self.tab_settings, label="Seçilen Fiducial Bileşeni (Seçilen Fiducial = 0,0):")
        
        self.combo_fiducial = wx.ComboBox(self.tab_settings, choices=self.fiducials, style=wx.CB_READONLY)
        if self.fiducials:
            self.combo_fiducial.SetSelection(0)
            self.selected_fiducial = self.fiducials[0]

        fid_sizer.Add(self.rb_origin_fid, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        fid_sizer.Add(self.combo_fiducial, 0, wx.ALIGN_CENTER_VERTICAL)

        origin_sizer.Add(self.rb_origin_aux, 0, wx.ALL, 6)
        origin_sizer.Add(self.rb_origin_abs, 0, wx.ALL, 6)
        origin_sizer.Add(fid_sizer, 0, wx.ALL, 6)

        sizer.Add(origin_sizer, 0, wx.EXPAND | wx.ALL, 10)

        box_rot = wx.StaticBox(self.tab_settings, label="Standart Kılıf Dönüş Açı (Rotation Offset) Kuralları")
        rot_sizer = wx.StaticBoxSizer(box_rot, wx.VERTICAL)

        self.list_offsets = wx.ListCtrl(self.tab_settings, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, size=(-1, 180))
        self.list_offsets.InsertColumn(0, "Footprint Kılıf Adı / Kalıbı", width=300)
        self.list_offsets.InsertColumn(1, "Dönüş Açı Düzeltmesi (Offset Degree)", width=220)
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
        self.status_text.SetLabel(f"Orijin güncellendi ({self.origin_mode.upper()}). Toplam {len(self.components)} bileşen yeniden hesaplandı.")

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
        
        info = f"Aktif Profil: {self.current_preset.get('name')}\n" \
               f"Açıklama: {desc}\n" \
               f"Tür: {'Özel Kullanıcı Profili' if is_custom else 'Sistem Hazır Profili'}\n" \
               f"Mevcut Sütunlar: {', '.join(cols)}"
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
        res = wx.MessageBox(f"'{name}' isimli özel profili silmek istediğinize emin misiniz?", "Profil Silme Onayı", wx.YES_NO | wx.ICON_QUESTION)
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
            wx.MessageBox("Lütfen geçerli bir çıktı dizini seçin.", "Hata", wx.OK | wx.ICON_ERROR)
            return

        if not any([self.chk_csv.GetValue(), self.chk_txt.GetValue(), self.chk_xlsx.GetValue(), self.chk_json.GetValue()]):
            wx.MessageBox("Lütfen üretmek istediğiniz en az bir çıktı formatını işaretleyin.", "Hata", wx.OK | wx.ICON_WARNING)
            return

        proj_name = self.txt_project_name.GetValue().strip() or "PCB_Project"
        rev_name = self.txt_revision.GetValue().strip() or "v1.0"
        
        prefix = f"{proj_name}_{rev_name}"
        safe_prefix = "".join(c for c in prefix if c.isalnum() or c in ('_', '-'))

        exported_files = []

        try:
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

            # 5. ZIP Paketleme
            if self.chk_zip.GetValue() and exported_files:
                zip_path = os.path.join(out_dir, f"{safe_prefix}_Assembly_Package.zip")
                ZipPackager.create_zip_package(zip_path, exported_files)

            files_str = "\n".join([f"• {os.path.basename(f)}" for f in exported_files])
            wx.MessageBox(f"Seçilen tüm dizgi dosyaları başarıyla üretildi!\n\nProje: {proj_name} ({rev_name})\n\nÜretilen Dosyalar:\n{files_str}\n\nKonum:\n{out_dir}",
                            "Başarılı", wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)

        except Exception as e:
            wx.MessageBox(f"Dosyalar üretilirken bir hata oluştu:\n{str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
