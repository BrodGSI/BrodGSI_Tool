# 🟢 BrodGSI Tool v3.0 (Matrix Edition)

[![Telegram](https://img.shields.io/badge/Telegram-BrodGSIUpdates-00FF41?style=for-the-badge&logo=telegram)](https://t.me/BrodGSIUpdates)
[![SourceForge](https://img.shields.io/badge/SourceForge-Downloads-00FF41?style=for-the-badge&logo=sourceforge)](https://sourceforge.net/projects/brodgsi/files/)

> 🌍 **Language / Язык:** [English](README.md) | [Русский](README_RU.md)

**BrodGSI Tool** — это кроссплатформенный автоматизированный сборщик бутабельных GSI-образов (Project Treble) из любых стоковых прошивок (Xiaomi, Samsung OneUI, Pixel, OnePlus, Vivo, Realme и др.). Инструмент объединяет базы патчей четырёх проектов (**MysticGSI**, **yaebuebugsitool**, **ErfanGSIs**, **OriginGSITool**) в едином матричном интерфейсе и поддерживает облачную сборку через GitHub Actions с прямой выгрузкой на SourceForge.

---

## ⚡ Основные возможности

* **Матричный стиль (Matrix Green UI):** Полностью зелёная цветовая схема терминала на базе `rich` и `questionary`.
* **Умный автовыбор патчей (Smart Heuristics):** Скрипт анализирует `build.prop` из `system`, `vendor` и `product`, определяет оболочку (OneUI, HyperOS, OriginOS и т.д.), версию Android, кодовое имя телефона (`ro.product.device`) и процессор (`ro.board.platform`), автоматически подбирая наиболее подходящие патчи.
* **Специальный патчер для OneUI (KnoxPatch):** Автоматическая декомпиляция `services.jar` через `apktool`, модификация `SystemServer.smali` на участке `StartKnoxGuard` (удаление `move-result` выше вызова и замена условного перехода `if-*` на безусловный `goto`) и обратная сборка.
* **Всеядный распаковщик:** Рекурсивная распаковка `.zip`, `.tgz`, `payload.bin`, `super.img`, `.new.dat.br`, `UPDATE.APP`, `AP.tar.md5`, `EROFS`, `EXT4` и `F2FS`.
* **Быстрая синхронизация баз (Sparse Checkout):** Скачивает из репозиториев только папки с патчами за считанные секунды.
* **Автосжатие в 7z:** Готовые образы автоматически сжимаются в `.7z` (Ultra LZMA2), а исходный `.img` удаляется для экономии места на диске.

---

## ☁️ Как пользоваться облачной сборкой (GitHub Actions + SourceForge)

Вы можете собирать GSI прямо на серверах GitHub с автоматической загрузкой готового архива на SourceForge без нагрузки на свой ПК:

1. **Настройте секреты SourceForge в репозитории GitHub:**
   * Откройте ваш репозиторий на GitHub ➔ перейдите во вкладку **Settings** ➔ в меню слева выберите **Secrets and variables** ➔ **Actions**.
   * Нажмите кнопку **New repository secret** и добавьте два секрета:
     * `SF_USERNAME` — ваш логин (никнейм) на SourceForge.
     * `SF_PASSWORD` — ваш пароль от аккаунта SourceForge.
2. **Запустите сборку (Workflow):**
   * Перейдите во вкладку **Actions** в вашем репозитории GitHub.
   * Слева выберите **BrodGSI Cloud Builder & SourceForge Uploader**.
   * Нажмите кнопку **Run workflow** справа и заполните поля:
     * **Direct URL to Firmware:** вставьте прямую ссылку на скачивание прошивки (`.zip` / `.tgz`).
     * **Output Filesystem Type:** выберите `ext4`, `erofs` или `both`.
     * **Apply OEM Debloat Lists:** оставьте галочку (`true`), чтобы удалить мусорные приложения.
     * **Target subfolder on SourceForge:** укажите имя папки на SourceForge, куда загрузится готовый образ (например, `GooglePixel3_Android9`).
   * Нажмите зеленую кнопку **Run workflow**. По окончании процесса сжатый `.7z` архив автоматически появится в вашем проекте на SourceForge без лимита в 500 МБ!

---

## 🛠 Требования и бинарники (Локальный запуск)

В проекте настроена кроссплатформенная структура папок `bin/`.

### Для пользователей Windows (amd64):
Тулка работает **«из коробки»**. Все необходимые бинарники (`7z`, `mke2fs`, `simg2img`, `lpunpack` и др.) уже включены в папку `bin/windows_amd64/`.
* **Важно:** Для работы Smali-патчера (KnoxPatch на прошивках Samsung) необходимо установить в систему **Java (JRE/JDK 11+)**.

### Для пользователей Linux и macOS:
В тулку включены все бинарники **только для `windows_amd64`** (за исключением `payload-dumper-go` — он единственный бинарник, который положен во все папки платформ). Все остальные утилиты под Linux необходимо установить отдельно через пакетный менеджер:

**Debian / Ubuntu / Mint:**
```bash
sudo apt update
sudo apt install git python3-pip p7zip-full android-sdk-libsparse-utils erofs-utils e2fsprogs patch default-jre apktool
```

**Arch Linux / Manjaro:**
```sudo pacman -S git python-pip p7zip android-tools erofs-utils e2fsprogs patch jre-openjdk android-apktool```

## 🚀 Быстрый старт (На ПК)
```
git clone https://github.com/BrodGSI/BrodGSI_Tool
cd BrodGSI_Tool
pip install -r requirements.txt
python brodgsi.py
```
## 💻 Запуск

# Linux и MacOS:
```
python3 brodgsi.py
```

# Windows:
```
python brodgsi.py
```

## 🔗 Официальные ссылки
[📢 Telegram-канал с релизами](https://t.me/BrodGSIUpdates)
[📦 Архив сборок на SourceForge](https://sourceforge.net/projects/brodgsi/files)
