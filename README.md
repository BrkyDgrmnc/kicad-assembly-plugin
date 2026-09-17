# KiCad 10 Assembly & Fabrication Tool

A customizable Python action plugin for **KiCad 10** (also compatible with KiCad 8 & 9) that generates assembly files (BOM, Pick & Place / CPL, and ZIP packages) with dynamic vendor column templates and Pick & Place machine presets.

---

## ✨ Key Features

1. **Customizable Column & Format Template Engine**:
   - Define custom column headers and dynamic tag expressions (e.g. `{Footprint}-{Value}` -> `RC1206-0R`).
   - Default custom vendor format (`RefDes`, `PatternName`, `Type`, `ValUe`, `Layer`, `LocationX`, `LocationY`, `Rotation`, `smd value`).
2. **Pick & Place Machine & Service Presets**:
   - **NeoDen** (YY1, NeoDen4, K1830)
   - **Charmhigh** (CHMT36VA, CHMT48VB)
   - **LitePlacer**
   - **JLCPCB / PCBWay**
3. **Fiducial & Origin Alignment Modes**:
   - **Auxiliary Origin**: Uses KiCad auxiliary axis origin.
   - **Absolute Origin**: Uses board top-left sheet origin (0,0).
   - **Fiducial (0,0)**: Align coordinates relative to a chosen PCB Fiducial component (e.g., FID1).
4. **Interactive High-Contrast User Interface**:
   - Dark Mode compliant grid with soft warning highlights for missing LCSC/MPN data.
   - Live search & filter bar by RefDes, Value, Footprint, or LCSC/MPN.
   - Rich interactive tooltips on all UI options.
5. **Multi-Format Export**:
   - Native `.xlsx` (without external dependencies), `.csv`, `.txt`, `.json`, and single-click `.zip` package.

---

## 🛠️ Installation

### Method 1: Local / Manual Installation
1. Clone or download this repository.
2. Copy the plugin folder to your KiCad plugins directory:
   - **Windows**: `%APPDATA%\kicad\10.0\scripting\plugins\`
   - **Linux**: `~/.local/share/kicad/10.0/scripting/plugins/`
   - **macOS**: `~/Library/Preferences/kicad/10.0/scripting/plugins/`
3. Open KiCad PCB Editor and click the plugin icon on the top toolbar.

### Method 2: KiCad Plugin & Content Manager (PCM)
1. Open KiCad PCM.
2. Click **Install from File...** and select the plugin zip archive.

---

## 🧪 Standalone Testing (Outside KiCad)

To test the GUI and exporter without opening KiCad:

```bash
python run_standalone_test.py
```

---

## 📜 License

This project is licensed under the **MIT License**.
