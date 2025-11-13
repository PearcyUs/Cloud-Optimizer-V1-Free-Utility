# Date: 12/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

import os
import winreg
import ctypes
import shutil

__all__ = [
    "set_high_performance",
    "clean_temp_files",
    "optimize_network",
    "optimize_services",
    "disable_visual_effects",
    "disable_useless_programs",
    "is_admin",
]
from cloud_optimizer.utils import run_hidden_command

def is_admin():
    """Verifica se o programa está rodando com privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def set_high_performance():
    """Ativa plano de energia de alto desempenho e remove timeouts."""
    if not is_admin():
        raise PermissionError("Requer privilégios de administrador")
    
    try:
        # GUID do plano High Performance
        high_perf_guid = '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
        result = run_hidden_command(
            ['powercfg', '/setactive', high_perf_guid],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode != 0:
            raise Exception(f"Falha ao ativar plano: {result.stderr}")
        
        # Remove timeouts de economia de energia
        for cmd, value in [
            ('monitor-timeout-ac', '0'),
            ('disk-timeout-ac', '0'),
            ('standby-timeout-ac', '0'),
            ('hibernate-timeout-ac', '0'),
        ]:
            run_hidden_command(
                ['powercfg', '/change', cmd, value],
                capture_output=True,
                check=False,
            )
        
        return True
    except Exception as e:
        raise Exception(f"Erro ao configurar desempenho máximo: {str(e)}")

def clean_temp_files():
    """Remove arquivos temporários do sistema (TEMP, TMP, Prefetch, logs)."""
    deleted = 0
    errors = []
    
    # Pastas a limpar
    folders = [
        os.environ.get('TEMP'),
        os.environ.get('TMP'),
        r'C:\Windows\Temp',
        r'C:\Windows\Prefetch',
        r'C:\Windows\Logs',
    ]
    
    for folder in folders:
        if not folder or not os.path.exists(folder):
            continue
        
        try:
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        deleted += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                        deleted += 1
                except Exception:
                    pass  # Arquivo em uso, pula
        except Exception as e:
            errors.append(f"{folder}: {str(e)}")
    
    if deleted == 0 and errors:
        raise Exception(f"Nenhum arquivo removido. Erros: {'; '.join(errors)}")
    
    return True

def optimize_network():
    """Otimiza configurações de rede TCP/IP e limpa cache DNS."""
    if not is_admin():
        raise PermissionError("Requer privilégios de administrador")
    
    try:
        commands = [
            # Auto-tuning para melhor throughput
            ['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'],
            # Chimney offload (reduz CPU)
            ['netsh', 'int', 'tcp', 'set', 'global', 'chimney=enabled'],
            # RSS (Receive Side Scaling)
            ['netsh', 'int', 'tcp', 'set', 'global', 'rss=enabled'],
            # Limpa cache DNS
            ['ipconfig', '/flushdns'],
            # Renova IP (opcional, pode causar breve desconexão)
            # ['ipconfig', '/release'],
            # ['ipconfig', '/renew'],
        ]
        
        for cmd in commands:
            result = run_hidden_command(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0 and 'flushdns' not in cmd:
                raise Exception(f"Comando falhou: {' '.join(cmd)}")
        
        return True
    except Exception as e:
        raise Exception(f"Erro ao otimizar rede: {str(e)}")

def optimize_services():
    """Desativa serviços desnecessários (telemetria, indexação, etc)."""
    if not is_admin():
        raise PermissionError("Requer privilégios de administrador")
    
    services = {
        'DiagTrack': 'Telemetria do Windows',
        'dmwappushservice': 'Push de apps da Store',
        'SysMain': 'SuperFetch/Prefetch',
        'WSearch': 'Indexação Windows Search',
    }
    
    disabled = []
    errors = []
    
    for svc, desc in services.items():
        try:
            # Para o serviço
            run_hidden_command(['sc', 'stop', svc], capture_output=True, check=False)
            
            # Desabilita inicialização automática
            result = run_hidden_command(
                ['sc', 'config', svc, 'start=disabled'],
                capture_output=True,
                text=True,
                check=False,
            )
            
            if result.returncode == 0:
                disabled.append(desc)
            else:
                errors.append(f"{desc}: {result.stderr.strip()}")
        except Exception as e:
            errors.append(f"{desc}: {str(e)}")
    
    if not disabled and errors:
        raise Exception(f"Nenhum serviço desativado. Erros: {'; '.join(errors)}")
    
    return True

def disable_visual_effects():
    """Desativa efeitos visuais do Windows para melhor desempenho."""
    try:
        # Chave principal de efeitos visuais
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # 2 = Ajustar para melhor desempenho
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        
        # Desabilita animações e transparências específicas
        adv_key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        adv_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, adv_key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # Configurações de desempenho
        settings = {
            'TaskbarAnimations': 0,        # Sem animações na barra de tarefas
            'ListviewAlphaSelect': 0,      # Sem seleção com sombra
            'ListviewShadow': 0,           # Sem sombra em ícones
            'TaskbarSmallIcons': 1,        # Ícones pequenos (menos espaço)
        }
        
        for name, value in settings.items():
            winreg.SetValueEx(adv_key, name, 0, winreg.REG_DWORD, value)
        
        winreg.CloseKey(adv_key)
        
        # UserPreferencesMask para desabilitar mais efeitos
        dwm_key_path = r"Control Panel\Desktop"
        dwm_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, dwm_key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # Desabilita menu de animação
        winreg.SetValueEx(dwm_key, "UserPreferencesMask", 0, winreg.REG_BINARY, 
                         bytes([0x90, 0x12, 0x03, 0x80, 0x10, 0x00, 0x00, 0x00]))
        
        winreg.CloseKey(dwm_key)
        
        return True
    except Exception as e:
        raise Exception(f"Erro ao desativar efeitos visuais: {str(e)}")

def disable_useless_programs():
    """Remove programas comuns da inicialização (OneDrive, Skype, Teams, Spotify)."""
    targets = ['OneDrive', 'Skype', 'Teams', 'Spotify']
    removed = []
    
    # Remove do registro de inicialização
    for hive, path in [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]:
        try:
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if any(t.lower() in name.lower() or t.lower() in str(value).lower() for t in targets):
                        try:
                            winreg.DeleteValue(key, name)
                            removed.append(name)
                        except Exception:
                            pass
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    
    # Desabilita tarefas agendadas comuns
    if is_admin():
        for target in targets:
            try:
                # Lista tarefas que contenham o nome do app
                result = run_hidden_command(
                    ['schtasks', '/query', '/fo', 'LIST'],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                
                if target.lower() in result.stdout.lower():
                    # Desabilita a tarefa (não deleta, apenas desativa)
                    run_hidden_command(
                        ['schtasks', '/change', '/tn', f'*{target}*', '/disable'],
                        capture_output=True,
                        check=False,
                    )
            except Exception:
                pass
    
    if not removed:
        raise Exception("Nenhum programa encontrado na inicialização")
    
    return True
