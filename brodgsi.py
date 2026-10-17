#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrodGSI Tool v3.0 - Universal Cross-Platform GSI Builder & Multi-Repo Patch Engine
Features:
  - Auto ROM & Android Version Detection (build.prop & filesystem heuristics)
  - Patch Scoring Engine (Auto-selects the most comprehensive patch or offers manual choice)
  - Automatic Fallback to Generic Treble patches
  - Bilingual TUI Interface (Russian / English)
  - Supports: Windows, Linux, macOS (x64 & arm64)
"""

import os
import re
import sys
import shlex
import shutil
import struct
import tarfile
import zipfile
import platform
import subprocess
import urllib.parse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import requests
import brotli
import lz4.frame
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)

console = Console()

# ==========================================
# СИСТЕМА ЛОКАЛИЗАЦИИ (RU / EN)
# ==========================================
I18N = {
    "ru": {
        "subtitle": "Кроссплатформенный сборщик GSI с автоопределением прошивки",
        "os_arch": "ОС и Архитектура:",
        "repos_label": "Базы патчей:",
        "formats_label": "Форматы:",
        "main_menu": "Главное меню:",
        "menu_local": "1. Собрать GSI из локального файла (архив или образ)",
        "menu_url": "2. Собрать GSI по прямой ссылке (URL)",
        "menu_sync": "3. Скачать / Обновить базы патчей (MysticGSI, OriginGSI, ErfanGSI, yaebuebu)",
        "menu_list": "4. Показать каталог прошивок и объем патчей в базах",
        "menu_tools": "5. Проверить системные бинарные утилиты",
        "menu_lang": "6. Сменить язык / Change Language (RU/EN)",
        "menu_exit": "7. Выход",
        "sync_rule": "Синхронизация баз патчей из 4 GSI-проектов",
        "git_missing": "Ошибка: Утилита git не найдена в системе! Установите Git для скачивания баз патчей.",
        "updating": "Обновление",
        "cloning": "Клонирование",
        "repo_skip": "Репозиторий недоступен или пропущен",
        "repo_ok": "База успешно загружена!",
        "repos_empty_ask": "Папка repos/ пуста. Скачать патчи из всех 4 репозиториев прямо сейчас?",
        "enter_path": "Укажите путь к файлу прошивки или образу:",
        "file_not_found": "Ошибка: Файл не найден!",
        "enter_url": "Введите прямую ссылку (URL) на прошивку:",
        "select_fs": "Выберите файловую систему для финального GSI:",
        "fs_ext4": "ext4 (Read/Write, максимальная совместимость)",
        "fs_erofs": "erofs (Read-Only, минимальный размер образа - Android 11+)",
        "fs_both": "Сделать оба образа (и ext4, и erofs)",
        "ask_debloat": "Применить списки деблоата (удаление мусора OEM)?",
        "select_patch_mode": "Выберите режим подбора патчей для прошивки:",
        "mode_auto": "Автовыбор (применить вариант патча с наибольшим количеством изменений)",
        "mode_manual": "Ручной выбор (выбрать из списка подходящих вариантов, если их несколько)",
        "stage1": "Этап 1: Рекурсивная распаковка контейнеров прошивки",
        "stage2": "Этап 2: Извлечение и слияние разделов в единый System",
        "stage3": "Этап 3: Автоопределение прошивки и применение патчей",
        "stage4": "Этап 4: Генерация SELinux и упаковка бутабельного GSI",
        "detected_rom": "Автоопределение прошивки:",
        "no_specific_patches": "Специфичные патчи для этой прошивки не найдены. Используются универсальные Generic-патчи!",
        "multiple_patches_found": "Найдено несколько вариантов патчей для",
        "choose_patch_variant": "Выберите вариант патча (указан индекс объема изменений):",
        "auto_selected_patch": "Автовыбор выбрал самый полный набор патчей:",
        "score_details": "очков изменений",
        "build_done": "Готовый бутабельный GSI образ создан:",
        "menu_clean": "7. Очистка рабочих папок",
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
    },
    "en": {
        "subtitle": "Cross-Platform GSI Builder with Auto ROM Detection",
        "os_arch": "OS & Architecture:",
        "repos_label": "Patch Databases:",
        "formats_label": "Formats:",
        "main_menu": "Main Menu:",
        "menu_local": "1. Build GSI from local file (archive or image)",
        "menu_url": "2. Build GSI from direct URL",
        "menu_sync": "3. Download / Update patch repos (MysticGSI, OriginGSI, ErfanGSI, yaebuebu)",
        "menu_list": "4. Show supported ROM profiles & patch scores",
        "menu_tools": "5. Check required binary tools",
        "menu_lang": "6. Change Language / Сменить язык (EN/RU)",
        "menu_exit": "7. Exit",
        "sync_rule": "Synchronizing patch databases from 4 GSI projects",
        "git_missing": "Error: 'git' utility not found! Please install Git to clone patch repositories.",
        "updating": "Updating",
        "cloning": "Cloning",
        "repo_skip": "Repository unavailable or skipped",
        "repo_ok": "Database loaded successfully!",
        "repos_empty_ask": "The repos/ folder is empty. Download patches from all 4 repositories now?",
        "enter_path": "Enter path to firmware archive or image:",
        "file_not_found": "Error: File not found!",
        "enter_url": "Enter direct firmware URL:",
        "select_fs": "Select target filesystem for final GSI:",
        "fs_ext4": "ext4 (Read/Write, maximum compatibility)",
        "fs_erofs": "erofs (Read-Only, minimal image size - Android 11+)",
        "fs_both": "Build both images (ext4 and erofs)",
        "ask_debloat": "Apply debloat lists (remove OEM bloatware)?",
        "select_patch_mode": "Select patch selection mode:",
        "mode_auto": "Auto-select (pick the patch variant with the most modifications/highest score)",
        "mode_manual": "Manual choice (choose from available variants if multiple exist)",
        "stage1": "Stage 1: Recursive container & archive extraction",
        "stage2": "Stage 2: Extracting & merging partitions into unified System",
        "stage3": "Stage 3: Auto-detecting ROM & applying patches",
        "stage4": "Stage 4: SELinux context generation & bootable GSI packing",
        "detected_rom": "Auto-detected firmware:",
        "no_specific_patches": "No ROM-specific patches found. Falling back to universal Generic patches!",
        "multiple_patches_found": "Multiple patch variants found for",
        "choose_patch_variant": "Select patch variant to apply (sorted by modification volume score):",
        "auto_selected_patch": "Auto-select picked the most comprehensive patch set:",
        "score_details": "modification points",
        "build_done": "Bootable GSI image successfully built:",
        "menu_clean": "7. Clean workspace directories",
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
    },
}

LANG = "ru"


def tr(key: str) -> str:
    return I18N.get(LANG, I18N["ru"]).get(key, key)

import stat

def remove_readonly(func, path, exc_info):
    """Корректно добавляет права на запись для удаления файлов как на Windows, так и на Linux."""
    try:
        # Добавляем бит записи, не трогая остальные права
        os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
        func(path)
    except Exception:
        func(path)

# Полный список разделов
TARGET_PARTITIONS = [
    "system", "product", "system_ext", "mi_ext", "odm_ext", "vendor",
    "opproduct", "my_product", "my_heytap", "my_stock", "my_bigball",
    "my_carrier", "my_region", "my_manifest", "prism", "optics", "india", "reserve"
]

MERGE_TO_SYSTEM = [
    "product", "system_ext", "mi_ext", "odm_ext",
    "opproduct", "my_product", "my_heytap", "my_stock", "my_bigball",
    "my_carrier", "my_region", "my_manifest", "prism", "optics"
]

PATCH_REPOS = {
    "mysticgsi": "https://github.com/MysticGSI/mysticgsi.git",
    "yaebuebugsitool": "https://github.com/radgoodnow/yaebuebugsitool.git",
    "ErfanGSIs": "https://github.com/erfanoabdi/ErfanGSIs.git",
    "OriginGSITool": "https://github.com/defnotegor/OriginGSITool.git",
}

# Сигнатуры для автоматического распознавания типа прошивки по build.prop и папкам
ROM_SIGNATURES = [
    ("HyperOS", [r"ro\.mi\.os\.version", r"ro\.build\.version\.incremental=OS1", r"ro\.build\.version\.incremental=OS2"]),
    ("MIUI", [r"ro\.miui\.ui\.version", r"ro\.miui\.cust_variant"]),
    ("OneUI", [r"ro\.build\.version\.oneui", r"ro\.build\.PDA", r"ro\.config\.knox"]),
    ("ColorOS", [r"ro\.build\.version\.oplusrom", r"ro\.build\.version\.opporom", r"ro\.oplus\.version"]),
    ("OxygenOS", [r"ro\.oxygen\.version", r"ro\.rom\.version=Oxygen"]),
    ("RealmeUI", [r"ro\.build\.version\.realmeui"]),
    ("MagicOS", [r"ro\.build\.version\.magic", r"msc\.config\.magic"]),
    ("EMUI", [r"ro\.build\.version\.emui", r"ro\.confg\.hw_systemversion"]),
    ("OriginOS", [r"ro\.vivo\.os\.version", r"ro\.vivo\.os\.name", r"ro\.vivo\.product\.version"]),
    ("Flyme", [r"ro\.build\.user=flyme", r"ro\.flyme\.published", r"ro\.meizu\.build"]),
    ("RedMagicOS", [r"ro\.build\.nubia\.rom\.name", r"ro\.nubia\.version"]),
    ("MyUI", [r"ro\.mot\.build", r"ro\.build\.Characteristics=motorola"]),
    ("ROG", [r"ro\.build\.asus\.sku", r"ro\.asus\.rog"]),
    ("NothingOS", [r"ro\.nothing\.version", r"ro\.build\.nothing"]),
    ("Pixel", [r"ro\.product\.brand=google", r"ro\.build\.flavor=.*pixel", r" com\.google\.android\.apps\.nexuslauncher"]),
]


class PlatformEnv:
    """Управление окружением ОС, архитектурой (x64/arm64) и внешними утилитами."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.sys_name = platform.system().lower()
        machine = platform.machine().lower()
        
        if machine in ["x86_64", "amd64"]:
            self.arch = "amd64"
        elif machine in ["aarch64", "arm64"]:
            self.arch = "arm64"
        else:
            self.arch = machine

        self.platform_tag = f"{self.sys_name}_{self.arch}"
        self.bin_dir = self.base_dir / "bin" / self.platform_tag
        self.ext = ".exe" if self.sys_name == "windows" else ""

    def get_tool(self, name: str) -> str:
        """Ищет бинарную утилиту в папке bin локально или в системе."""
        candidates = [self.bin_dir / f"{name}{self.ext}", self.bin_dir / f"{name}.jar"]
        for local_bin in candidates:
            if local_bin.exists():
                if self.sys_name != "windows" and local_bin.suffix != ".jar":
                    os.chmod(local_bin, 0o755)
                return str(local_bin)
        return shutil.which(name) or shutil.which(f"{name}.bat") or ""


    def cleanup_menu(base_dir: Path):
        """Интерактивное меню очистки рабочих папок с поддержкой локализации."""
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

        action = questionary.select(tr("clean_title"), choices=choices).ask()
        if not action or action.startswith("5") or "Back" in action or "Назад" in action:
            return

        if action.startswith("1") or action.startswith("4"):
            if workspace_dir.exists():
                shutil.rmtree(workspace_dir, onerror=remove_readonly)
                console.print(f"[green]{tr('clean_ws_done')}[/green]")
            else:
                console.print(f"[yellow]{tr('clean_ws_empty')}[/yellow]")

        if action.startswith("2") or action.startswith("4"):
            if output_dir.exists():
                shutil.rmtree(output_dir, onerror=remove_readonly)
                console.print(f"[green]{tr('clean_out_done')}[/green]")
            else:
                console.print(f"[yellow]{tr('clean_out_empty')}[/yellow]")

        if action.startswith("3") or action.startswith("4"):
            if repos_dir.exists():
                shutil.rmtree(repos_dir, onerror=remove_readonly)
                console.print(f"[green]{tr('clean_repos_done')}[/green]")
            else:
                console.print(f"[yellow]{tr('clean_repos_empty')}[/yellow]")

        questionary.press_any_key_to_continue().ask()
    

    def run_cmd(self, cmd: List[str], cwd: Optional[Path] = None, env_vars: Optional[Dict[str, str]] = None, check: bool = True) -> subprocess.CompletedProcess:
        full_env = os.environ.copy()
        if env_vars:
            full_env.update(env_vars)
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=full_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check
        )


