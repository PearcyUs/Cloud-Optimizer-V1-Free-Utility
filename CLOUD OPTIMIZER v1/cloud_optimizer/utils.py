# Date: 11/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

import os
import sys
import ctypes
import subprocess

__all__ = ["is_admin", "run_as_admin", "run_hidden_command"]

_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Reexecuta o processo como administrador se ainda não for elevado."""
    try:
        if not is_admin():
            params = ' '.join([f'"{a}"' for a in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)
    except Exception:
        pass


def run_hidden_command(cmd, **kwargs):
    """Executa comandos sem abrir janela de console em sistemas Windows."""
    if os.name == "nt":
        kwargs.setdefault("creationflags", _CREATE_NO_WINDOW)
        startupinfo = kwargs.get("startupinfo")
        if startupinfo is None:
            startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
    return subprocess.run(cmd, **kwargs)
