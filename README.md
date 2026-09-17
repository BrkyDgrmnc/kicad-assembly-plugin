# KiCad 10 Dizgi ve Montaj Eklentisi (Assembly & Fabrication Tool)

Bu eklenti, **KiCad 10** (ve KiCad 8/9 uyumlu) PCB Editor içerisinde çalışan, tek tıkla dizgi (SMD/THT Montaj) ve üretim dosyalarını (BOM, Pick & Place / CPL, ZIP Arşivi) oluşturan özelleştirilebilir bir Python eklentisidir.

---

## ✨ Özellikler

1. **Özelleştirilebilir Sütun & Format Şablon Motoru**:
   - İstenilen sütun isimleri ve birleşik şablonlar (Örn: `{Footprint}-{Value}` -> `RC1206-0R`).
   - Görseldeki özel firma formatı **varsayılan ön tanımlı profil** olarak dahil edilmiştir (`RefDes`, `PatternName`, `Type`, `ValUe`, `Layer`, `LocationX`, `LocationY`, `Rotation`, `smd value`).
2. **Dizgi Makineleri Profil Desteği (Pick & Place Machines)**:
   - **NeoDen** (YY1, NeoDen4, K1830)
   - **Charmhigh** (CHMT36VA, CHMT48VB)
   - **LitePlacer**
   - **JLCPCB / PCBWay**
3. **Kullanıcı Dostu Modern wxPython Arayüzü**:
   - Canlı renkli tablo önizlemesi (eksik LCSC/MPN değerleri soft sarı renk ile uyarılır).
   - Anlık arama ve filtreleme.
   - Sütun ekleme, silme, sıralama ve dinamik etiket tanımlama.
4. **Çıktı Formatları**:
   - `.csv`, Excel (`.xlsx`) ve tek tıkla `.zip` arşivleme.

---

## 🛠️ Kurulum

### Yöntem 1: Yerel / Manuel Kurulum (Hemen Kullanım)
1. Bu klasörü veya `.zip` arşivini indirin.
2. Klasörü KiCad eklenti dizinine kopyalayın:
   - **Windows**: `%APPDATA%\kicad\10.0\scripting\plugins\`
   - **Linux**: `~/.local/share/kicad/10.0/scripting/plugins/`
   - **macOS**: `~/Library/Preferences/kicad/10.0/scripting/plugins/`
3. KiCad PCB Editor'ü açın, üst araç çubuğundaki eklenti simgesine tıklayın.

### Yöntem 2: KiCad PCM (Plugin & Content Manager) Yüklemesi
1. KiCad PCM menüsünü açın.
2. *"Install from File..."* seçeneğini tıklayıp eklenti zip dosyasını yükleyin.

---

## 🌐 KiCad Mağazasında (PCM) Yayınlama Rehberi

Eklentinizi resmi KiCad PCM mağazasına göndermek için:
1. Bu depoyu GitHub üzerinde yayınlayın ve bir Release (Örn: `v1.0.0`) oluşturun.
2. `.zip` dosyasının indirme bağlantısını ve `SHA-256` özeti ile `metadata.json` dosyanızı hazırlayın.
3. [kicad-addons](https://gitlab.com/kicad/code/kicad-addons) resmi deposuna bir Pull Request gönderin.

---

## 🧪 Bağımsız Test Etme (KiCad Dışında)

KiCad olmadan arayüzü ve dışa aktarıcıyı test etmek için:

```bash
python run_standalone_test.py
```

---

## 📜 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır.
