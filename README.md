# 🟢 BrodGSI Tool v3.0 (Matrix Edition)

[![Telegram](https://img.shields.io/badge/Telegram-BrodGSIUpdates-00FF41?style=for-the-badge&logo=telegram)](https://t.me/BrodGSIUpdates)
[![SourceForge](https://img.shields.io/badge/SourceForge-Downloads-00FF41?style=for-the-badge&logo=sourceforge)](https://sourceforge.net/projects/brodgsi/files/)

> 🌍 **Language / Язык:** [English](README.md) | [Русский](README_RU.md)

**BrodGSI Tool** is an automated, cross-platform kitchen for building bootable Project Treble Generic System Images (GSI) from stock OEM firmwares (Xiaomi, Samsung OneUI, Pixel, OnePlus, Vivo, Realme, etc.). It unites patch engines and scripts from **MysticGSI**, **yaebuebugsitool**, **ErfanGSIs**, and **OriginGSITool** under a single Matrix-styled CLI and supports headless cloud building via GitHub Actions with direct upload to SourceForge.

---

## ⚡ Key Features

* **Matrix CLI Theme:** Complete hacker-green terminal design powered by `rich` and `questionary`.
* **Smart Hardware & ROM Heuristic Analyzer:** Automatically reads `build.prop` from `system`, `vendor`, and `product` to detect OEM skin, Android SDK, chipset (`ro.board.platform`), and device codename (`ro.product.device`) to calculate the highest-scoring patch set.
* **Samsung OneUI KnoxPatch Engine:** Automatically decompiles `services.jar`, patches `SystemServer.smali` around `StartKnoxGuard` (removes `move-result` above it and replaces conditional `if-*` with unconditional `goto`), and recompiles on the fly.
* **Recursive Container Unpacker:** Supports `.zip`, `.tgz`, `payload.bin`, `super.img`, `.new.dat.br`, `UPDATE.APP`, `AP.tar.md5`, `EROFS`, `EXT4`, and `F2FS`.
* **Sparse Git Sync:** Uses `git sparse-checkout` to fetch only essential patch folders in seconds without downloading gigabytes of bloat.
* **Auto-Compression:** Compresses final images into Ultra LZMA2 `.7z` archives and deletes raw `.img` files to save disk space.

---

## ☁️ How to Build GSI in the Cloud (GitHub Actions + SourceForge)

You can build GSIs directly on GitHub's servers and automatically upload them to SourceForge without using your PC's bandwidth or disk space:

1. **Fork or Push** this repository to your GitHub account.
2. **Configure SourceForge Secrets:**
   * Go to your repository on GitHub ➔ **Settings** ➔ **Secrets and variables** ➔ **Actions**.
   * Click **New repository secret** and add two secrets:
     * `SF_USERNAME` — Your SourceForge account username.
     * `SF_PASSWORD` — Your SourceForge account password.
3. **Run the Workflow:**
   * Open the **Actions** tab in your GitHub repository.
   * Select **BrodGSI Cloud Builder & SourceForge Uploader** on the left.
   * Click **Run workflow** on the right and fill in the parameters:
     * **Direct URL to Firmware:** Paste a direct link to any stock ROM (`.zip` / `.tgz`).
     * **Output Filesystem Type:** Choose `ext4`, `erofs`, or `both`.
     * **Apply OEM Debloat Lists:** Leave checked (`true`) to remove bloatware.
     * **Target subfolder on SourceForge:** Specify the destination folder name (e.g., `GooglePixel3_Android9`).
   * Click the green **Run workflow** button. Once finished, the compressed `.7z` GSI will appear directly in your SourceForge files!

---

## 🛠 Requirements & Binaries (Local Build)

The project uses a cross-platform `bin/` directory structure.

### For Windows (amd64) Users:
Ready to work **out-of-the-box**. All required `.exe` binaries (`7z`, `mke2fs`, `simg2img`, `lpunpack`, `payload-dumper-go`, etc.) are pre-included in `bin/windows_amd64/`.
* **Note:** You must install **Java (JRE/JDK 11+)** on your system to use Smali patching (`apktool` for Samsung KnoxPatch).

### For Linux & macOS Users:
Only `windows_amd64` binaries are fully bundled in the repo (**except `payload-dumper-go`**, which is pre-placed in all platform folders). You must install the remaining tools via your package manager:

**Debian / Ubuntu / Mint:**
```bash
sudo apt update
sudo apt install git python3-pip p7zip-full android-sdk-libsparse-utils erofs-utils e2fsprogs patch default-jre apktool
```

**Arch Linux / Manjaro:**
```sudo pacman -S git python-pip p7zip android-tools erofs-utils e2fsprogs patch jre-openjdk android-apktool```

## 🚀 Quick Start (Local)
```
git clone [https://github.com/BrodGSI/BrodGSI_Tool.git](https://github.com/BrodGSI/BrodGSI_Tool.git)
cd BrodGSI_Tool
pip install -r requirements.txt
python brodgsi.py
```

## 💻 Running the tool

# Linux and MacOS:
```
python3 brodgsi.py
```

# Windows:
```
python brodgsi.py
```

## 🔗 Official Links
[📢 Telegram Channel (Releases & Updates)](https://t.me/BrodGSIUpdates)
[📦 SourceForge Mirror (Download GSIs)](https://sourceforge.net/projects/brodgsi/files)
