"""
KiCad 10 Dizgi ve Montaj Eklentisi - Canlı Önizleme Tablosu Bileşeni
"""

import wx
import wx.grid
from typing import List, Dict, Any
from plugin.core.template_engine import TemplateEngine

class PreviewGridTable(wx.grid.Grid):
    """
    Canlı dizgi verilerini yüksek kontrastlı, kristal netliğinde renkli vurgulama ile gösteren wx Grid tablosu.
    Koyu Tema (Dark Mode) dahil mükemmel görünürlük sağlar.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.CreateGrid(0, 0)
        self.EnableEditing(False)
        self.SetRowLabelSize(40)
        self.SetColLabelSize(30)
        self.SetGridLineColour(wx.Colour(200, 210, 225))

        # Yüksek kontrastlı başlık görünümü
        self.SetLabelBackgroundColour(wx.Colour(30, 41, 59)) # Dark Slate (#1E293B)
        self.SetLabelTextColour(wx.Colour(255, 255, 255))     # Pure White

        # Yüksek kontrastlı yazı tipi
        font = self.GetFont()
        font.SetPointSize(9)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.SetLabelFont(font)

    def update_data(self, components: List[Dict[str, Any]], preset: Dict[str, Any], search_filter: str = ""):
        """
        Preset ve bileşen listesine göre tabloyu yeniden doldurur.
        """
        columns = preset.get("columns", [])
        resolved_rows = TemplateEngine.process_components(components, columns)

        if search_filter:
            q = search_filter.lower()
            filtered_rows = []
            for r in resolved_rows:
                if any(q in str(val).lower() for val in r.values()):
                    filtered_rows.append(r)
            resolved_rows = filtered_rows

        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0:
            self.DeleteCols(0, self.GetNumberCols())

        if not columns:
            return

        headers = [col.get("header", "Column") for col in columns]
        self.AppendCols(len(headers))
        for idx, h in enumerate(headers):
            self.SetColLabelValue(idx, h)

        self.AppendRows(len(resolved_rows))

        # Yüksek Kontrastlı Renk Paleti (Koyu Temada Asla Silik Görünmez)
        even_bg = wx.Colour(255, 255, 255)
        odd_bg = wx.Colour(241, 245, 249)      # Açık Mavi-Gri (#F1F5F9)
        dark_text_fg = wx.Colour(15, 23, 42)    # Derin Lacivert/Siyah (#0F172A)
        
        warning_bg = wx.Colour(254, 243, 199)   # Yumuşak Amber Sarı (#FEF3C7)
        warning_fg = wx.Colour(146, 64, 14)     # Koyu Kahve-Amber (#92400E)

        cell_font = self.GetFont()
        cell_font.SetPointSize(9)
        cell_font.SetWeight(wx.FONTWEIGHT_MEDIUM)

        for row_idx, row_data in enumerate(resolved_rows):
            is_odd = (row_idx % 2 != 0)
            base_bg = odd_bg if is_odd else even_bg

            for col_idx, h in enumerate(headers):
                val = str(row_data.get(h, ""))
                self.SetCellValue(row_idx, col_idx, val)

                # Eksik alan uyarısı
                if not val.strip() or (val.startswith("{") and val.endswith("}")):
                    self.SetCellBackgroundColour(row_idx, col_idx, warning_bg)
                    self.SetCellTextColour(row_idx, col_idx, warning_fg)
                else:
                    self.SetCellBackgroundColour(row_idx, col_idx, base_bg)
                    self.SetCellTextColour(row_idx, col_idx, dark_text_fg)

                self.SetCellFont(row_idx, col_idx, cell_font)

        self.AutoSizeColumns()
        self.Refresh()
