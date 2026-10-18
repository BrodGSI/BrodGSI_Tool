#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrodGSI Tool v3.0 (Matrix Edition)
Cross-platform automated Project Treble GSI builder (Windows / Linux / macOS / CI)
"""

import os
import re
import sys
import stat
import time
import shutil
import struct
import tarfile
import zipfile
import platform
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

import requests
import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)

# ==============================================================================
# МАТРИЧНАЯ ЦВЕТОВАЯ СХЕМА (MATRIX GREEN UI)
# ==============================================================================
MATRIX_THEME = Theme({
    "info": "bright_green",
    "warning": "bold green",
    "danger": "bold bright_green",
    "error": "bold bright_green",
    "cyan": "bright_green",
    "yellow": "green",
    "green": "bold bright_green",
    "red": "bold bright_green",
    "dim": "dim green",
    "rule.line": "bright_green",
    "bar.complete": "bright_green",
    "bar.finished": "bold bright_green",
    "bar.pulse": "green",
    "progress.description": "bright_green",
    "progress.percentage": "bold bright_green",
})

console = Console(theme=MATRIX_THEME)

MATRIX_STYLE = Style([
    ("qmark", "fg:#00ff41 bold"),
    ("question", "fg:#00ff41 bold"),
    ("answer", "fg:#00ff41 bold"),
    ("pointer", "fg:#00ff41 bold"),
    ("highlighted", "fg:#000000 bg:#00ff41 bold"),
    ("selected", "fg:#00ff41"),
    ("separator", "fg:#008f11"),
    ("instruction", "fg:#008f11"),
    ("text", "fg:#00ff41"),
])

# ==============================================================================
# КОНСТАНТЫ И КОНФИГУРАЦИЯ
# ==============================================================================
LANG = "ru"

REPOS_CONFIG = {
    "MysticGSI": "https://github.com/MysticGSI/MysticGSI.git",
    "yaebuebugsitool": "https://github.com/yaebuebu/yaebuebugsitool.git",
    "ErfanGSIs": "https://github.com/erfanoabdi/ErfanGSIs.git",
    "OriginGSITool": "https://github.com/Iceows/OriginGSITool.git",
}

TARGET_PARTITIONS = [
    "system",
    "vendor",
    "product",
    "system_ext",
    "odm",
    "my_product",
    "my_heytap",
    "my_manifest",
    "my_region",
    "my_stock",
    "prism",
    "optics",
]

MERGE_TO_SYSTEM = [
    "product",
    "system_ext",
    "my_product",
    "my_heytap",
    "my_manifest",
    "my_region",
    "my_stock",
    "prism",
    "optics",
]

# Безопасный список деблоата (БЕЗ удаления KnoxGuard, чтобы не вызывать блокировку/бутлуп)
DEFAULT_DEBLOAT_DIRS = [
    "app/Drive",
    "app/Duo",
    "app/Maps",
    "app/YouTube",
    "app/Videos",
    "app/Music2",
    "app/Photos",
    "priv-app/Velvet",
    "priv-app/Turbo",
    "priv-app/Wellbeing",
    "product/app/Gmail2",
    "product/app/GoogleTTS",
    "product/app/Maps",
    "product/app/YouTube",
    "product/priv-app/Velvet",
    "product/priv-app/AndroidAutoStub",
    "app/SamsungPass",
    "priv-app/SamsungPassAutofill_v1",
]

# ==============================================================================
# ЛОКАЛИЗАЦИЯ (RU / EN)
# ==============================================================================
I18N = {
    "ru": {
        "subtitle": "Кроссплатформенный сборщик GSI с автоопределением прошивки",
        "os_arch": "ОС и Архитектура:",
        "patch_bases": "Базы патчей:",
        "formats": "Форматы:",
        "main_menu": "Главное меню:",
        "menu_local": "1. Собрать GSI из локального файла / папки",
        "menu_url": "2. Собрать GSI по прямой ссылке (URL)",
        "menu_sync": "3. Синхронизировать базы патчей (Sparse Git)",
        "menu_list": "4. Показать список доступных профилей патчей",
        "menu_tools": "5. Диагностика системных утилит (bin/)",
        "menu_clean": "6. Очистка рабочих папок",
        "menu_lang": "7. Сменить язык / Change Language (RU -> EN)",
        "menu_exit": "8. Выход",
        "clean_title": "Выберите режим очистки:",
        "clean_workspace": "1. Очистить только workspace/ (временные файлы распаковки)",
        "clean_output": "2. Очистить только output/ (готовые GSI образы)",
        "clean_repos": "3. Очистить только repos/ (скачанные базы патчей)",
        "clean_all": "4. Очистить ВСЁ (workspace, output и repos)",
        "clean_back": "5. Назад в главное меню",
        "clean_ws_done": "✓ Папка workspace/ успешно очищена.",
        "clean_ws_empty": "Папка workspace/ уже пуста.",
        "clean_out_done": "✓ Папка output/ успешно очищена.",
        "clean_out_empty": "Папка output/ уже пуста.",
        "clean_repos_done": "✓ Папка repos/ успешно очищена.",
        "clean_repos_empty": "Папка repos/ уже пуста.",
        "ask_path": "Введите путь к прошивке (ZIP, TGZ, Payload, Super, папка):",
        "ask_url": "Введите прямую ссылку (URL) на прошивку:",
        "ask_patch_mode": "Выберите режим подбора патчей для прошивки:",
        "mode_auto": "Автовыбор (анализ прошивки, телефона и подбор лучшего патча)",
        "mode_manual": "Ручной выбор из списка профилей",
        "ask_fs": "Выберите файловую систему для финального GSI:",
        "fs_ext4": "ext4 (Read/Write, максимальная совместимость)",
        "fs_erofs": "erofs (Read-Only, минимальный размер)",
        "fs_both": "both (Собрать оба варианта: EXT4 и EROFS)",
        "ask_debloat": "Применить списки деблоата (удаление мусора OEM)?",
        "ask_split": "Разбить итоговый 7z архив на части по 450 МБ (для веб-загрузки SourceForge)?",
        "stage1": "Этап 1: Рекурсивная распаковка контейнеров прошивки",
        "stage2": "Этап 2: Распаковка разделов и слияние в единый system",
        "stage3": "Этап 3: Анализ донора, KnoxPatch и применение Treble-патчей",
        "stage4": "Этап 4: Перепаковка образа GSI и сжатие в 7z",
        "cloning": "Клонирование патчей из",
        "updating": "Обновление базы",
        "repo_ok": "База синхронизирована",
        "repo_skip": "Не удалось синхронизировать",
        "build_done": "Сборка GSI успешно завершена! Готовые файлы:",
    },
    "en": {
        "subtitle": "Cross-platform GSI Builder with Smart Firmware Heuristics",
        "os_arch": "OS & Architecture:",
        "patch_bases": "Patch Bases:",
        "formats": "Supported Formats:",
        "main_menu": "Main Menu:",
        "menu_local": "1. Build GSI from local file / directory",
        "menu_url": "2. Build GSI from direct URL",
        "menu_sync": "3. Sync patch repositories (Sparse Git)",
        "menu_list": "4. List available ROM patch profiles",
        "menu_tools": "5. Check system binaries & tools (bin/)",
        "menu_clean": "6. Clean workspace directories",
        "menu_lang": "7. Change Language / Сменить язык (EN -> RU)",
        "menu_exit": "8. Exit",
        "clean_title": "Select cleanup mode:",
        "clean_workspace": "1. Clean workspace/ only (temporary extraction files)",
        "clean_output": "2. Clean output/ only (built GSI images)",
        "clean_repos": "3. Clean repos/ only (downloaded patch bases)",
        "clean_all": "4. Clean ALL (workspace, output, and repos)",
        "clean_back": "5. Back to main menu",
        "clean_ws_done": "✓ workspace/ folder successfully cleaned.",
        "clean_ws_empty": "workspace/ folder is already empty.",
        "clean_out_done": "✓ output/ folder successfully cleaned.",
        "clean_out_empty": "output/ folder is already empty.",
        "clean_repos_done": "✓ repos/ folder successfully cleaned.",
        "clean_repos_empty": "repos/ folder is already empty.",
        "ask_path": "Enter path to firmware (ZIP, TGZ, Payload, Super, folder):",
        "ask_url": "Enter direct firmware URL:",
        "ask_patch_mode": "Select patch resolution mode:",
        "mode_auto": "Auto-select (analyze firmware/device and pick best match)",
        "mode_manual": "Manual selection from profile list",
        "ask_fs": "Select output GSI filesystem:",
        "fs_ext4": "ext4 (Read/Write, maximum compatibility)",
        "fs_erofs": "erofs (Read-Only, ultra-compact)",
        "fs_both": "both (Build both EXT4 and EROFS images)",
        "ask_debloat": "Apply OEM debloat lists?",
        "ask_split": "Split final 7z archive into 450MB volumes (for SourceForge Web)?",
        "stage1": "Stage 1: Recursive Firmware Container Extraction",
        "stage2": "Stage 2: Unpacking Partitions & Merging into System",
        "stage3": "Stage 3: Donor Analysis, KnoxPatch & Treble Patching",
        "stage4": "Stage 4: Repacking GSI Image & Ultra 7z Compression",
        "cloning": "Cloning patches from",
        "updating": "Updating repository",
        "repo_ok": "Repository synced",
        "repo_skip": "Failed to sync",
        "build_done": "GSI build completed successfully! Output files:",
    },
}


def tr(key: str) -> str:
    return I18N.get(LANG, I18N["ru"]).get(key, key)


# ==============================================================================
# БЕЗОПАСНОЕ УДАЛЕНИЕ ФАЙЛОВ (WINDOWS + LINUX СОВМЕСТИМОЕ)
# ==============================================================================
def remove_readonly(func, path, exc_info):
    """Корректно добавляет права на запись для удаления защищенных файлов на Windows и Linux."""
    try:
        os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
        func(path)
    except Exception:
        try:
            func(path)
        except Exception:
            pass


def safe_rmtree(dir_path: Path):
    """Безопасное рекурсивное удаление папки с обходом флагов Read-Only."""
    if dir_path.exists():
        shutil.rmtree(dir_path, onerror=remove_readonly)


# ==============================================================================
# ОКРУЖЕНИЕ ПЛАТФОРМЫ И ПОИСК УТИЛИТ
# ==============================================================================
class PlatformEnv:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        raw_sys = platform.system().lower()
        if "windows" in raw_sys:
            self.sys_name = "windows"
            self.ext = ".exe"
        elif "darwin" in raw_sys:
            self.sys_name = "darwin"
            self.ext = ""
        else:
            self.sys_name = "linux"
            self.ext = ""

        raw_arch = platform.machine().lower()
        if raw_arch in ("x86_64", "amd64"):
            self.arch = "amd64"
        elif raw_arch in ("aarch64", "arm64"):
            self.arch = "arm64"
        else:
            self.arch = raw_arch

        self.bin_dir = self.base_dir / "bin" / f"{self.sys_name}_{self.arch}"
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    def get_tool(self, name: str) -> str:
        """Ищет бинарную утилиту в bin/, в системном PATH или в стандартных путях Git/Java на Windows."""
        if name == "sdat2img":
            return "Built-in (Python Native)"

        candidates = [
            self.bin_dir / f"{name}{self.ext}",
            self.bin_dir / name,
            self.bin_dir / f"{name}.jar",
            self.bin_dir / f"{name}.bat",
        ]
        
        # Если ищем java, проверяем также путь, если распаковано в bin/windows_amd64/bin/
        if name == "java":
            candidates.append(self.bin_dir / "bin" / f"{name}{self.ext}")

        for local_bin in candidates:
            if local_bin.exists():
                if self.sys_name != "windows" and local_bin.suffix != ".jar":
                    try:
                        os.chmod(local_bin, os.stat(local_bin).st_mode | 0o111)
                    except Exception:
                        pass
                return str(local_bin)

        # Поиск в системном PATH
        sys_found = shutil.which(name) or shutil.which(f"{name}.bat")
        if sys_found:
            return sys_found

        # Дополнительный автопоиск для Windows (Git usr/bin и Java)
        if self.sys_name == "windows":
            if name in ("patch", "bash", "sh"):
                git_paths = [
                    Path(r"C:\Program Files\Git\usr\bin") / f"{name}.exe",
                    Path(r"C:\Program Files\Git\bin") / f"{name}.exe",
                    Path(r"C:\Program Files (x86)\Git\usr\bin") / f"{name}.exe",
                ]
                for gp in git_paths:
                    if gp.exists():
                        return str(gp)

            if name == "java":
                for prog_dir in [os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]:
                    for vendor in ["Java", "Eclipse Adoptium", "Microsoft", "BellSoft", "Zulu"]:
                        java_root = Path(prog_dir) / vendor
                        if java_root.exists():
                            found_javas = list(java_root.rglob("java.exe"))
                            if found_javas:
                                return str(found_javas[0])

        # Fallback для brotli через Python-модуль
        if name == "brotli":
            try:
                import brotli  # noqa
                return "Built-in (Python brotli module)"
            except ImportError:
                pass

        return ""

    def print_diagnostics(self):
        tools = [
            "7z",
            "git",
            "payload-dumper-go",
            "simg2img",
            "img2simg",
            "lpunpack",
            "brotli",
            "sdat2img.py",
            "extract.erofs",
            "mkfs.erofs",
            "mke2fs",
            "e2fsdroid",
            "patch",
            "apktool",
            "java",
        ]
        table = Table(title=f"Binaries & Tools ({self.sys_name}_{self.arch})", border_style="bright_green")
        table.add_column("Tool", style="bold bright_green")
        table.add_column("Status", style="bright_green")
        table.add_column("Resolved Path", style="dim green")

        for t in tools:
            resolved = self.get_tool(t)
            if resolved:
                table.add_row(t, "✓ FOUND", resolved)
            else:
                table.add_row(t, "✗ MISSING", "Not in bin/ or PATH")
        console.print(table)


# ==============================================================================
# СИНХРОНИЗАЦИЯ БАЗ ПАТЧЕЙ (SPARSE CHECKOUT — ТОЛЬКО ПАТЧИ)
# ==============================================================================
class RepoSyncManager:
    def __init__(self, base_dir: Path, env: PlatformEnv):
        self.base_dir = base_dir
        self.env = env
        self.repos_dir = self.base_dir / "repos"
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def sync_all(self):
        git_bin = self.env.get_tool("git") or "git"
        git_env = os.environ.copy()
        git_env["GIT_TERMINAL_PROMPT"] = "0"

        for name, url in REPOS_CONFIG.items():
            target_dir = self.repos_dir / name
            if (target_dir / ".git").exists():
                console.log(f"[bright_green]{tr('updating')} {name}...[/bright_green]")
                subprocess.run([git_bin, "pull"], cwd=str(target_dir), env=git_env, check=False)
            else:
                console.log(f"[bright_green]{tr('cloning')} {name} ({url})...[/bright_green]")
                res = subprocess.run(
                    [git_bin, "clone", "--filter=blob:none", "--sparse", "--depth=1", url, str(target_dir)],
                    env=git_env,
                    check=False,
                )
                if res.returncode == 0:
                    if name.lower() == "mysticgsi":
                        sparse_dirs = ["patches"]
                    else:
                        sparse_dirs = ["ROMsPatches", "roms", "Patches", "prebuilt", "common"]
                    subprocess.run(
                        [git_bin, "sparse-checkout", "set"] + sparse_dirs,
                        cwd=str(target_dir),
                        env=git_env,
                        check=False,
                    )
                    console.log(f"[bold bright_green]✓ {name}: {tr('repo_ok')} (Sparse Patches Only)[/bold bright_green]")
                else:
                    console.log(f"[green]⚠ {tr('repo_skip')}: {name}[/green]")
                    safe_rmtree(target_dir)

    def discover_patch_candidates(self) -> list:
        candidates = []
        if not self.repos_dir.exists():
            return candidates
        search_roots = ["patches", "ROMsPatches", "roms", "Patches"]
        for repo in self.repos_dir.iterdir():
            if not repo.is_dir():
                continue
            for sr in search_roots:
                root_dir = repo / sr
                if root_dir.exists() and root_dir.is_dir():
                    for item in root_dir.iterdir():
                        if item.is_dir() and not item.name.startswith("."):
                            candidates.append(item)
        return candidates


# ==============================================================================
# ЭТАП 1: РЕКУРСИВНЫЙ РАСПАКОВЩИК КОНТЕЙНЕРОВ ПРОШИВКИ
# ==============================================================================
class FirmwareExtractor:
    def __init__(self, env: PlatformEnv, work_dir: Path):
        self.env = env
        self.work_dir = work_dir
        self.extract_dir = self.work_dir / "01_extracted"
        self.img_dir = self.work_dir / "02_images"
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)

    def download_rom(self, url: str) -> Path:
        dl_dir = self.work_dir / "00_download"
        dl_dir.mkdir(parents=True, exist_ok=True)
        clean_name = url.split("?")[0].rstrip("/").split("/")[-1]
        if not clean_name or "." not in clean_name:
            clean_name = "firmware_download.zip"
        dest_path = dl_dir / clean_name

        aria2 = self.env.get_tool("aria2c")
        if aria2:
            console.log(f"[bright_green]⬇ Скачивание через aria2c (16 потоков): {clean_name}[/bright_green]")
            res = subprocess.run([aria2, "-x16", "-s16", "-d", str(dl_dir), "-o", clean_name, url])
            if res.returncode == 0 and dest_path.exists():
                return dest_path

        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with Progress(
                SpinnerColumn(style="bright_green"),
                TextColumn("[bright_green]{task.description}[/bright_green]"),
                BarColumn(complete_style="bright_green", finished_style="bold bright_green"),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(clean_name, total=total)
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
        return dest_path

    def process_input(self, source_path: Path):
        console.rule(f"[bold bright_green]{tr('stage1')}[/bold bright_green]")
        if source_path.is_dir():
            for item in source_path.rglob("*"):
                if item.is_file():
                    shutil.copy2(item, self.extract_dir / item.name)
        else:
            self._unpack_archive(source_path, self.extract_dir)

        for _ in range(5):
            changed = False
            for f in list(self.extract_dir.rglob("*")):
                if f.is_file() and self._process_intermediate(f):
                    changed = True
            if not changed:
                break

        for part in TARGET_PARTITIONS:
            candidate = self.img_dir / f"{part}.img"
            if candidate.exists() and candidate.stat().st_size > 0:
                fs_label = self._detect_fs_type(candidate)
                console.log(f"[bold bright_green]✓ Partition Ready: {candidate.name} ({fs_label})[/bold bright_green]")

        if not (self.img_dir / "system.img").exists():
            raise RuntimeError("Не удалось извлечь system.img из предоставленной прошивки!")

    def _unpack_archive(self, archive: Path, out_dir: Path) -> bool:
        name_l = archive.name.lower()
        seven_z = self.env.get_tool("7z")

        if name_l.endswith(".zip"):
            console.log(f"[bright_green]{archive.name} -> ZIP[/bright_green]")
            if seven_z:
                subprocess.run([seven_z, "x", "-y", f"-o{out_dir}", str(archive)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                with zipfile.ZipFile(archive, "r") as zf:
                    zf.extractall(out_dir)
            return True

        if any(name_l.endswith(ext) for ext in (".tgz", ".tar.gz", ".tar", ".tar.md5")):
            console.log(f"[bright_green]{archive.name} -> TAR/TGZ[/bright_green]")
            if seven_z:
                subprocess.run([seven_z, "x", "-y", f"-o{out_dir}", str(archive)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                with tarfile.open(archive, "r:*") as tf:
                    tf.extractall(out_dir)
            return True

        if name_l.endswith((".7z", ".rar", ".xz", ".gz", ".lz4")):
            if seven_z:
                console.log(f"[bright_green]{archive.name} -> 7Z Extract[/bright_green]")
                subprocess.run([seven_z, "x", "-y", f"-o{out_dir}", str(archive)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
        return False

    def _process_intermediate(self, file_path: Path) -> bool:
        name = file_path.name
        name_l = name.lower()

        if name_l.endswith((".zip", ".tar", ".tgz", ".tar.gz", ".tar.md5", ".7z")):
            sub_out = file_path.parent / f"unpacked_{file_path.stem}"
            sub_out.mkdir(parents=True, exist_ok=True)
            if self._unpack_archive(file_path, sub_out):
                try:
                    file_path.unlink()
                except Exception:
                    pass
                return True

        if name_l == "payload.bin":
            dumper = self.env.get_tool("payload-dumper-go")
            if dumper:
                console.log("[bright_green]payload.bin -> payload-dumper-go[/bright_green]")
                subprocess.run([dumper, "-o", str(self.img_dir), str(file_path)], check=False)
                try:
                    file_path.unlink()
                except Exception:
                    pass
                return True

        if name_l.endswith(".new.dat.br"):
            brotli = self.env.get_tool("brotli")
            out_dat = file_path.with_suffix("")
            if brotli:
                console.log(f"[bright_green]{name} -> brotli[/bright_green]")
                subprocess.run([brotli, "-d", str(file_path), "-o", str(out_dat)], check=False)
                try:
                    file_path.unlink()
                except Exception:
                    pass
                return True

        if name_l.endswith(".new.dat"):
            part_prefix = name[:-8]
            transfer_list = file_path.parent / f"{part_prefix}.transfer.list"
            if transfer_list.exists():
                console.log(f"[bright_green]{name} -> sdat2img[/bright_green]")
                out_img = self.img_dir / f"{part_prefix}.img"
                self._sdat2img_native(transfer_list, file_path, out_img)
                try:
                    file_path.unlink()
                    transfer_list.unlink()
                except Exception:
                    pass
                return True

        if name_l.endswith(".img"):
            part_stem = file_path.stem.lower()
            for suffix in ("_a", "_b"):
                if part_stem.endswith(suffix) and part_stem[:-2] in TARGET_PARTITIONS:
                    part_stem = part_stem[:-2]

            if self._is_sparse_image(file_path):
                simg2img = self.env.get_tool("simg2img")
                if simg2img:
                    raw_img = file_path.with_suffix(".raw.img")
                    subprocess.run([simg2img, str(file_path), str(raw_img)], check=False)
                    if raw_img.exists() and raw_img.stat().st_size > 0:
                        try:
                            file_path.unlink()
                        except Exception:
                            pass
                        raw_img.rename(file_path)
                        return True

            if part_stem == "super":
                lpunpack = self.env.get_tool("lpunpack")
                if lpunpack:
                    console.log("[bright_green]super.img -> lpunpack[/bright_green]")
                    subprocess.run([lpunpack, str(file_path), str(self.extract_dir)], check=False)
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
                    return True

            if part_stem in TARGET_PARTITIONS:
                target_img = self.img_dir / f"{part_stem}.img"
                if file_path.resolve() != target_img.resolve():
                    shutil.move(str(file_path), str(target_img))
                    return True

        return False

    @staticmethod
    def _is_sparse_image(img_path: Path) -> bool:
        try:
            with open(img_path, "rb") as f:
                magic = f.read(4)
            return magic == b"\x3a\xff\x26\xed"
        except Exception:
            return False

    @staticmethod
    def _detect_fs_type(img_path: Path) -> str:
        try:
            with open(img_path, "rb") as f:
                header = f.read(4096)
            if len(header) >= 0x404 and header[0x400:0x404] == b"\xe2\xe1\xf5\xe0":
                return "EROFS"
            if len(header) >= 0x43A and header[0x438:0x43A] == b"\x53\xef":
                return "EXT4"
        except Exception:
            pass
        return "RAW/EXT4"

    @staticmethod
    def _sdat2img_native(transfer_list_path: Path, new_dat_path: Path, out_img_path: Path):
        BLOCK_SIZE = 4096
        lines = transfer_list_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        version = int(lines[0])
        commands = []
        for line in lines[4 if version >= 2 else 2 :]:
            parts = line.split(" ")
            cmd = parts[0]
            if cmd in ("new", "erase", "zero"):
                nums = [int(x) for x in parts[1].split(",")]
                block_ranges = [(nums[i], nums[i + 1]) for i in range(1, len(nums), 2)]
                commands.append((cmd, block_ranges))

        with open(new_dat_path, "rb") as dat_f, open(out_img_path, "wb") as out_f:
            for cmd, ranges in commands:
                if cmd == "new":
                    for begin, end in ranges:
                        out_f.seek(begin * BLOCK_SIZE)
                        count = end - begin
                        out_f.write(dat_f.read(count * BLOCK_SIZE))


# ==============================================================================
# ЭТАП 3: УМНЫЙ АНАЛИЗАТОР ПРОШИВКИ, KNOXPATCH (ONEUI) И ПРИМЕНЕНИЕ ПАТЧЕЙ
# ==============================================================================
class UniversalPatchEngine:
    def __init__(self, env: PlatformEnv, base_dir: Path, repo_mgr: RepoSyncManager, sys_root: Path, inner_sys: Path):
        self.env = env
        self.base_dir = base_dir
        self.repo_mgr = repo_mgr
        self.sys_root = sys_root
        self.inner_sys = inner_sys
        self.props = {}
        self.rom_info = {}
        self.android_ver = "14"
        self.extra_file_contexts = []
        self._analyze_firmware_and_device()

    def _analyze_firmware_and_device(self):
        """Собирает все build.prop и определяет ОС, оболочку, телефон и чипсет донора."""
        prop_files = [
            self.inner_sys / "build.prop",
            self.inner_sys / "product" / "etc" / "build.prop",
            self.inner_sys / "product" / "build.prop",
            self.inner_sys / "system_ext" / "etc" / "build.prop",
            self.inner_sys / "vendor" / "build.prop",
            self.sys_root / "vendor" / "build.prop",
        ]
        for pf in prop_files:
            if pf.exists():
                try:
                    for line in pf.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            self.props[k.strip()] = v.strip()
                except Exception:
                    pass

        brand = self.props.get("ro.product.system.brand") or self.props.get("ro.product.brand", "Generic")
        device = self.props.get("ro.product.system.device") or self.props.get("ro.product.device", "generic")
        model = self.props.get("ro.product.system.model") or self.props.get("ro.product.model", "Unknown")
        board = self.props.get("ro.board.platform") or self.props.get("ro.product.board", "unknown")
        sdk = self.props.get("ro.build.version.sdk", "34")
        self.android_ver = self.props.get("ro.build.version.release", "14").split(".")[0]

        os_skin = "AOSP"
        os_aliases = ["aosp", "pixel", "generic"]

        if (
            any(k.startswith("ro.build.version.oneui") or "samsung" in brand.lower() for k in self.props)
            or (self.inner_sys / "framework" / "samsung-services.jar").exists()
        ):
            os_skin = "OneUI"
            os_aliases = ["oneui", "samsung", "knox"]
        elif "ro.mi.os.version.name" in self.props:
            os_skin = "HyperOS"
            os_aliases = ["hyperos", "miui", "xiaomi"]
        elif "ro.miui.ui.version.name" in self.props:
            os_skin = "MIUI"
            os_aliases = ["miui", "xiaomi"]
        elif "ro.vivo.os.name" in self.props or "vivo" in brand.lower():
            os_skin = "OriginOS"
            os_aliases = ["originos", "funtouch", "vivo"]
        elif "ro.build.version.oplusrom" in self.props or any(x in brand.lower() for x in ["oppo", "realme", "oneplus"]):
            os_skin = "ColorOS"
            os_aliases = ["coloros", "oxygenos", "realmeui", "oplus", "oneplus"]
        elif "ro.Nothing.version" in self.props or "nothing" in brand.lower():
            os_skin = "NothingOS"
            os_aliases = ["nothing", "nothingos"]
        elif "google" in brand.lower():
            os_skin = "Pixel"
            os_aliases = ["pixel", "google", "aosp"]

        self.rom_info = {
            "brand": brand,
            "device": device,
            "model": model,
            "board": board,
            "sdk": sdk,
            "android_ver": self.android_ver,
            "os_skin": os_skin,
            "aliases": os_aliases,
        }

        console.log(
            f"[bold bright_green]🔍 Анализ донора:[/bold bright_green] "
            f"[bright_green]{brand} {model} ({device}) | Чипсет: {board} | "
            f"Оболочка: {os_skin} | Android {self.android_ver} (SDK {sdk})[/bright_green]"
        )

    def _score_patch_candidate(self, patch_dir: Path) -> int:
        """Вычисляет рейтинг подходящего патча на основе оболочки, телефона, чипсета и богатства патча."""
        name_lower = patch_dir.name.lower()
        path_lower = str(patch_dir).lower()
        score = 0

        if any(alias in name_lower for alias in self.rom_info["aliases"]):
            score += 100
        elif any(alias in path_lower for alias in self.rom_info["aliases"]):
            score += 50

        dev = self.rom_info["device"].lower()
        brd = self.rom_info["board"].lower()
        if dev != "generic" and dev in name_lower:
            score += 60
        if brd != "unknown" and brd in name_lower:
            score += 40

        if f"a{self.android_ver}" in name_lower or f"android{self.android_ver}" in name_lower or self.rom_info["sdk"] in name_lower:
            score += 50

        files_count = sum(1 for _ in patch_dir.rglob("*") if _.is_file())
        sh_count = sum(1 for _ in patch_dir.rglob("*.sh"))
        diff_count = sum(1 for _ in patch_dir.rglob("*.patch")) + sum(1 for _ in patch_dir.rglob("*.diff"))
        score += min(files_count * 2, 40) + (sh_count * 10) + (diff_count * 15)

        return score

    def apply_oneui_knox_patch(self):
        """
        Специальный патч для Samsung OneUI (KnoxPatch):
        Не удаляя сам пакет KnoxGuard из системы (чтобы избежать блокировки/бутлупа),
        декомпилирует services.jar, в SystemServer.smali находит вызов StartKnoxGuard,
        удаляет move-result выше него и меняет условный переход if-* на goto.
        """
        services_jar = self.inner_sys / "framework" / "services.jar"
        if not services_jar.exists():
            return

        apktool = self.env.get_tool("apktool")
        java_bin = shutil.which("java")
        if not apktool or not java_bin:
            console.log("[green]⚠ Пропуск KnoxPatch: не найден apktool или Java в системе.[/green]")
            return

        console.log("[bold bright_green]🛡 [OneUI] Запуск KnoxPatch для services.jar (обход StartKnoxGuard без удаления APK)...[/bold bright_green]")
        work_jar_dir = self.base_dir / "workspace" / "knox_services_tmp"
        safe_rmtree(work_jar_dir)

        if apktool.endswith(".jar"):
            decompile_cmd = [java_bin, "-jar", apktool, "d", "-f", str(services_jar), "-o", str(work_jar_dir)]
            build_cmd = [java_bin, "-jar", apktool, "b", str(work_jar_dir), "-o", str(services_jar)]
        else:
            decompile_cmd = [apktool, "d", "-f", str(services_jar), "-o", str(work_jar_dir)]
            build_cmd = [apktool, "b", str(work_jar_dir), "-o", str(services_jar)]

        res = subprocess.run(decompile_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            console.log("[green]⚠ Ошибка декомпиляции services.jar[/green]")
            return

        smali_files = list(work_jar_dir.rglob("SystemServer.smali"))
        if not smali_files:
            console.log("[green]⚠ Файл SystemServer.smali не найден в services.jar[/green]")
            safe_rmtree(work_jar_dir)
            return

        patched_any = False
        for smali_file in smali_files:
            lines = smali_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            modified = False

            for idx, line in enumerate(lines):
                if "StartKnoxGuard" in line:
                    console.log(f"[bright_green]✓ Найден блок StartKnoxGuard в {smali_file.name} (строка {idx + 1})[/bright_green]")
                    start_search = max(0, idx - 18)
                    for back_idx in range(idx - 1, start_search - 1, -1):
                        b_line = lines[back_idx].strip()

                        if b_line.startswith("if-"):
                            parts = b_line.split(",")
                            if len(parts) >= 2 and ":cond_" in parts[-1]:
                                target_label = parts[-1].strip()
                                indent = lines[back_idx][: len(lines[back_idx]) - len(lines[back_idx].lstrip())]
                                lines[back_idx] = f"{indent}goto {target_label}"
                                console.log(
                                    f"[bright_green]  -> Заменен '{b_line}' на 'goto {target_label}' (строка {back_idx + 1})[/bright_green]"
                                )
                                modified = True

                        elif b_line.startswith("move-result"):
                            lines[back_idx] = f"    # removed by BrodGSI KnoxPatch: {b_line}"
                            console.log(f"[bright_green]  -> Удален '{b_line}' (строка {back_idx + 1})[/bright_green]")
                            modified = True
                            break

            if modified:
                smali_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                patched_any = True

        if patched_any:
            console.log("[bright_green]🔨 Сборка пропатченного services.jar...[/bright_green]")
            b_res = subprocess.run(build_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if b_res.returncode == 0:
                console.log("[bold bright_green]✓ KnoxPatch успешно применен к services.jar![/bold bright_green]")
            else:
                console.log("[green]⚠ Ошибка при обратной сборке services.jar[/green]")
        else:
            console.log("[dim]Участок StartKnoxGuard не потребовал изменений или уже пропатчен.[/dim]")

        safe_rmtree(work_jar_dir)

    def resolve_and_apply_patches(self, auto_select_mode: bool = True, enable_debloat: bool = True) -> str:
        candidates = self.repo_mgr.discover_patch_candidates()
        selected_patches = []

        if candidates:
            if auto_select_mode:
                scored = [(self._score_patch_candidate(c), c) for c in candidates]
                scored.sort(key=lambda x: x[0], reverse=True)
                best_score, best_candidate = scored[0]
                console.log(
                    f"[bold bright_green]🎯 Автовыбор подобрал профиль: "
                    f"{best_candidate.name} ({best_candidate.parent.parent.name}) — Рейтинг: {best_score} очков[/bold bright_green]"
                )
                selected_patches = [best_candidate]
            else:
                choices = [f"{c.name} ({c.parent.parent.name})" for c in candidates]
                picked = questionary.checkbox(
                    "Выберите профили патчей (Пробел - отметить, Enter - подтвердить):",
                    choices=choices,
                    style=MATRIX_STYLE,
                ).ask()
                if picked:
                    for p_str in picked:
                        idx = choices.index(p_str)
                        selected_patches.append(candidates[idx])

        for patch_dir in selected_patches:
            self._apply_patch_directory(patch_dir)

        if self.rom_info.get("os_skin") == "OneUI":
            self.apply_oneui_knox_patch()

        if enable_debloat:
            self._run_debloat()

        return self.rom_info.get("os_skin", "Generic")

    def _apply_patch_directory(self, patch_dir: Path):
        console.log(f"[bright_green]🔧 Применение профиля патчей: {patch_dir.name}...[/bright_green]")
        for overlay_name in ("system", "prebuilt", "overlay"):
            ov_dir = patch_dir / overlay_name
            if ov_dir.exists() and ov_dir.is_dir():
                shutil.copytree(ov_dir, self.inner_sys, dirs_exist_ok=True)

        for prop_file in patch_dir.rglob("*.prop"):
            try:
                extra_lines = prop_file.read_text(encoding="utf-8", errors="ignore")
                main_prop = self.inner_sys / "build.prop"
                if main_prop.exists():
                    with open(main_prop, "a", encoding="utf-8") as f:
                        f.write(f"\n# Added from {patch_dir.name}/{prop_file.name}\n{extra_lines}\n")
            except Exception:
                pass

        patch_bin = self.env.get_tool("patch")
        if patch_bin:
            for diff_file in patch_dir.rglob("*.patch"):
                subprocess.run(
                    [patch_bin, "-p1", "-d", str(self.sys_root), "-i", str(diff_file), "--forward"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

        bash_bin = shutil.which("bash")
        if bash_bin:
            for sh_file in patch_dir.glob("*.sh"):
                subprocess.run(
                    [bash_bin, str(sh_file), str(self.inner_sys)],
                    cwd=str(patch_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

    def _run_debloat(self):
        removed = 0
        for rel_path in DEFAULT_DEBLOAT_DIRS:
            target = self.inner_sys / rel_path
            if target.exists():
                safe_rmtree(target)
                removed += 1
        if removed:
            console.log(f"[bright_green]🧹 Деблоат: удалено {removed} мусорных OEM-пакетов (KnoxGuard сохранен).[/bright_green]")


# ==============================================================================
# ЭТАП 2 И 4: СБОРКА СИСТЕМЫ, BOOT-ФИКСЫ, ПЕРЕПАКОВКА И СЖАТИЕ В 7Z
# ==============================================================================
class GSIPatcher:
    def __init__(
        self,
        env: PlatformEnv,
        base_dir: Path,
        work_dir: Path,
        repo_mgr: RepoSyncManager,
        split_archive: bool = False,
    ):
        self.env = env
        self.base_dir = base_dir
        self.work_dir = work_dir
        self.repo_mgr = repo_mgr
        self.split_archive = split_archive
        self.img_dir = self.work_dir / "02_images"
        self.fs_dir = self.work_dir / "03_filesystem"
        self.out_dir = self.base_dir / "output"
        self.fs_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def unpack_partition(self, part_name: str, img_path: Path, out_dir: Path):
        out_dir.mkdir(parents=True, exist_ok=True)
        fs_type = FirmwareExtractor._detect_fs_type(img_path)
        console.log(f"[bright_green]📂 Распаковка {img_path.name} ({fs_type})...[/bright_green]")

        if fs_type == "EROFS":
            erofs_bin = self.env.get_tool("extract.erofs")
            if erofs_bin:
                subprocess.run([erofs_bin, "-i", str(img_path), "-x", "-o", str(out_dir.parent)], check=False)
                extracted_sub = out_dir.parent / part_name
                if extracted_sub.exists() and extracted_sub != out_dir:
                    shutil.move(str(extracted_sub), str(out_dir))
                return

        seven_z = self.env.get_tool("7z")
        if seven_z:
            subprocess.run([seven_z, "x", "-y", f"-o{out_dir}", str(img_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _apply_mandatory_boot_fixes(self, sys_root: Path, inner_sys: Path):
        """Обязательные правки build.prop и штамп PortedByBrodGSI."""
        build_prop = inner_sys / "build.prop"
        date_str = datetime.now().strftime("%Y%m%d")
        stamp = f"PortedByBrodGSI_{date_str}"

        mandatory_props = [
            "",
            "# === BrodGSI Treble Mandatory Fixes ===",
            f"ro.build.display.id={stamp}",
            f"ro.system.build.id={stamp}",
            "ro.control_privapp_permissions=log",
            "persist.sys.usb.config=adb,mtp",
            "ro.adb.secure=0",
            "ro.debuggable=1",
            "service.adb.root=1",
            "ro.setupwizard.mode=OPTIONAL",
        ]

        if build_prop.exists():
            try:
                content = build_prop.read_text(encoding="utf-8", errors="ignore")
                content += "\n" + "\n".join(mandatory_props) + "\n"
                build_prop.write_text(content, encoding="utf-8")
                console.log(f"[bold bright_green]✓ Применены Treble-фиксы и штамп: {stamp}[/bold bright_green]")
            except Exception as e:
                console.log(f"[green]⚠ Не удалось обновить build.prop: {e}[/green]")

    def _get_dir_size_bytes(self, folder: Path) -> int:
        total = 0
        for root, _, files in os.walk(folder):
            for f in files:
                fp = Path(root) / f
                if not fp.is_symlink():
                    try:
                        total += fp.stat().st_size
                    except Exception:
                        pass
        return total

    def _repack_image(self, sys_root: Path, rom_label: str, android_ver: str, fs_type: str, extra_contexts: list) -> Path:
        out_name = f"BrodGSI-{rom_label}-A{android_ver}-AB-{fs_type.upper()}.img"
        out_img = self.out_dir / out_name
        if out_img.exists():
            out_img.unlink()

        if fs_type.lower() == "erofs":
            mkfs_erofs = self.env.get_tool("mkfs.erofs")
            if mkfs_erofs:
                console.log(f"[bright_green]🔨 Сборка EROFS образа: {out_name}...[/bright_green]")
                subprocess.run([mkfs_erofs, "-zlz4hc", "-T", "1230768000", str(out_img), str(sys_root)], check=False)
                if out_img.exists():
                    return out_img

        console.log(f"[bright_green]🔨 Сборка EXT4 образа: {out_name}...[/bright_green]")
        raw_size = self._get_dir_size_bytes(sys_root)
        target_size = max(int(raw_size * 1.18) + (128 * 1024 * 1024), 1024 * 1024 * 1024)
        blocks = target_size // 4096

        mke2fs = self.env.get_tool("mke2fs")
        e2fsdroid = self.env.get_tool("e2fsdroid")

        if mke2fs and e2fsdroid:
            subprocess.run(
                [mke2fs, "-O", "^has_journal", "-L", "/", "-I", "256", "-M", "/", "-m", "0", "-t", "ext4", "-b", "4096", str(out_img), str(blocks)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                [e2fsdroid, "-e", "-T", "1230768000", "-f", str(sys_root), "-a", "/", str(out_img)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            shutil.copy2(self.img_dir / "system.img", out_img)

        return out_img

    def _compress_to_7z(self, img_path: Path) -> Path:
        seven_z = self.env.get_tool("7z")
        if not seven_z or not img_path.exists():
            console.log("[green]⚠ Утилита 7z не найдена. Оставляем .img без сжатия.[/green]")
            return img_path

        archive_path = img_path.with_suffix(".7z")
        console.log(f"[bright_green]📦 Упаковка {img_path.name} в архив (Ultra LZMA2)... Это займет пару минут.[/bright_green]")

        cmd = [seven_z, "a", "-t7z", "-mx=9", "-m0=lzma2", "-md=64m", "-ms=on"]
        if self.split_archive:
            cmd.append("-v450m")
        cmd.extend([str(archive_path), str(img_path)])

        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        check_file = archive_path.with_suffix(".7z.001") if self.split_archive else archive_path
        if res.returncode == 0 and check_file.exists():
            console.log(f"[bold bright_green]✓ Сжатие завершено: {check_file.name}[/bold bright_green]")
            try:
                img_path.unlink()
                console.log(f"[dim]🗑 Оригинальный файл {img_path.name} удален для экономии места на диске.[/dim]")
            except Exception as e:
                console.log(f"[green]⚠ Архив создан, но удалить оригинал не удалось: {e}[/green]")
            return check_file
        else:
            console.log("[bold bright_green]✗ Ошибка при сжатии. Оставляем оригинальный .img файл.[/bold bright_green]")
            return img_path

    def build_gsi(self, auto_select_mode: bool = True, fs_type: str = "ext4", enable_debloat: bool = True) -> list:
        console.rule(f"[bold bright_green]{tr('stage2')}[/bold bright_green]")

        sys_img = self.img_dir / "system.img"
        if not sys_img.exists():
            raise FileNotFoundError("system.img not found!")

        sys_root = self.fs_dir / "system"
        self.unpack_partition("system", sys_img, sys_root)

        inner_sys = sys_root / "system"
        if not inner_sys.exists() and (sys_root / "build.prop").exists():
            temp_sys = self.fs_dir / "system_tmp"
            sys_root.rename(temp_sys)
            sys_root.mkdir(parents=True, exist_ok=True)
            shutil.move(str(temp_sys), str(sys_root / "system"))
            inner_sys = sys_root / "system"

        for part in MERGE_TO_SYSTEM:
            part_img = self.img_dir / f"{part}.img"
            if part_img.exists():
                console.log(f"[bright_green]🔗 Слияние раздела {part}.img -> /system/{part}...[/bright_green]")
                target_part_dir = inner_sys / part
                if target_part_dir.is_symlink() or target_part_dir.is_file():
                    target_part_dir.unlink()
                elif target_part_dir.is_dir():
                    safe_rmtree(target_part_dir)

                self.unpack_partition(part, part_img, target_part_dir)

                root_link = sys_root / part
                if root_link.exists() or root_link.is_symlink():
                    if root_link.is_dir() and not root_link.is_symlink():
                        safe_rmtree(root_link)
                    else:
                        root_link.unlink()
                try:
                    os.symlink(f"/system/{part}", root_link)
                except OSError:
                    pass

        console.rule(f"[bold bright_green]{tr('stage3')}[/bold bright_green]")
        patch_engine = UniversalPatchEngine(self.env, self.base_dir, self.repo_mgr, sys_root, inner_sys)
        final_rom_label = patch_engine.resolve_and_apply_patches(
            auto_select_mode=auto_select_mode, enable_debloat=enable_debloat
        )
        self._apply_mandatory_boot_fixes(sys_root, inner_sys)

        console.rule(f"[bold bright_green]{tr('stage4')}[/bold bright_green]")
        fs_types = ["ext4", "erofs"] if fs_type == "both" else [fs_type]
        output_images = []
        for fst in fs_types:
            out_img = self._repack_image(
                sys_root, final_rom_label, patch_engine.android_ver, fst, patch_engine.extra_file_contexts
            )
            out_archive = self._compress_to_7z(out_img)
            output_images.append(out_archive)

        return output_images


# ==============================================================================
# ИНТЕРАКТИВНЫЕ МЕНЮ И ТОЧКА ВХОДА MAIN()
# ==============================================================================
def print_banner(env: PlatformEnv):
    console.clear()
    info_text = (
        f"[bold bright_green]{tr('os_arch')}[/bold bright_green]  {env.sys_name.upper()} ({env.arch})\n"
        f"[bold bright_green]{tr('patch_bases')}[/bold bright_green]   MysticGSI • yaebuebugsitool • ErfanGSIs • OriginGSITool\n"
        f"[bold bright_green]{tr('formats')}[/bold bright_green]       ZIP, TGZ, Payload, Super, .new.dat.br, UPDATE.APP, AP.tar, EROFS/EXT4/F2FS"
    )
    panel = Panel(
        info_text,
        title="[bold bright_green]BrodGSI Tool v3.0 (Matrix Edition)[/bold bright_green]",
        subtitle=f"[bright_green]{tr('subtitle')}[/bright_green]",
        border_style="bright_green",
    )
    console.print(panel)


def cleanup_menu(base_dir: Path):
    """Интерактивное меню очистки рабочих папок с поддержкой локализации и обходом Read-Only."""
    workspace_dir = base_dir / "workspace"
    output_dir = base_dir / "output"
    repos_dir = base_dir / "repos"

    choices = [
        tr("clean_workspace"),
        tr("clean_output"),
        tr("clean_repos"),
        tr("clean_all"),
        tr("clean_back"),
    ]

    action = questionary.select(tr("clean_title"), choices=choices, style=MATRIX_STYLE).ask()
    if not action or action.startswith("5") or "Back" in action or "Назад" in action:
        return

    if action.startswith("1") or action.startswith("4"):
        if workspace_dir.exists():
            safe_rmtree(workspace_dir)
            console.print(f"[bold bright_green]{tr('clean_ws_done')}[/bold bright_green]")
        else:
            console.print(f"[green]{tr('clean_ws_empty')}[/green]")

    if action.startswith("2") or action.startswith("4"):
        if output_dir.exists():
            safe_rmtree(output_dir)
            console.print(f"[bold bright_green]{tr('clean_out_done')}[/bold bright_green]")
        else:
            console.print(f"[green]{tr('clean_out_empty')}[/green]")

    if action.startswith("3") or action.startswith("4"):
        if repos_dir.exists():
            safe_rmtree(repos_dir)
            console.print(f"[bold bright_green]{tr('clean_repos_done')}[/bold bright_green]")
        else:
            console.print(f"[green]{tr('clean_repos_empty')}[/green]")

    questionary.press_any_key_to_continue(style=MATRIX_STYLE).ask()


def main():
    global LANG
    parser = argparse.ArgumentParser(description="BrodGSI Tool v3.0 (Matrix Edition)")
    parser.add_argument("--ci", action="store_true", help="Run in headless CI mode (GitHub Actions)")
    parser.add_argument("--url", type=str, help="Direct firmware URL or local file path")
    parser.add_argument("--fs", type=str, default="ext4", choices=["ext4", "erofs", "both"], help="Output filesystem")
    parser.add_argument("--debloat", action="store_true", help="Enable OEM debloat")
    parser.add_argument("--split", action="store_true", help="Split 7z archive into 450MB volumes")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    env = PlatformEnv(base_dir)
    repo_mgr = RepoSyncManager(base_dir, env)
    work_dir = base_dir / "workspace"

    # Headless режим для облачной сборки через GitHub Actions
    if args.ci:
        console.rule("[bold bright_green]BrodGSI Tool v3.0 — CLOUD CI MODE[/bold bright_green]")
        if not args.url:
            raise ValueError("Параметр --url обязателен в режиме --ci!")
        repo_mgr.sync_all()
        safe_rmtree(work_dir)
        extractor = FirmwareExtractor(env, work_dir)
        source_path = extractor.download_rom(args.url) if args.url.startswith("http") else Path(args.url)
        extractor.process_input(source_path)

        patcher = GSIPatcher(env, base_dir, work_dir, repo_mgr, split_archive=args.split)
        built = patcher.build_gsi(auto_select_mode=True, fs_type=args.fs, enable_debloat=args.debloat)
        console.rule("[bold bright_green]CI BUILD COMPLETED[/bold bright_green]")
        for f in built:
            console.print(f"[bold bright_green] -> {f}[/bold bright_green]")
        sys.exit(0)

    # Интерактивный режим
    while True:
        print_banner(env)
        action = questionary.select(
            tr("main_menu"),
            choices=[
                tr("menu_local"),
                tr("menu_url"),
                tr("menu_sync"),
                tr("menu_list"),
                tr("menu_tools"),
                tr("menu_clean"),
                tr("menu_lang"),
                tr("menu_exit"),
            ],
            style=MATRIX_STYLE,
        ).ask()

        if not action or action.startswith("8") or "Exit" in action or "Выход" in action:
            sys.exit(0)

        if action.startswith("7"):
            LANG = "en" if LANG == "ru" else "ru"
            continue

        if action.startswith("6"):
            cleanup_menu(base_dir)
            continue

        if action.startswith("5"):
            env.print_diagnostics()
            questionary.press_any_key_to_continue(style=MATRIX_STYLE).ask()
            continue

        if action.startswith("4"):
            candidates = repo_mgr.discover_patch_candidates()
            if not candidates:
                console.print("[green]Базы патчей еще не скачаны. Выберите пункт 3 для синхронизации.[/green]")
            else:
                table = Table(title="Available Patch Profiles", border_style="bright_green")
                table.add_column("#", style="dim green")
                table.add_column("Profile Name", style="bold bright_green")
                table.add_column("Source Repo", style="bright_green")
                for idx, c in enumerate(candidates, 1):
                    table.add_row(str(idx), c.name, c.parent.parent.name)
                console.print(table)
            questionary.press_any_key_to_continue(style=MATRIX_STYLE).ask()
            continue

        if action.startswith("3"):
            repo_mgr.sync_all()
            questionary.press_any_key_to_continue(style=MATRIX_STYLE).ask()
            continue

        # Сборка GSI (Пункты 1 и 2)
        if action.startswith("1") or action.startswith("2"):
            if not repo_mgr.discover_patch_candidates():
                repo_mgr.sync_all()

            safe_rmtree(work_dir)
            extractor = FirmwareExtractor(env, work_dir)

            if action.startswith("1"):
                raw_path = questionary.text(tr("ask_path"), style=MATRIX_STYLE).ask()
                if not raw_path:
                    continue
                source_path = Path(raw_path.strip("\"'"))
                if not source_path.exists():
                    console.print("[bold bright_green]✗ Указанный файл или папка не существует![/bold bright_green]")
                    questionary.press_any_key_to_continue(style=MATRIX_STYLE).ask()
                    continue
            else:
                rom_url = questionary.text(tr("ask_url"), style=MATRIX_STYLE).ask()
                if not rom_url:
                    continue
                source_path = extractor.download_rom(rom_url.strip())

            mode_choice = questionary.select(
                tr("ask_patch_mode"),
                choices=[tr("mode_auto"), tr("mode_manual")],
                style=MATRIX_STYLE,
            ).ask()
            auto_select_mode = mode_choice == tr("mode_auto")

            fs_choice = questionary.select(
                tr("ask_fs"),
                choices=[tr("fs_ext4"), tr("fs_erofs"), tr("fs_both")],
                style=MATRIX_STYLE,
            ).ask()
            fs_type = "ext4" if fs_choice.startswith("ext4") else ("erofs" if fs_choice.startswith("erofs") else "both")

            enable_debloat = questionary.confirm(tr("ask_debloat"), default=True, style=MATRIX_STYLE).ask()
            split_archive = questionary.confirm(tr("ask_split"), default=False, style=MATRIX_STYLE).ask()

            extractor.process_input(source_path)
            patcher = GSIPatcher(env, base_dir, work_dir, repo_mgr, split_archive=split_archive)
            built_files = patcher.build_gsi(
                auto_select_mode=auto_select_mode, fs_type=fs_type, enable_debloat=enable_debloat
            )

            console.rule(f"[bold bright_green]{tr('build_done')}[/bold bright_green]")
            for bf in built_files:
                console.print(f"[bold bright_green]📦 {bf}[/bold bright_green]")
            questionary.press_any_key_to_continue(style=MATRIX_STYLE).ask()


if __name__ == "__main__":
    main()