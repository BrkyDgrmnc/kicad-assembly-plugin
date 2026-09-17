"""
KiCad 10 Dizgi ve Montaj Eklentisi - Sütun ve Şablon Düzenleyici Penceresi
"""

import wx
from typing import Dict, Any, List
from plugin.core.preset_manager import PresetManager

class TemplateEditorDialog(wx.Dialog):
    """
    Kullanıcının sütun başlıklarını, sıralamasını ve dinamik formatlarını ({Footprint}-{Value} vb.)
    düzenlemesini ve özel isim vererek kaydetmesini sağlayan wx.Dialog penceresi.
    """

    def __init__(self, parent, current_preset: Dict[str, Any]):
        super().__init__(parent, title="Sütun ve Format Şablon Düzenleyici", size=(780, 580),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.preset = dict(current_preset)
        self.columns = [dict(c) for c in self.preset.get("columns", [])]

        self.init_ui()
        self.Centre()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Üst Açıklama
        header_box = wx.StaticBox(self, label="Dinamik Şablon Motoru Rehberi")
        header_sizer = wx.StaticBoxSizer(header_box, wx.VERTICAL)
        help_lbl = wx.StaticText(self, label=(
            "Etiket Kullanımı: Sütun şablonlarında {Reference}, {Footprint}, {Value}, {Layer}, {X}, {Y}, {Rotation}, {LCSC}, {MPN} kullanabilirsiniz.\n"
            "Örnek Birleşik Şablon: '{Footprint}-{Value}' -> 'RC1206-0R' üretir."
        ))
        help_lbl.SetForegroundColour(wx.Colour(0, 102, 204))
        header_sizer.Add(help_lbl, 0, wx.ALL, 8)
        main_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Sütun Listesi ve Butonlar
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Sütun Başlığı (Header)", width=220)
        self.list_ctrl.InsertColumn(1, "Şablon İfadesi (Template)", width=370)
        content_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.RIGHT, 10)

        # Yan Butonlar
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_add = wx.Button(self, label="➕ Yeni Sütun Ekle")
        self.btn_edit = wx.Button(self, label="✏️ Sütunu Düzenle")
        self.btn_delete = wx.Button(self, label="🗑️ Sütunu Sil")
        self.btn_up = wx.Button(self, label="⬆️ Yukarı Taşı")
        self.btn_down = wx.Button(self, label="⬇️ Aşağı Taşı")

        btn_sizer.Add(self.btn_add, 0, wx.EXPAND | wx.BOTTOM, 6)
        btn_sizer.Add(self.btn_edit, 0, wx.EXPAND | wx.BOTTOM, 6)
        btn_sizer.Add(self.btn_delete, 0, wx.EXPAND | wx.BOTTOM, 16)
        btn_sizer.Add(self.btn_up, 0, wx.EXPAND | wx.BOTTOM, 6)
        btn_sizer.Add(self.btn_down, 0, wx.EXPAND | wx.BOTTOM, 6)

        content_sizer.Add(btn_sizer, 0, wx.ALIGN_TOP)
        main_sizer.Add(content_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Alt Butonlar (İptal / İsimle Kaydet / Şablonu Uygula)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_save_as = wx.Button(self, label="💾 Farklı Kaydet (Profil Adı)...")
        self.btn_save_as.SetBackgroundColour(wx.Colour(234, 246, 255))
        bottom_sizer.Add(self.btn_save_as, 0, wx.LEFT, 10)

        bottom_sizer.AddStretchSpacer()
        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, label="İptal")
        self.btn_save = wx.Button(self, wx.ID_OK, label="✓ Şablonu Uygula")

        bottom_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 8)
        bottom_sizer.Add(self.btn_save, 0, wx.RIGHT, 10)
        main_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)

        # Olay Bağlantıları
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
        dlg = ColumnEditDialog(self, "Yeni Sütun Ekle", "", "{Value}")
        if dlg.ShowModal() == wx.ID_OK:
            header, template = dlg.get_values()
            if header:
                self.columns.append({"header": header, "template": template})
                self.refresh_list()

    def on_edit_col(self, event):
        sel = self.list_ctrl.GetFirstSelected()
        if sel == -1:
            wx.MessageBox("Lütfen düzenlemek için bir sütun seçin.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
            return
        col = self.columns[sel]
        dlg = ColumnEditDialog(self, "Sütunu Düzenle", col.get("header", ""), col.get("template", ""))
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
        dlg = wx.TextEntryDialog(self, "Lütfen yeni profil için bir isim girin:\n(Örn: Ahmet Elektronik NeoDen YY1 Formatı)", "Özel Profili Kaydet")
        if dlg.ShowModal() == wx.ID_OK:
            preset_name = dlg.GetValue().strip()
            if preset_name:
                saved = PresetManager.save_new_preset(preset_name, f"Kullanıcı Profili: {preset_name}", self.columns)
                self.preset = saved
                wx.MessageBox(f"'{preset_name}' profili başarıyla kaydedildi!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
                self.EndModal(wx.ID_OK)

    def get_updated_preset(self) -> Dict[str, Any]:
        self.preset["columns"] = self.columns
        return self.preset


class ColumnEditDialog(wx.Dialog):
    def __init__(self, parent, title, header="", template=""):
        super().__init__(parent, title=title, size=(450, 220))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 2, 10, 10)
        grid.AddGrowableCol(1, 1)

        grid.Add(wx.StaticText(self, label="Sütun Başlığı:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_header = wx.TextCtrl(self, value=header)
        grid.Add(self.txt_header, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self, label="Şablon İfadesi:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_template = wx.TextCtrl(self, value=template)
        grid.Add(self.txt_template, 1, wx.EXPAND)

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 15)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(wx.Button(self, wx.ID_CANCEL, "İptal"), 0, wx.RIGHT, 8)
        btn_sizer.Add(wx.Button(self, wx.ID_OK, "Tamam"), 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Centre()

    def get_values(self):
        return self.txt_header.GetValue().strip(), self.txt_template.GetValue().strip()
