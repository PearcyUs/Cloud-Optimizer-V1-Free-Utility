# Date: 10/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

import shutil
import time
import psutil

from cloud_optimizer.utils import run_hidden_command


class Monitor:
    """Coletor de métricas do sistema com estado para deltas (disco/rede)."""

    def __init__(self) -> None:
        self._prev_disk = None
        self._prev_net = None
        self._prev_ts = None
        self._gpu_cli = self._detect_gpu_cli()
        self._last_cpu_pct = 0.0

    def get_metrics(self) -> dict:
        """Retorna um dicionário com métricas atuais e strings formatadas.
        Campos:
          - cpu_pct (float)
          - ram_used_gb (float)
          - ram_pct (float)
          - gpu_txt (str)
          - temp_txt (str)
          - disk_mb_s (float)
          - net_mbit_s (float)
          - formatted: {CPU,RAM,GPU,Temp,Disco,Rede}
        """
        out = {
            'cpu_pct': 0.0,
            'ram_used_gb': 0.0,
            'ram_pct': 0.0,
            'gpu_txt': 'N/A',
            'temp_txt': 'N/A',
            'disk_mb_s': 0.0,
            'net_mbit_s': 0.0,
        }
        try:
            # CPU
            cpu_times = psutil.cpu_times_percent(interval=0.3, percpu=False)
            cpu_idle = getattr(cpu_times, 'idle', None)
            if cpu_idle is not None:
                cpu = max(0.0, min(100.0, 100.0 - float(cpu_idle)))
            else:
                cpu = psutil.cpu_percent(interval=None)

            if cpu <= 0.01 and self._last_cpu_pct > 0.0:
                cpu = self._last_cpu_pct * 0.92

            self._last_cpu_pct = float(cpu)
            out['cpu_pct'] = self._last_cpu_pct

            # RAM
            vm = psutil.virtual_memory()
            out['ram_used_gb'] = vm.used / (1024 ** 3)
            out['ram_pct'] = float(vm.percent)

            # GPU
            out['gpu_txt'] = self._read_gpu_usage()

            # Temperatura CPU
            temp_txt = 'N/A'
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for key in ['coretemp', 'cpu-thermal', 'Package id 0']:
                        arr = temps.get(key)
                        if arr:
                            vals = [t.current for t in arr if getattr(t, 'current', None)]
                            if vals:
                                temp_txt = f"{sum(vals) / len(vals):.0f}°C"
                                break
            except Exception:
                pass
            # Fallback WMI (Windows)
            if temp_txt == 'N/A':
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\\wmi")
                    sensors = w.MSAcpi_ThermalZoneTemperature()
                    if sensors:
                        # WMI retorna temperatura em décimos de Kelvin
                        kelvin = sensors[0].CurrentTemperature
                        celsius = kelvin / 10.0 - 273.15
                        temp_txt = f"{celsius:.0f}°C"
                except Exception:
                    pass
            out['temp_txt'] = temp_txt

            # Disco e Rede (delta por segundo)
            now = time.time()
            if self._prev_disk is None:
                self._prev_disk = psutil.disk_io_counters()
            if self._prev_net is None:
                self._prev_net = psutil.net_io_counters()
            if self._prev_ts is None:
                self._prev_ts = now

            dt = max(0.001, now - self._prev_ts)
            disk = psutil.disk_io_counters()
            net = psutil.net_io_counters()

            disk_bytes = ((disk.read_bytes - self._prev_disk.read_bytes) + (disk.write_bytes - self._prev_disk.write_bytes)) / dt
            out['disk_mb_s'] = disk_bytes / (1024 ** 2)

            net_bytes = ((net.bytes_sent - self._prev_net.bytes_sent) + (net.bytes_recv - self._prev_net.bytes_recv)) / dt
            out['net_mbit_s'] = (net_bytes * 8) / (1024 ** 2)

            self._prev_disk = disk
            self._prev_net = net
            self._prev_ts = now
        except Exception:
            pass

        out['formatted'] = {
            'CPU': f"{out['cpu_pct']:.0f}%",
            'RAM': f"{out['ram_used_gb']:.1f} GB",
            'GPU': out['gpu_txt'],
            'Temp': out['temp_txt'],
            'Disco': f"{out['disk_mb_s']:.1f} MB/s",
            'Rede': f"{out['net_mbit_s']:.2f} Mb/s",
        }
        return out

    def _detect_gpu_cli(self):
        try:
            return shutil.which('nvidia-smi')
        except Exception:
            return None

    def _read_gpu_usage(self) -> str:
        if not self._gpu_cli:
            return 'N/A'
        try:
            result = run_hidden_command(
                [self._gpu_cli, '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return 'N/A'
            output = result.stdout.strip().splitlines()
            if not output:
                return 'N/A'
            value = output[0].strip()
            if not value:
                return 'N/A'
            return f"{float(value):.0f}%"
        except Exception:
            return 'N/A'