class PatchCandidate:
    """Представляет конкретный вариант патча из одного из репозиториев с расчетом объема изменений."""
    def __init__(self, repo_name: str, rom_name: str, android_ver: str, path: Path):
        self.repo_name = repo_name
        self.rom_name = rom_name
        self.android_ver = android_ver
        self.path = path
        self.score, self.summary = self._calculate_modification_score()

    def _calculate_modification_score(self) -> Tuple[int, str]:
        """
        Оценивает объем изменений в папке патча:
        - Количество непустых строк в .sh, .prop, .patch, file_contexts, debloat
        - Количество файлов оверлеев/библиотек/аппок для замены
        """
        score = 0
        script_lines = 0
        overlay_files = 0
        smali_patches = 0

        for item in self.path.rglob("*"):
            if not item.is_file():
                continue
            ext = item.suffix.lower()
            name = item.name.lower()
            if ext in [".sh", ".prop", ".txt"] or "context" in name or "debloat" in name:
                try:
                    lines = [
                        l.strip() for l in item.read_text(encoding="utf-8", errors="ignore").splitlines()
                        if l.strip() and not l.strip().startswith("#")
                    ]
                    script_lines += len(lines)
                    score += len(lines) * 2
                except Exception:
                    pass
            elif ext in [".patch", ".diff"]:
                try:
                    lines = item.read_text(encoding="utf-8", errors="ignore").splitlines()
                    smali_patches += 1
                    score += len(lines) * 3
                except Exception:
                    pass
            else:
                overlay_files += 1
                score += 15  # Каждый бинарник/оверлей/apk весит 15 очков

        summary = f"Score: {score} (Files: {overlay_files}, Script/Prop lines: {script_lines}, Smali diffs: {smali_patches})"
        return score, summary


