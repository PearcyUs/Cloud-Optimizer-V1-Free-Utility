# Date: 09/11/2025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

import os
import winreg
import shutil
import ctypes
from typing import List, Dict


def list_startup_programs() -> List[Dict[str, str]]:
    """Lista programas configurados para iniciar com o Windows (registro e pastas Startup)."""
    data: List[Dict[str, str]] = []

    def add_item(name: str, exe: str, value: str, source: str) -> None:
        data.append({
            'name': name or '(Sem nome)',
            'exe': exe or '',
            'value': value or '',
            'source': source,
        })

    reg_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM Run"),
    ]
    for root, sub, src in reg_paths:
        try:
            with winreg.OpenKey(root, sub, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        exe = ''
                        if isinstance(value, str):
                            exe = value.strip().strip('"')
                        add_item(name, exe, str(value), src)
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

    startup_dirs = [
        os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.join(os.environ.get('PROGRAMDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
    ]
    for d in startup_dirs:
        try:
            if d and os.path.isdir(d):
                disabled_dir = r"C:\CloudOptimizerDisabled"
                for fname in os.listdir(d):
                    path = os.path.join(d, fname)
                    # Ignora a pasta de desabilitados
                    if os.path.isdir(path):
                        # pula diretórios (inclusive a pasta de disabled)
                        continue
                    # Ignora tudo que esteja dentro da pasta Disabled
                    if disabled_dir and path.startswith(disabled_dir):
                        continue
                    # Filtra por tipos comuns de inicialização
                    if not fname.lower().endswith((".lnk", ".exe", ".bat", ".cmd", ".vbs", ".ps1", ".ini")):
                        continue
                    add_item(os.path.splitext(fname)[0], path, path, 'Startup Folder')
        except Exception:
            pass

    data.sort(key=lambda x: x['name'].lower())
    return data


def _is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def disable_startup_item(entry: Dict[str, str]) -> bool:
    """Desativa uma entrada da inicialização de acordo com sua origem.

    entry deve conter: name, value, source
    - HKCU Run: remove o valor do registro (usuário atual)
    - HKLM Run: remove o valor do registro (todos os usuários) [requer admin]
    - Startup Folder: move o atalho/arquivo para a pasta r"C:\CloudOptimizerDisabled"
    """
    source = entry.get('source', '')
    name = entry.get('name', '')
    value = entry.get('value', '')

    if source in ("HKCU Run", "HKLM Run"):
        hive = winreg.HKEY_CURRENT_USER if source == "HKCU Run" else winreg.HKEY_LOCAL_MACHINE
        run_subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        disabled_subkey = r"Software\Microsoft\Windows\CurrentVersion\Run\DisabledByCloudOptimizer"

        # HKLM requer admin
        if hive == winreg.HKEY_LOCAL_MACHINE and not _is_admin():
            raise PermissionError("Desabilitar itens em HKLM requer executar como administrador")

        try:
            # Abrir chave Run para ler valor
            with winreg.OpenKey(hive, run_subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key_read:
                try:
                    original_name, original_value, val_type = None, None, None
                    # Tenta ler pelo nome informado
                    original_value, val_type = winreg.QueryValueEx(key_read, name)
                    original_name = name
                except FileNotFoundError:
                    # Pode ter sido listado com name modificado; procura por valor igual
                    i = 0
                    while True:
                        try:
                            vname, vdata, vtype = winreg.EnumValue(key_read, i)
                            if str(vdata).strip() == value.strip():
                                original_name, original_value, val_type = vname, vdata, vtype
                                break
                            i += 1
                        except OSError:
                            break
                    if original_name is None:
                        # Já não existe
                        return True

            # Cria subchave de Disabled e move o valor para lá
            with winreg.CreateKeyEx(hive, disabled_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key_disabled:
                winreg.SetValueEx(key_disabled, original_name, 0, val_type, original_value)

            with winreg.OpenKey(hive, run_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key_mod:
                try:
                    winreg.DeleteValue(key_mod, original_name)
                except FileNotFoundError:
                    pass
            return True
        except OSError as e:
            raise Exception(f"Falha ao mover valor para Disabled: {e}")

    elif source == "Startup Folder":
        path = value
        if not path or not os.path.exists(path):
            # Já não existe
            return True
        base_dir = os.path.dirname(path)
        # Se for diretório (pasta) em vez de arquivo, consideramos já desabilitado
        if os.path.isdir(path):
            return True
        target_dir = r"C:\CloudOptimizerDisabled"
        try:
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, os.path.basename(path))
            # Se já existir, cria um nome alternativo
            if os.path.exists(target_path):
                name_no_ext, ext = os.path.splitext(os.path.basename(path))
                i = 1
                while True:
                    alt = os.path.join(target_dir, f"{name_no_ext} ({i}){ext}")
                    if not os.path.exists(alt):
                        target_path = alt
                        break
                    i += 1
            shutil.move(path, target_path)
            return True
        except Exception as e:
            raise Exception(f"Falha ao mover arquivo da pasta Startup: {e}")

    else:
        # Fonte desconhecida
        raise Exception(f"Fonte desconhecida: {source}")


def _startup_dirs() -> List[str]:
    return [
        os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.join(os.environ.get('PROGRAMDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
    ]


def list_disabled_startup_items() -> List[Dict[str, str]]:
    """Lista arquivos e valores de registro desativados."""
    items: List[Dict[str, str]] = []
    for base in _startup_dirs():
        try:
            if not base or not os.path.isdir(base):
                continue
            disabled_dir = r"C:\CloudOptimizerDisabled"
            if not os.path.isdir(disabled_dir):
                continue
            for fname in os.listdir(disabled_dir):
                path = os.path.join(disabled_dir, fname)
                if os.path.isdir(path):
                    continue
                items.append({
                    'name': os.path.splitext(fname)[0],
                    'path': path,
                    'base': base,
                    'source': 'Startup Folder',
                })
        except Exception:
            continue
    # Também lista valores do registro movidos para a subchave DisabledByCloudOptimizer
    for hive, source in [
        (winreg.HKEY_CURRENT_USER, 'HKCU Run'),
        (winreg.HKEY_LOCAL_MACHINE, 'HKLM Run'),
    ]:
        try:
            disabled_subkey = r"Software\Microsoft\Windows\CurrentVersion\Run\DisabledByCloudOptimizer"
            with winreg.OpenKey(hive, disabled_subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
                i = 0
                while True:
                    try:
                        vname, vdata, vtype = winreg.EnumValue(k, i)
                        items.append({
                            'name': vname,
                            'path': str(vdata),
                            'base': disabled_subkey,
                            'source': source,
                            'kind': 'registry',
                            'hive': 'HKCU' if hive == winreg.HKEY_CURRENT_USER else 'HKLM',
                        })
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

    items.sort(key=lambda x: x['name'].lower())
    return items


def restore_startup_item(entry: Dict[str, str]) -> bool:
    """Restaura arquivo da pasta Disabled ou valor de registro para Run."""
    kind = entry.get('kind', 'file')
    if kind == 'registry':
        hive = winreg.HKEY_CURRENT_USER if entry.get('hive') == 'HKCU' else winreg.HKEY_LOCAL_MACHINE
        # HKLM requer admin
        if hive == winreg.HKEY_LOCAL_MACHINE and not _is_admin():
            raise PermissionError("Restaurar itens em HKLM requer executar como administrador")

        disabled_subkey = r"Software\Microsoft\Windows\CurrentVersion\Run\DisabledByCloudOptimizer"
        run_subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        name = entry.get('name', '')
        try:
            with winreg.OpenKey(hive, disabled_subkey, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as kd:
                value, vtype = winreg.QueryValueEx(kd, name)
                # Escreve de volta em Run
                with winreg.OpenKey(hive, run_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as kr:
                    winreg.SetValueEx(kr, name, 0, vtype, value)
                # Remove do Disabled
                try:
                    winreg.DeleteValue(kd, name)
                except FileNotFoundError:
                    pass
            return True
        except OSError as e:
            raise Exception(f"Falha ao restaurar valor do registro: {e}")
    else:
        path = entry.get('path', '')
        base = entry.get('base', '')
        if not path or not os.path.exists(path):
            return True
        if not base:
            base = os.path.dirname(os.path.dirname(path))
        try:
            os.makedirs(base, exist_ok=True)
            target = os.path.join(base, os.path.basename(path))
            if os.path.exists(target):
                name_no_ext, ext = os.path.splitext(os.path.basename(path))
                i = 1
                while True:
                    alt = os.path.join(base, f"{name_no_ext} (restored {i}){ext}")
                    if not os.path.exists(alt):
                        target = alt
                        break
                    i += 1
            shutil.move(path, target)
            return True
        except Exception as e:
            raise Exception(f"Falha ao restaurar item: {e}")


def create_test_startup_entries() -> Dict[str, bool]:

    results = {"HKCU": False, "HKLM": False}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as k:
            winreg.SetValueEx(k, "CloudOptTest_User", 0, winreg.REG_SZ, "notepad.exe")
            results["HKCU"] = True
    except OSError:
        pass

    if _is_admin():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as k:
                winreg.SetValueEx(k, "CloudOptTest_System", 0, winreg.REG_SZ, "notepad.exe")
                results["HKLM"] = True
        except OSError:
            pass
    return results


def remove_test_startup_entries() -> Dict[str, bool]:
    """Remove entradas de teste criadas por create_test_startup_entries."""
    results = {"HKCU": False, "HKLM": False}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as k:
            try:
                winreg.DeleteValue(k, "CloudOptTest_User")
                results["HKCU"] = True
            except FileNotFoundError:
                pass
    except OSError:
        pass

    if _is_admin():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as k:
                try:
                    winreg.DeleteValue(k, "CloudOptTest_System")
                    results["HKLM"] = True
                except FileNotFoundError:
                    pass
        except OSError:
            pass
    return results

