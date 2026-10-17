# 🛠 BrodGSI Tool

**BrodGSI Tool** is a cross-platform, rootless Automated Generic System Image (GSI) builder with a TUI interface. It combines the patch databases and porting methodologies from four major GSI projects into a single Python engine.

**BrodGSI Tool** — это кроссплатформенный инструмент для автоматической сборки бутабельных GSI-образов с псевдографическим TUI-интерфейсом, объединяющий наработки четырёх крупнейших GSI-проектов.

---

## ✨ Features / Возможности

* **🌍 Cross-Platform & Multi-Arch:** Runs natively on **Windows, Linux, and macOS** (`x86_64` / `amd64` and `arm64` / `aarch64`) without requiring `sudo mount` (rootless extraction & repacking).
* **📦 Universal Container Extractor:** Automatically detects file signatures (Magic Bytes) regardless of file name. Supports:
  * `.zip`, `.tgz`, `.tar.gz`, `.tar`, `.7z`, `.lz4`
  * `payload.bin`, `super.img` (raw & sparse), `system.new.dat.br`, `system.new.dat`
  * Huawei `UPDATE.APP`, Samsung `AP.tar.md5` (`.img.lz4`), Xiaomi `fastboot_images.tgz`
  * Filesystems: **EXT4**, **EROFS**, **F2FS**
* **🔍 Smart Auto-Detection & Patch Scoring:**
  * Automatically detects the Android Version, SDK level, and OEM ROM skin (`HyperOS`, `MIUI`, `OneUI`, `ColorOS`, `OxygenOS`, `RealmeUI`, `MagicOS`, `OriginOS`, `Flyme`, `Pixel`, etc.) by scanning `build.prop` and partition trees.
  * **Auto-Select Mode:** Calculates a modification score (files + script lines + smali patches) across all repositories and automatically picks the most comprehensive patch set.
  * **Manual Mode:** Lets you choose between available patch variants if multiple exist.
  * **Generic Fallback:** Automatically falls back to universal PHH-Treble Generic patches if no OEM-specific patch exists.
* **🌐 Bilingual TUI:** Full support for **Russian (RU)** and **English (EN)**.

---

## 🤝 Integrated Patch Databases / Интегрированные проекты

BrodGSI automatically clones, updates, and interprets patches from:
1. [MysticGSI/mysticgsi](https://github.com/MysticGSI/mysticgsi)
2. [radgoodnow/yaebuebugsitool](https://github.com/radgoodnow/yaebuebugsitool)
3. [erfanoabdi/ErfanGSIs](https://github.com/erfanoabdi/ErfanGSIs)
4. [defnotegor/OriginGSITool](https://github.com/defnotegor/OriginGSITool)

---

# 🚀 Quick Start / Быстрый старт

## 1. Install Dependencies / Установка зависимостей
```bash
git clone [https://github.com/BrodGSI/BrodGSI_Tool.git](https://github.com/BrodGSI/BrodGSI_tool.git)
cd BrodGSI
pip install -r requirements.txt
```

## 2. Install System Tools / Системные утилиты

## Linux (Arch / Ubuntu / Debian):
### Ubuntu / Debian
    ```sudo apt install git p7zip-full android-sdk-libsparse-utils erofs-utils e2fsprogs```
### Arch Linux
    ```sudo pacman -S git p7zip android-tools erofs-utils e2fsprogs```
### macOS:
    ```brew install git sevenzip erofs-utils e2fsprogs```
### Windows:
	Place binaries (`7z.exe`, `lpunpack.exe`, `payload-dumper-go.exe`, `mke2fs.exe`, `e2fsdroid.exe`, `mkfs.erofs.exe`) into `bin/windows_amd64/`.
	
# 3. Run / Запуск
## Linux and MacOS:
```
python3 brodgsi.py
```
## Windows:
```
python brodgsi.py
```