class RepoSyncManager:
    """Менеджер синхронизации и индексации 4 репозиториев с патчами."""
    def __init__(self, env: PlatformEnv, base_dir: Path):
        self.env = env
        self.repos_dir = base_dir / "repos"
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def sync_all(self):
        git_bin = self.env.get_tool("git")
        if not git_bin:
            console.print(f"[bold red]{tr('git_missing')}[/bold red]")
            return

        git_env = os.environ.copy()
        git_env["GIT_TERMINAL_PROMPT"] = "0"
        git_env["GCM_INTERACTIVE"] = "never"

        console.rule(f"[bold cyan]{tr('sync_rule')}")
        for name, url in PATCH_REPOS.items():
            target_dir = self.repos_dir / name
            if target_dir.exists() and not (target_dir / ".git").exists():
                shutil.rmtree(target_dir, onerror=remove_readonly)

            if (target_dir / ".git").exists():
                console.log(f"[cyan]{tr('updating')} {name}...[/cyan]")
                subprocess.run([git_bin, "pull"], cwd=str(target_dir), env=git_env, check=False)
            else:
                console.log(f"[cyan]{tr('cloning')} {name} ({url})...[/cyan]")
                # Используем --filter=blob:none и --sparse для мгновенного клонирования без скачивания внутренностей
                res = subprocess.run(
                    [git_bin, "clone", "--filter=blob:none", "--sparse", "--depth=1", url, str(target_dir)],
                    env=git_env, check=False
                )
                
                if res.returncode == 0:
                    # Указываем, какие конкретно папки нам нужны для каждого репо
                    if name.lower() == "mysticgsi":
                        sparse_dirs = ["patches"]
                    else:
                        sparse_dirs = ["ROMsPatches", "roms", "Patches", "prebuilt", "common"]
                    
                    # Говорим гиту скачать только их
                    subprocess.run(
                        [git_bin, "sparse-checkout", "set"] + sparse_dirs,
                        cwd=str(target_dir), env=git_env, check=False
                    )
                    console.log(f"[green]✓ {name}: {tr('repo_ok')} (Только патчи)[/green]")
                else:
                    console.log(f"[yellow]⚠ {tr('repo_skip')}: {name}[/yellow]")
                    if target_dir.exists():
                        shutil.rmtree(target_dir, onerror=remove_readonly)

    def find_candidates(self, rom_type: str, target_android_ver: str) -> List[PatchCandidate]:
        aliases = {
            "hyperos": ["hyperos", "miui"],
            "miui": ["miui", "hyperos"],
            "oxygenos": ["oxygenos", "coloros", "realmeui", "oos"],
            "coloros": ["coloros", "oxygenos", "realmeui"],
            "realmeui": ["realmeui", "coloros", "oxygenos"],
            "oneui": ["oneui", "samsung"],
            "pixel": ["pixel", "generic"],
            "magicos": ["magicos", "magicui", "emui"],
            "emui": ["emui", "magicui", "magicos"],
            "originos": ["originos", "funtouchos", "vivo"],
        }
        search_names = aliases.get(rom_type.lower(), [rom_type.lower()])
        candidates: List[PatchCandidate] = []

        mystic_root = self.repos_dir / "mysticgsi" / "patches"
        if mystic_root.exists():
            for d in mystic_root.iterdir():
                if d.is_dir() and d.name.lower() in search_names:
                    candidates.append(PatchCandidate("MysticGSI", d.name, "Universal", d))

        for repo in ["OriginGSITool", "yaebuebugsitool", "ErfanGSIs"]:
            r_path = self.repos_dir / repo
            for sub in ["ROMsPatches", "roms"]:
                s_root = r_path / sub
                if not s_root.exists():
                    continue
                for ver_dir in s_root.iterdir():
                    if not ver_dir.is_dir():
                        continue
                    for rom_d in ver_dir.iterdir():
                        if rom_d.is_dir() and rom_d.name.lower() in search_names:
                            cand = PatchCandidate(repo, rom_d.name, ver_dir.name, rom_d)
                            if ver_dir.name == target_android_ver:
                                cand.score += 500
                                cand.summary += f" [Exact Android {target_android_ver} Match +500]"
                            candidates.append(cand)

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates

    def list_all_profiles(self) -> List[PatchCandidate]:
        all_cands: List[PatchCandidate] = []
        mystic_root = self.repos_dir / "mysticgsi" / "patches"
        if mystic_root.exists():
            for d in mystic_root.iterdir():
                if d.is_dir() and not d.name.startswith("_"):
                    all_cands.append(PatchCandidate("MysticGSI", d.name, "All", d))

        for repo in ["OriginGSITool", "yaebuebugsitool", "ErfanGSIs"]:
            r_path = self.repos_dir / repo
            for sub in ["ROMsPatches", "roms"]:
                s_root = r_path / sub
                if s_root.exists():
                    for ver_dir in s_root.iterdir():
                        if ver_dir.is_dir():
                            for rom_d in ver_dir.iterdir():
                                if rom_d.is_dir():
                                    all_cands.append(PatchCandidate(repo, rom_d.name, ver_dir.name, rom_d))
        all_cands.sort(key=lambda x: (x.rom_name.lower(), -x.score))
        return all_cands
        
        for repo in ["OriginGSITool", "yaebuebugsitool", "ErfanGSIs"]:
            r_path = self.repos_dir / repo
            for sub in ["ROMsPatches", "roms"]:
                s_root = r_path / sub
                if s_root.exists():
                    for ver_dir in s_root.iterdir():
                        if ver_dir.is_dir():
                            for rom_d in ver_dir.iterdir():
                                if rom_d.is_dir():
                                    all_cands.append(PatchCandidate(repo, rom_d.name, ver_dir.name, rom_d))
        all_cands.sort(key=lambda x: (x.rom_name.lower(), -x.score))
        return all_cands


class PureParsers:
    """Чистые Python-парсеры для sdat2img, Huawei UPDATE.APP и Samsung LZ4."""
    @staticmethod
    def sdat2img(transfer_list_path: Path, dat_file_path: Path, output_img_path: Path):
        BLOCK_SIZE = 4096
        with open(transfer_list_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        version = int(lines[0])
        cmd_start = 4 if version >= 2 else 2

        commands = []
        for line in lines[cmd_start:]:
            if not line:
                continue
            parts = line.split(" ")
            cmd = parts[0]
            if cmd in ["new", "zero", "erase"]:
                nums = [int(x) for x in parts[1].split(",")]
                ranges = [(nums[i], nums[i + 1]) for i in range(1, len(nums), 2)]
                commands.append((cmd, ranges))

        with open(dat_file_path, "rb") as dat_f, open(output_img_path, "wb") as out_f:
            max_block = 0
            for cmd, ranges in commands:
                for start, end in ranges:
                    if end > max_block:
                        max_block = end
                    if cmd == "new":
                        block_count = end - start
                        out_f.seek(start * BLOCK_SIZE)
                        out_f.write(dat_f.read(block_count * BLOCK_SIZE))
            if max_block > 0:
                out_f.seek(max_block * BLOCK_SIZE - 1)
                out_f.write(b"\x00")

    @staticmethod
    def extract_huawei_update_app(update_app_path: Path, out_dir: Path):
        with open(update_app_path, "rb") as f:
            data = f.read()

        magic = b"\x55\xAA\x5A\xA5"
        offset = 0
        while True:
            idx = data.find(magic, offset)
            if idx == -1:
                break
            try:
                header_size = struct.unpack("<I", data[idx + 4 : idx + 8])[0]
                data_size = struct.unpack("<I", data[idx + 24 : idx + 28])[0]
                part_name_raw = data[idx + 60 : idx + 92]
                part_name = part_name_raw.split(b"\x00")[0].decode("ascii", errors="ignore").lower()
                
                if any(t in part_name for t in TARGET_PARTITIONS + ["super"]):
                    img_offset = idx + header_size
                    out_file = out_dir / f"{part_name}.img"
                    with open(out_file, "wb") as out_f:
                        out_f.write(data[img_offset : img_offset + data_size])
                offset = idx + header_size + data_size
            except Exception:
                offset = idx + 4

    @staticmethod
    def decompress_lz4_file(lz4_path: Path, out_path: Path):
        with open(lz4_path, "rb") as f_in, open(out_path, "wb") as f_out:
            decompressor = lz4.frame.LZ4FrameDecompressor()
            while chunk := f_in.read(64 * 1024 * 1024):
                f_out.write(decompressor.decompress(chunk))


class UniversalExtractor:
    """Универсальный распаковщик любых архивов и образов прошивок."""
    def __init__(self, env: PlatformEnv, work_dir: Path):
        self.env = env
        self.work_dir = work_dir
        self.raw_dir = work_dir / "01_extracted_containers"
        self.img_dir = work_dir / "02_partition_images"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)

    def detect_magic(self, file_path: Path) -> str:
        if not file_path.is_file() or file_path.stat().st_size < 16:
            return "unknown"

        with open(file_path, "rb") as f:
            head = f.read(4096)

        if head.startswith(b"PK\x03\x04"):
            return "zip"
        if head.startswith(b"\x1f\x8b"):
            return "gzip"
        if head.startswith(b"7z\xbc\xaf\x27\x1c"):
            return "7z"
        if head.startswith(b"\x28\xb5\x2f\xfd"):
            return "zstd"
        if head.startswith(b"\x04\x22\x4d\x18"):
            return "lz4"
        if head.startswith(b"CrAU"):
            return "payload"
        if head.startswith(b"\x3a\xff\x26\xed"):
            return "sparse_img"
        if len(head) > 262 and head[257:262] == b"ustar":
            return "tar"
        if len(head) >= 1080 and head[1080:1082] == b"\x53\xef":
            return "ext4"
        if len(head) >= 1028 and head[1024:1028] == b"\xe2\xe1\xf5\xe0":
            return "erofs"
        if len(head) >= 1028 and head[1024:1028] == b"\x10\x20\xf5\xf2":
            return "f2fs"
        if b"\x55\xAA\x5A\xA5" in head[:256]:
            return "update_app"
        if len(head) >= 4096 and (head[4096 - 4 : 4096] == b"gLpD" or b"gLpH" in head):
            return "super_raw"

        name = file_path.name.lower()
        if name.endswith(".new.dat.br"):
            return "dat_br"
        if name.endswith(".new.dat"):
            return "dat"
        return "unknown"

    def process_input(self, source_path: Path):
        console.rule(f"[bold cyan]{tr('stage1')}")
        self._handle_file(source_path, self.raw_dir)
        
        for _ in range(5):
            files = list(self.raw_dir.rglob("*"))
            progressed = False
            for f in files:
                if f.is_file() and self._process_intermediate(f):
                    progressed = True
            if not progressed:
                break

        self._collect_final_images()

    def _handle_file(self, f_path: Path, dest: Path):
        ftype = self.detect_magic(f_path)
        console.log(f"[bold]{f_path.name}[/bold] -> [yellow]{ftype.upper()}[/yellow]")

        if ftype == "zip":
            with zipfile.ZipFile(f_path, "r") as zf:
                zf.extractall(dest)
        elif ftype in ["gzip", "tar"]:
            try:
                with tarfile.open(f_path, "r:*") as tf:
                    tf.extractall(dest)
            except Exception:
                seven_z = self.env.get_tool("7z")
                if seven_z:
                    self.env.run_cmd([seven_z, "x", str(f_path), f"-o{dest}", "-y"])
        elif ftype == "7z":
            seven_z = self.env.get_tool("7z")
            if not seven_z:
                raise RuntimeError("7z binary required!")
            self.env.run_cmd([seven_z, "x", str(f_path), f"-o{dest}", "-y"])
        else:
            shutil.copy2(f_path, dest / f_path.name)

    def _process_intermediate(self, f_path: Path) -> bool:
        ftype = self.detect_magic(f_path)
        name_lower = f_path.name.lower()

        if ftype in ["zip", "gzip", "tar"] and not name_lower.endswith(".img"):
            self._handle_file(f_path, f_path.parent)
            f_path.unlink()
            return True

        if ftype == "lz4":
            out_name = f_path.name[:-4] if name_lower.endswith(".lz4") else f"{f_path.name}.raw"
            out_path = f_path.parent / out_name
            PureParsers.decompress_lz4_file(f_path, out_path)
            f_path.unlink()
            return True

        if ftype == "payload":
            dumper = self.env.get_tool("payload-dumper-go")
            if not dumper:
                raise RuntimeError("payload-dumper-go required in bin/!")
            self.env.run_cmd([dumper, "-o", str(self.img_dir), str(f_path)])
            f_path.unlink()
            return True

        if ftype == "update_app":
            PureParsers.extract_huawei_update_app(f_path, self.raw_dir)
            f_path.unlink()
            return True

        if ftype == "dat_br":
            out_dat = f_path.parent / f_path.name[:-3]
            with open(f_path, "rb") as f_in, open(out_dat, "wb") as f_out:
                decompressor = brotli.Decompressor()
                while chunk := f_in.read(64 * 1024 * 1024):
                    f_out.write(decompressor.process(chunk))
            f_path.unlink()
            return True

        if ftype == "dat":
            prefix = f_path.name.replace(".new.dat", "")
            t_list = f_path.parent / f"{prefix}.transfer.list"
            if t_list.exists():
                out_img = self.img_dir / f"{prefix}.img"
                PureParsers.sdat2img(t_list, f_path, out_img)
                f_path.unlink()
                return True

        if ftype == "sparse_img":
            simg2img = self.env.get_tool("simg2img")
            if simg2img:
                raw_img = f_path.parent / f"{f_path.stem}_raw.img"
                self.env.run_cmd([simg2img, str(f_path), str(raw_img)])
                f_path.unlink()
                raw_img.rename(f_path)
                return True

        if "super" in name_lower and ftype in ["super_raw", "unknown"] and f_path.stat().st_size > 100 * 1024 * 1024:
            lpunpack = self.env.get_tool("lpunpack")
            if lpunpack:
                self.env.run_cmd([lpunpack, str(f_path), str(self.img_dir)])
                f_path.unlink()
                return True

        return False

    def _collect_final_images(self):
        for f in list(self.raw_dir.rglob("*")) + list(self.img_dir.rglob("*")):
            if not f.is_file():
                continue
            ftype = self.detect_magic(f)
            if ftype in ["ext4", "erofs", "f2fs"]:
                clean_name = f.stem.lower()
                for suffix in ["_a", "_b", "_raw"]:
                    if clean_name.endswith(suffix):
                        clean_name = clean_name[: -len(suffix)]
                
                for target in TARGET_PARTITIONS:
                    if clean_name == target or clean_name.startswith(f"{target}."):
                        dest_img = self.img_dir / f"{target}.img"
                        if f != dest_img and f.stat().st_size > 2 * 1024 * 1024:
                            shutil.move(str(f), str(dest_img))
                            console.log(f"[green]✓ Partition Ready:[/green] {dest_img.name} ({ftype.upper()})")


class UniversalPatchEngine:
    """
    Движок автоопределения прошивки, выбора оптимального патча и кроссплатформенного применения модификаций.
    """
    def __init__(self, env: PlatformEnv, base_dir: Path, repo_mgr: RepoSyncManager, sys_root: Path, inner_sys: Path):
        self.env = env
        self.base_dir = base_dir
        self.repos_dir = base_dir / "repos"
        self.repo_mgr = repo_mgr
        self.sys_root = sys_root
        self.inner_sys = inner_sys
        self.extra_file_contexts: List[str] = []
        self.sdk_ver, self.android_ver, self.detected_rom = self._auto_detect_firmware_info()

    def _auto_detect_firmware_info(self) -> Tuple[str, str, str]:
        """Автоматически определяет версию Android, SDK и название оболочки (HyperOS, OneUI, Pixel, ColorOS и т.д.)."""
        sdk, ver = "34", "14"
        combined_props = ""

        for prop_file in self.sys_root.rglob("*.prop"):
            if prop_file.is_file():
                try:
                    combined_props += "\n" + prop_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    pass

        m_sdk = re.search(r"ro\.build\.version\.sdk=(\d+)", combined_props)
        m_ver = re.search(r"ro\.build\.version\.release=([^\s\n]+)", combined_props)
        if m_sdk:
            sdk = m_sdk.group(1)
        if m_ver:
            ver = m_ver.group(1).split(".")[0]

        # Определение оболочки по регулярным выражениям
        detected_rom = "Generic"
        for rom_name, patterns in ROM_SIGNATURES:
            if any(re.search(pat, combined_props, re.IGNORECASE) for pat in patterns):
                detected_rom = rom_name
                break

        # Дополнительная эвристика по специфичным папкам разделов, если prop замаскирован
        if detected_rom == "Generic":
            if (self.inner_sys / "mi_ext").exists() or (self.inner_sys / "app" / "MiuiSystemUI").exists():
                detected_rom = "HyperOS" if int(ver) >= 14 else "MIUI"
            elif (self.inner_sys / "prism").exists() or (self.inner_sys / "priv-app" / "SystemUISamsung").exists():
                detected_rom = "OneUI"
            elif (self.inner_sys / "my_heytap").exists() or (self.inner_sys / "my_product").exists():
                detected_rom = "ColorOS"

        console.print(
            Panel(
                f"[bold green]{tr('detected_rom')}[/bold green] [bold yellow]{detected_rom}[/bold yellow] "
                f"(Android [bold cyan]{ver}[/bold cyan] / SDK [bold cyan]{sdk}[/bold cyan])",
                border_style="green",
            )
        )
        return sdk, ver, detected_rom

    def resolve_and_apply_patches(self, auto_select_mode: bool = True, enable_debloat: bool = True) -> str:
        """
        Подбирает патчи под обнаруженную прошивку:
        - Всегда накладывает базовый Generic/Prebuilt слой Treble.
        - Ищет патчи для конкретной прошивки.
        - Если их нет -> остается на Generic.
        - Если найдено несколько -> либо автовыбирает вариант с максимальным Score, либо спрашивает пользователя.
        """
        # 1. Всегда применяем базовые Treble-патчи (Generic / Prebuilt)
        self._apply_common_treble_overlays()

        # 2. Ищем кандидатов под конкретную обнаруженную прошивку
        candidates = self.repo_mgr.find_candidates(self.detected_rom, self.android_ver)

        if not candidates:
            console.print(f"[bold yellow]⚠ {tr('no_specific_patches')}[/bold yellow]")
            return "Generic"

        chosen_candidates: List[PatchCandidate] = []

        if len(candidates) == 1:
            chosen_candidates = [candidates[0]]
            console.log(f"[green]✓ Выбран патч:[/green] {candidates[0].repo_name}/{candidates[0].rom_name} ({candidates[0].summary})")
        else:
            if auto_select_mode:
                best = candidates[0]  # Уже отсортировано по убыванию score
                chosen_candidates = [best]
                console.print(
                    f"[bold cyan]★ {tr('auto_selected_patch')}[/bold cyan] "
                    f"[bold yellow]{best.repo_name} -> {best.rom_name} (A{best.android_ver})[/bold yellow] "
                    f"[{best.score} {tr('score_details')}]"
                )
            else:
                console.print(f"[bold cyan]{tr('multiple_patches_found')} {self.detected_rom}:[/bold cyan]")
                choices = []
                cand_map = {}
                for idx, c in enumerate(candidates, 1):
                    label = f"{idx}. [{c.repo_name} | A{c.android_ver}] {c.rom_name} — {c.summary}"
                    choices.append(label)
                    cand_map[label] = [c]
                
                all_label = f"★ Применить ВСЕ найденные патчи по очереди ({len(candidates)} шт.) / Apply ALL sequentially"
                choices.insert(0, all_label)
                cand_map[all_label] = candidates

                ans = questionary.select(tr("choose_patch_variant"), choices=choices).ask()
                chosen_candidates = cand_map.get(ans, [candidates[0]])

        for cand in chosen_candidates:
            console.rule(f"[bold yellow]Patching: {cand.repo_name} ({cand.rom_name} / A{cand.android_ver})")
            self._process_patch_directory(cand.path, enable_debloat=enable_debloat)

        return self.detected_rom

    def _apply_common_treble_overlays(self):
        common_candidates = [
            self.base_dir / "patches",
            self.repos_dir / "mysticgsi" / "patches" / "generic",
            self.repos_dir / "mysticgsi" / "patches" / "common",
            self.repos_dir / "OriginGSITool" / "Patches" / "common",
            self.repos_dir / "OriginGSITool" / "Patches" / self.android_ver,
            self.repos_dir / "yaebuebugsitool" / "Patches" / "common",
            self.repos_dir / "ErfanGSIs" / "prebuilt" / "common",
            self.repos_dir / "ErfanGSIs" / "prebuilt" / self.android_ver,
        ]
        for c_dir in common_candidates:
            if c_dir.exists():
                console.log(f"[cyan]Generic Treble Layer:[/cyan] {c_dir.relative_to(self.base_dir)}")
                self._process_patch_directory(c_dir, enable_debloat=False)

    def _process_patch_directory(self, patch_dir: Path, enable_debloat: bool):
        for folder_name in ["system", "product", "system_ext", "overlay"]:
            src_tree = patch_dir / folder_name
            if src_tree.exists() and src_tree.is_dir():
                dest_tree = self.inner_sys if folder_name == "system" else self.inner_sys / folder_name
                shutil.copytree(src_tree, dest_tree, dirs_exist_ok=True)

        for prop_file in patch_dir.rglob("*.prop"):
            self._merge_prop_file(prop_file)

        for fc_file in patch_dir.rglob("*file_contexts*"):
            if fc_file.is_file():
                lines = [l.strip() for l in fc_file.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
                self.extra_file_contexts.extend(lines)

        if enable_debloat:
            for deb_file in list(patch_dir.glob("*debloat*")):
                if deb_file.is_file():
                    self._execute_debloat_file(deb_file)

        for sh_file in sorted(patch_dir.glob("*.sh")):
            if "debloat" in sh_file.name.lower():
                continue
            self._execute_or_transpile_shell_script(sh_file)

        for diff_file in patch_dir.rglob("*.patch"):
            self._apply_smali_or_text_patch(diff_file)

    def _merge_prop_file(self, prop_file: Path):
        target_prop = self.inner_sys / "build.prop"
        if not target_prop.exists():
            return

        new_lines = [
            l.strip() for l in prop_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            if l.strip() and not l.strip().startswith("#") and "=" in l
        ]
        if not new_lines:
            return

        orig_text = target_prop.read_text(encoding="utf-8", errors="ignore")
        appended = []
        for line in new_lines:
            key = line.split("=", 1)[0].strip()
            if re.search(rf"^{re.escape(key)}=", orig_text, flags=re.MULTILINE):
                orig_text = re.sub(rf"^{re.escape(key)}=.*$", line, orig_text, flags=re.MULTILINE)
            else:
                appended.append(line)

        if appended:
            orig_text += f"\n# Patched from {prop_file.name}\n" + "\n".join(appended) + "\n"
        target_prop.write_text(orig_text, encoding="utf-8")

    def _execute_debloat_file(self, deb_file: Path):
        content = deb_file.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cleaned = re.sub(r"^rm\s+(-[rf]+\s+)?", "", line)
            for token in shlex.split(cleaned, posix=True):
                rel_path = token
                for prefix in ["$1/", "${1}/", "$systemdir/system/", "$systemdir/", "/system/", "system/"]:
                    if rel_path.startswith(prefix):
                        rel_path = rel_path[len(prefix):]
                rel_path = rel_path.lstrip("/")
                if not rel_path:
                    continue
                target = self.inner_sys / rel_path
                if target.exists():
                    shutil.rmtree(target, onerror=remove_readonly) if (target.is_dir() and not target.is_symlink()) else target.unlink(missing_ok=True)

    def _execute_or_transpile_shell_script(self, sh_file: Path):
        bash_bin = self.env.get_tool("bash")
        if bash_bin and self.env.sys_name in ["linux", "darwin"]:
            env_vars = {
                "systemdir": str(self.inner_sys),
                "romdir": str(self.sys_root),
            }
            self.env.run_cmd([bash_bin, str(sh_file), str(self.inner_sys)], cwd=sh_file.parent, env_vars=env_vars, check=False)
            return

        lines = sh_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in lines:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("rm "):
                cleaned = re.sub(r"^rm\s+(-[rf]+\s+)?", "", s)
                for token in shlex.split(cleaned, posix=True):
                    rel = token.replace("$1/", "").replace("${1}/", "").lstrip("/")
                    target = self.inner_sys / rel
                    if target.exists():
                        shutil.rmtree(target, onerror=remove_readonly) if target.is_dir() else target.unlink(missing_ok=True)
            elif ">>" in s and "build.prop" in s:
                m = re.search(r'echo\s+["\']?([^"\'>]+)["\']?\s*>>', s)
                if m:
                    prop_str = m.group(1).strip()
                    bprop = self.inner_sys / "build.prop"
                    if bprop.exists() and "=" in prop_str:
                        with open(bprop, "a", encoding="utf-8") as bf:
                            bf.write(f"\n{prop_str}\n")
            elif s.startswith("sed -i"):
                m = re.search(r"s/([^/]+)/([^/]*)/g?\s+([^\s]+)", s)
                if m:
                    old_pat, new_val, target_f = m.group(1), m.group(2), m.group(3)
                    target_f = target_f.replace("$1/", "").replace("${1}/", "").lstrip("/")
                    f_path = self.inner_sys / target_f
                    if f_path.exists() and f_path.is_file():
                        txt = f_path.read_text(encoding="utf-8", errors="ignore")
                        f_path.write_text(txt.replace(old_pat, new_val), encoding="utf-8")

    def _process_patch_directory(self, patch_dir: Path, enable_debloat: bool):
        for folder_name in ["system", "product", "system_ext", "overlay"]:
            src_tree = patch_dir / folder_name
            if src_tree.exists() and src_tree.is_dir():
                dest_tree = self.inner_sys if folder_name == "system" else self.inner_sys / folder_name
                shutil.copytree(src_tree, dest_tree, dirs_exist_ok=True)

        for prop_file in patch_dir.rglob("*.prop"):
            self._merge_prop_file(prop_file)

        for fc_file in patch_dir.rglob("*file_contexts*"):
            if fc_file.is_file():
                lines = [l.strip() for l in fc_file.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
                self.extra_file_contexts.extend(lines)

        if enable_debloat:
            for deb_file in list(patch_dir.glob("*debloat*")):
                if deb_file.is_file():
                    self._execute_debloat_file(deb_file)

        for sh_file in sorted(patch_dir.glob("*.sh")):
            if "debloat" in sh_file.name.lower():
                continue
            self._execute_or_transpile_shell_script(sh_file)

        for diff_file in patch_dir.rglob("*.patch"):
            self._apply_smali_or_text_patch(diff_file)

        # Вызываем штамповку подписи во всех build.prop после наложения патчей
        self._stamp_build_properties()

    def _stamp_build_properties(self):
        """Прописывает PortedByBrodGSI_<дата> в поля id, display.id и description всех build.prop."""
        import datetime
        date_tag = datetime.datetime.now().strftime("%Y%m%d")
        stamp_value = f"PortedByBrodGSI_{date_tag}"

        prop_files = list(self.inner_sys.rglob("build.prop"))
        for pf in prop_files:
            try:
                text = pf.read_text(encoding="utf-8", errors="ignore")
                modified = text
                
                # Ищем стандартные ключи номеров сборок и заменяем их значения
                keys_to_stamp = [
                    "ro.build.display.id",
                    "ro.build.id",
                    "ro.vendor.build.id",
                    "ro.product.build.id",
                    "ro.system.build.id",
                    "ro.system_ext.build.id",
                    "ro.odm.build.id",
                ]
                
                for key in keys_to_stamp:
                    pattern = rf"^({re.escape(key)}=).*$"
                    if re.search(pattern, modified, flags=re.MULTILINE):
                        modified = re.sub(pattern, rf"\1{stamp_value}", modified, flags=re.MULTILINE)
                    else:
                        # Если ключа не было, добавляем его
                        modified += f"\n{key}={stamp_value}\n"

                if modified != text:
                    pf.write_text(modified, encoding="utf-8")
                    console.log(f"[green]✓ Проставлена подпись сборки в:[/green] {pf.relative_to(self.inner_sys)}")
            except Exception as e:
                console.log(f"[yellow]⚠ Ошибка штамповки {pf.name}: {e}[/yellow]")

    def _apply_smali_or_text_patch(self, patch_file: Path):
        apktool_path = self.env.get_tool("apktool")
        patch_bin = self.env.get_tool("patch")
        
        # Исправлено: корректное определение target_jar для текущего патча
        target_jar = None
        p_str = patch_file.as_posix().lower()
        if "services" in p_str:
            target_jar = self.inner_sys / "framework" / "services.jar"
        elif "framework" in p_str:
            target_jar = self.inner_sys / "framework" / "framework.jar"

        if apktool_path and apktool_path.endswith(".jar"):
            apktool_cmd = ["java", "-jar", apktool_path]
        else:
            apktool_cmd = [apktool_path] if apktool_path else []

        if target_jar and target_jar.exists() and apktool_cmd and patch_bin:
            console.log(f"[cyan]Smali-патчинг {target_jar.name} -> {patch_file.name}...[/cyan]")
            tmp_decode = self.sys_root.parent / f"apktool_{target_jar.stem}"
            if not tmp_decode.exists():
                self.env.run_cmd(apktool_cmd + ["d", "-f", str(target_jar), "-o", str(tmp_decode)], check=False)
            self.env.run_cmd([patch_bin, "-p1", "-d", str(tmp_decode), "-i", str(patch_file)], check=False)
            self.env.run_cmd(apktool_cmd + ["b", str(tmp_decode), "-o", str(target_jar)], check=False)


class GSIPatcher:
    """Главный сборщик образа GSI."""
    def __init__(self, env: PlatformEnv, repo_mgr: RepoSyncManager, work_dir: Path, base_dir: Path):
        self.env = env
        self.repo_mgr = repo_mgr
        self.work_dir = work_dir
        self.base_dir = base_dir
        self.img_dir = work_dir / "02_partition_images"
        self.fs_dir = work_dir / "03_filesystem"
        self.config_dir = work_dir / "04_fs_config"
        self.out_dir = base_dir / "output"
        
        self.fs_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def build_gsi(self, auto_select_mode: bool = True, fs_type: str = "ext4", enable_debloat: bool = True) -> list:
        console.rule(f"[bold cyan]{tr('stage2')}")
        
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
                console.log(f"[cyan]Merging {part}.img -> /system/{part}...[/cyan]")
                target_part_dir = inner_sys / part
                if target_part_dir.is_symlink() or target_part_dir.is_file():
                    target_part_dir.unlink()
                elif target_part_dir.is_dir():
                    shutil.rmtree(target_part_dir, ignore_errors=True)
                
                self.unpack_partition(part, part_img, target_part_dir)
                
                root_link = sys_root / part
                if root_link.exists() or root_link.is_symlink():
                    if root_link.is_dir() and not root_link.is_symlink():
                        shutil.rmtree(root_link, ignore_errors=True)
                    else:
                        root_link.unlink()
                try:
                    os.symlink(f"/system/{part}", root_link)
                except OSError:
                    pass

        console.rule(f"[bold cyan]{tr('stage3')}")
        patch_engine = UniversalPatchEngine(self.env, self.base_dir, self.repo_mgr, sys_root, inner_sys)
        final_rom_label = patch_engine.resolve_and_apply_patches(auto_select_mode=auto_select_mode, enable_debloat=enable_debloat)
        self._apply_mandatory_boot_fixes(sys_root, inner_sys)

        console.rule(f"[bold cyan]{tr('stage4')}")
        fs_types = ["ext4", "erofs"] if fs_type == "both" else [fs_type]
        output_images = []
        for fst in fs_types:
            out_img = self._repack_image(sys_root, final_rom_label, patch_engine.android_ver, fst, patch_engine.extra_file_contexts)
            output_images.append(out_img)
            
        return output_images

    def unpack_partition(self, part_name: str, img_path: Path, target_extract_dir: Path):
        magic = UniversalExtractor(self.env, self.work_dir).detect_magic(img_path)
        target_extract_dir.mkdir(parents=True, exist_ok=True)

        if magic == "erofs":
            extract_erofs = self.env.get_tool("extract.erofs")
            if extract_erofs:
                self.env.run_cmd([extract_erofs, "-i", str(img_path), "-x", "-o", str(target_extract_dir)])
                return

        seven_z = self.env.get_tool("7z")
        if not seven_z:
            raise RuntimeError("7z or extract.erofs required in bin/!")
        self.env.run_cmd([seven_z, "x", str(img_path), f"-o{target_extract_dir}", "-y"], check=False)

    def _apply_mandatory_boot_fixes(self, sys_root: Path, inner_sys: Path):
        for rc_or_fstab in list(sys_root.rglob("*.rc")) + list(sys_root.rglob("*fstab*")):
            if not rc_or_fstab.is_file():
                continue
            try:
                text = rc_or_fstab.read_text(encoding="utf-8", errors="ignore")
                modified = text
                for flag in [",avb=vbmeta", ",avb", "avb_keys=", "forceencrypt=", "fileencryption=", ",quota"]:
                    modified = modified.replace(flag, "")
                if modified != text:
                    rc_or_fstab.write_text(modified, encoding="utf-8")
            except Exception:
                pass

        for rec_file in ["recovery-from-boot.p", "bin/install-recovery.sh", "etc/install-recovery.sh"]:
            target = inner_sys / rec_file
            if target.exists():
                target.unlink()

    def _generate_fs_and_selinux_configs(self, sys_root: Path, extra_contexts: List[str]) -> Tuple[Path, Path]:
        fs_config_file = self.config_dir / "fs_config.txt"
        file_contexts_file = self.config_dir / "file_contexts.txt"

        fs_lines = ["/ 0 0 0755", "lost+found 0 0 0700"]
        fc_lines = [
            "/ u:object_r:rootfs:s0",
            "/lost\\+found u:object_r:rootfs:s0",
            "/system(/.*)? u:object_r:system_file:s0",
            "/system/bin/.* u:object_r:system_file:s0",
            "/system/bin/init u:object_r:init_exec:s0",
            "/system/bin/sh u:object_r:shell_exec:s0",
            "/system/bin/rw-system\\.sh u:object_r:phhsu_exec:s0",
            "/system/lib(64)?(/.*)? u:object_r:system_lib_file:s0",
            "/system/product(/.*)? u:object_r:system_file:s0",
            "/system/system_ext(/.*)? u:object_r:system_file:s0",
            "/system/mi_ext(/.*)? u:object_r:system_file:s0",
        ]
        fc_lines.extend(extra_contexts)

        for item in sys_root.rglob("*"):
            rel = item.relative_to(sys_root).as_posix()
            if item.is_symlink():
                fs_lines.append(f"{rel} 0 0 0777 {os.readlink(item)}")
            elif item.is_dir():
                fs_lines.append(f"{rel} 0 0 0755")
            else:
                if "/bin/" in f"/{rel}" or "/xbin/" in f"/{rel}" or rel.endswith(".sh"):
                    fs_lines.append(f"{rel} 0 2000 0755")
                else:
                    fs_lines.append(f"{rel} 0 0 0644")

        fs_config_file.write_text("\n".join(fs_lines) + "\n", encoding="utf-8")
        file_contexts_file.write_text("\n".join(dict.fromkeys(fc_lines)) + "\n", encoding="utf-8")
        return fs_config_file, file_contexts_file

    def _repack_image(self, sys_root: Path, rom_label: str, android_ver: str, fs_type: str, extra_contexts: List[str]) -> Path:
        fs_config, file_contexts = self._generate_fs_and_selinux_configs(sys_root, extra_contexts)
        output_gsi = self.out_dir / f"BrodGSI-{rom_label}-A{android_ver}-AB-{fs_type.upper()}.img"
        if output_gsi.exists():
            output_gsi.unlink()

        if fs_type == "erofs":
            mkfs_erofs = self.env.get_tool("mkfs.erofs")
            if not mkfs_erofs:
                raise RuntimeError("mkfs.erofs not found in bin/!")
            self.env.run_cmd([
                mkfs_erofs, "-zlz4hc,9", "-T", "1230768000",
                "--mount-point=/",
                f"--fs-config-file={fs_config}",
                f"--file-contexts={file_contexts}",
                str(output_gsi), str(sys_root),
            ])
        else:
            total_bytes = sum(f.stat().st_size for f in sys_root.rglob("*") if f.is_file() and not f.is_symlink())
            img_size_mb = int((total_bytes * 1.15) / (1024 * 1024)) + 150
            mke2fs = self.env.get_tool("mke2fs")
            e2fsdroid = self.env.get_tool("e2fsdroid")
            if not mke2fs:
                raise RuntimeError("mke2fs not found in bin/!")

            self.env.run_cmd([
                mke2fs, "-O", "^has_journal", "-L", "/", "-I", "256",
                "-M", "/", "-m", "0", "-t", "ext4", "-b", "4096",
                "-d", str(sys_root), str(output_gsi), f"{img_size_mb}M"
            ])
            if e2fsdroid:
                self.env.run_cmd([
                    e2fsdroid, "-e", "-T", "1230768000",
                    "-C", str(fs_config), "-S", str(file_contexts),
                    "-f", str(sys_root), "-a", "/", str(output_gsi)
                ], check=False)

        console.log(f"[bold green]✓ {tr('build_done')}[/bold green] {output_gsi}")
        return output_gsi


def download_firmware(url: str, dest_folder: Path) -> Path:
    dest_folder.mkdir(parents=True, exist_ok=True)
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path) or "firmware_archive.bin"
    dest_path = dest_folder / filename

    with requests.get(url, stream=True, allow_redirects=True, timeout=30) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%", "•",
            DownloadColumn(), "•", TransferSpeedColumn(), "•", TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("download", filename=filename, total=total_size)
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
    return dest_path

def cleanup_menu(base_dir: Path):
    """Интерактивное меню очистки рабочих папок с поддержкой локализации."""
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

    action = questionary.select(tr("clean_title"), choices=choices).ask()
    if not action or action.startswith("5") or "Back" in action or "Назад" in action:
        return

    if action.startswith("1") or action.startswith("4"):
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir, onerror=remove_readonly)
            console.print(f"[green]{tr('clean_ws_done')}[/green]")
        else:
            console.print(f"[yellow]{tr('clean_ws_empty')}[/yellow]")

    if action.startswith("2") or action.startswith("4"):
        if output_dir.exists():
            shutil.rmtree(output_dir, onerror=remove_readonly)
            console.print(f"[green]{tr('clean_out_done')}[/green]")
        else:
            console.print(f"[yellow]{tr('clean_out_empty')}[/yellow]")

    if action.startswith("3") or action.startswith("4"):
        if repos_dir.exists():
            shutil.rmtree(repos_dir, onerror=remove_readonly)
            console.print(f"[green]{tr('clean_repos_done')}[/green]")
        else:
            console.print(f"[yellow]{tr('clean_repos_empty')}[/yellow]")

    questionary.press_any_key_to_continue().ask()



def main():
    global LANG
    base_dir = Path(__file__).resolve().parent
    env = PlatformEnv(base_dir)
    repo_mgr = RepoSyncManager(env, base_dir)

    # Первичный выбор языка при старте
    lang_ans = questionary.select(
        "Выберите язык интерфейса / Select interface language:",
        choices=["Русский (RU)", "English (EN)"]
    ).ask()
    if lang_ans and "EN" in lang_ans:
        LANG = "en"

    while True:
        console.clear()
        info = Table.grid(padding=(0, 2))
        info.add_column(style="bold cyan")
        info.add_column(style="white")
        info.add_row(tr("os_arch"), f"{env.sys_name.upper()} ({env.arch})")
        info.add_row(tr("repos_label"), "MysticGSI • yaebuebugsitool • ErfanGSIs • OriginGSITool")
        info.add_row(tr("formats_label"), "ZIP, TGZ, Payload, Super, .new.dat.br, UPDATE.APP, AP.tar, EROFS/EXT4/F2FS")
        console.print(Panel(info, title="[bold green]BrodGSI Tool v3.0", subtitle=f"[italic]{tr('subtitle')}", border_style="cyan"))

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
        ).ask()

        # Обработка выхода (теперь это пункт 8)
        if not action or action.startswith("8") or "Exit" in action or "Выход" in action:
            sys.exit(0)

        # Обработка смены языка
        if action == tr("menu_lang") or "Language" in action or "язык" in action:
            LANG = "en" if LANG == "ru" else "ru"
            continue

        # Обработка очистки папок
        if action == tr("menu_clean") or "Clean" in action or "Очистка" in action:
            cleanup_menu(base_dir)
            continue
            
        if not action or action.startswith("7"):
            sys.exit(0)

        if action.startswith("6"):
            LANG = "en" if LANG == "ru" else "ru"
            continue

        if action.startswith("3"):
            repo_mgr.sync_all()
            questionary.press_any_key_to_continue().ask()
            continue

        if action.startswith("4"):
            profiles = repo_mgr.list_all_profiles()
            if not profiles:
                console.print(f"[yellow]{tr('repos_empty_ask')}[/yellow]")
            else:
                t = Table(title="ROM Profiles & Modification Volume Scores")
                t.add_column("ROM", style="bold green")
                t.add_column("Source Repo", style="cyan")
                t.add_column("Android", style="yellow")
                t.add_column("Modification Score", style="white")
                for p in profiles:
                    t.add_row(p.rom_name, p.repo_name, p.android_ver, p.summary)
                console.print(t)
            questionary.press_any_key_to_continue().ask()
            continue

        if action.startswith("5"):
            tools = ["git", "7z", "simg2img", "lpunpack", "payload-dumper-go", "mke2fs", "e2fsdroid", "mkfs.erofs", "extract.erofs", "apktool"]
            t_table = Table(title=f"Tools Status ({env.platform_tag})")
            t_table.add_column("Tool", style="cyan")
            t_table.add_column("Status", style="bold")
            t_table.add_column("Path")
            for t in tools:
                path = env.get_tool(t)
                status = "[green]OK[/green]" if path else "[red]Missing[/red]"
                t_table.add_row(t, status, path or f"bin/{env.platform_tag}/")
            console.print(t_table)
            questionary.press_any_key_to_continue().ask()
            continue

        # Проверка наличия склонированных баз патчей перед сборкой
        if not repo_mgr.list_all_profiles():
            if questionary.confirm(tr("repos_empty_ask"), default=True).ask():
                repo_mgr.sync_all()

        work_dir = base_dir / "workspace"
        if work_dir.exists():
            shutil.rmtree(work_dir, onerror=remove_readonly)
        work_dir.mkdir(parents=True, exist_ok=True)

        if action.startswith("1"):
            file_input = questionary.path(tr("enter_path")).ask()
            if not file_input:
                continue
            source_path = Path(file_input.strip("\"'")).resolve()
            if not source_path.exists():
                console.print(f"[bold red]{tr('file_not_found')}[/bold red]")
                questionary.press_any_key_to_continue().ask()
                continue
        else:
            url_input = questionary.text(tr("enter_url")).ask()
            if not url_input:
                continue
            source_path = download_firmware(url_input.strip(), work_dir / "00_downloads")

        mode_choice = questionary.select(
            tr("select_patch_mode"),
            choices=[tr("mode_auto"), tr("mode_manual")],
        ).ask()
        auto_select_mode = mode_choice == tr("mode_auto")

        fs_choice = questionary.select(
            tr("select_fs"),
            choices=[tr("fs_ext4"), tr("fs_erofs"), tr("fs_both")],
        ).ask()
        
        if "both" in fs_choice.lower() or "оба" in fs_choice.lower():
            fs_type = "both"
        else:
            fs_type = "erofs" if "erofs" in fs_choice else "ext4"
            
        enable_debloat = questionary.confirm(tr("ask_debloat"), default=True).ask()

        extractor = UniversalExtractor(env, work_dir)
        extractor.process_input(source_path)

        patcher = GSIPatcher(env, repo_mgr, work_dir, base_dir)
        patcher.build_gsi(auto_select_mode=auto_select_mode, fs_type=fs_type, enable_debloat=enable_debloat)


if __name__ == "__main__":
    main()