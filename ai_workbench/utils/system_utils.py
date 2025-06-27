"""
System Utilities for AI Workbench

This module provides utility functions for gathering system information,
performing health checks, and other system-related operations.
"""

import os
import sys
import platform
import subprocess
import psutil
import socket
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import logging

# Set up logging
logger = logging.getLogger(__name__)


def get_system_info() -> Dict[str, Any]:
    """
    Gather comprehensive system information
    
    Returns:
        Dictionary containing system information
    """
    try:
        # Basic system info
        sys_info = {
            'os': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
            },
            'cpu': get_cpu_info(),
            'memory': get_memory_info(),
            'disks': get_disk_info(),
            'network': get_network_info(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'users': [u.name for u in psutil.users()],
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return sys_info
        
    except Exception as e:
        logger.error(f"Error gathering system info: {e}")
        return {'error': str(e)}

def get_cpu_info() -> Dict[str, Any]:
    """Get CPU information"""
    try:
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'max_frequency': psutil.cpu_freq().max if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None,
            'min_frequency': psutil.cpu_freq().min if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None,
            'current_frequency': psutil.cpu_freq().current if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None,
            'cpu_percent': psutil.cpu_percent(interval=1, percpu=False),
            'cpu_percent_per_cpu': psutil.cpu_percent(interval=1, percpu=True),
            'cpu_stats': dict(psutil.cpu_stats()._asdict()) if hasattr(psutil, 'cpu_stats') else {},
            'cpu_times': {k: v for k, v in psutil.cpu_times()._asdict().items()}
        }
        
        # Add CPU times per CPU if available
        if hasattr(psutil, 'cpu_times_percent') and callable(psutil.cpu_times_percent):
            cpu_times_percent = psutil.cpu_times_percent(interval=1, percpu=True)
            cpu_info['cpu_times_percent'] = [
                {k: getattr(times, k) for k in times._fields} 
                for times in cpu_times_percent
            ]
            
        return cpu_info
        
    except Exception as e:
        logger.error(f"Error getting CPU info: {e}")
        return {'error': str(e)}

def get_memory_info() -> Dict[str, Any]:
    """Get memory information"""
    try:
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        return {
            'virtual': {
                'total': virtual_mem.total,
                'available': virtual_mem.available,
                'percent': virtual_mem.percent,
                'used': virtual_mem.used,
                'free': virtual_mem.free,
                'active': getattr(virtual_mem, 'active', None),
                'inactive': getattr(virtual_mem, 'inactive', None),
                'buffers': getattr(virtual_mem, 'buffers', None),
                'cached': getattr(virtual_mem, 'cached', None),
                'shared': getattr(virtual_mem, 'shared', None),
                'slab': getattr(virtual_mem, 'slab', None)
            },
            'swap': {
                'total': swap_mem.total,
                'used': swap_mem.used,
                'free': swap_mem.free,
                'percent': swap_mem.percent,
                'sin': getattr(swap_mem, 'sin', None),
                'sout': getattr(swap_mem, 'sout', None)
            }
        }
    except Exception as e:
        logger.error(f"Error getting memory info: {e}")
        return {'error': str(e)}

def get_disk_info() -> List[Dict[str, Any]]:
    """Get disk/partition information"""
    try:
        disks = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                
                # Add disk I/O counters if available
                try:
                    io_counters = psutil.disk_io_counters(perdisk=True).get(partition.device.replace('\\', '').replace(':', ''))
                    if io_counters:
                        disk_info['io_counters'] = io_counters._asdict()
                except Exception:
                    pass
                    
                disks.append(disk_info)
            except Exception as e:
                logger.warning(f"Could not get disk info for {partition.mountpoint}: {e}")
                
        return disks
        
    except Exception as e:
        logger.error(f"Error getting disk info: {e}")
        return [{'error': str(e)}]

def get_network_info() -> Dict[str, Any]:
    """Get network information"""
    try:
        net_io = psutil.net_io_counters()
        net_io_dict = net_io._asdict() if net_io else {}
        
        # Get network interfaces
        interfaces = {}
        for name, addrs in psutil.net_if_addrs().items():
            interfaces[name] = []
            for addr in addrs:
                interfaces[name].append({
                    'family': addr.family.name if hasattr(addr.family, 'name') else str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask if hasattr(addr, 'netmask') else None,
                    'broadcast': addr.broadcast if hasattr(addr, 'broadcast') else None,
                    'ptp': addr.ptp if hasattr(addr, 'ptp') else None
                })
        
        # Get network connections
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                conn_dict = {
                    'fd': conn.fd,
                    'family': conn.family.name if hasattr(conn.family, 'name') else str(conn.family),
                    'type': conn.type.name if hasattr(conn.type, 'name') else str(conn.type),
                    'laddr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                }
                connections.append(conn_dict)
        except Exception as e:
            logger.warning(f"Could not get network connections: {e}")
        
        return {
            'bytes_sent': net_io_dict.get('bytes_sent'),
            'bytes_recv': net_io_dict.get('bytes_recv'),
            'packets_sent': net_io_dict.get('packets_sent'),
            'packets_recv': net_io_dict.get('packets_recv'),
            'errin': net_io_dict.get('errin'),
            'errout': net_io_dict.get('errout'),
            'dropin': net_io_dict.get('dropin'),
            'dropout': net_io_dict.get('dropout'),
            'interfaces': interfaces,
            'connections': connections
        }
        
    except Exception as e:
        logger.error(f"Error getting network info: {e}")
        return {'error': str(e)}

def get_process_info(pid: Optional[int] = None) -> Dict[str, Any]:
    """
    Get information about a specific process or all processes
    
    Args:
        pid: Process ID (None for all processes)
        
    Returns:
        Dictionary containing process information
    """
    try:
        if pid is not None:
            process = psutil.Process(pid)
            return _get_process_details(process)
        else:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    processes.append(_get_process_details(proc))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return {'processes': processes}
    except Exception as e:
        logger.error(f"Error getting process info: {e}")
        return {'error': str(e)}

def _get_process_details(process: psutil.Process) -> Dict[str, Any]:
    """Get detailed information about a process"""
    try:
        with process.oneshot():
            return {
                'pid': process.pid,
                'name': process.name(),
                'exe': process.exe(),
                'cmdline': process.cmdline(),
                'create_time': process.create_time(),
                'username': process.username(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_info': process.memory_info()._asdict(),
                'memory_percent': process.memory_percent(),
                'io_counters': process.io_counters()._asdict() if hasattr(process, 'io_counters') else {},
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
                'num_ctx_switches': process.num_ctx_switches()._asdict() if hasattr(process, 'num_ctx_switches') else {},
                'ppid': process.ppid(),
                'uids': process.uids()._asdict() if hasattr(process, 'uids') else {},
                'gids': process.gids()._asdict() if hasattr(process, 'gids') else {},
                'terminal': process.terminal(),
                'cpu_times': process.cpu_times()._asdict(),
                'memory_maps': [mmap._asdict() for mmap in process.memory_maps()] if hasattr(process, 'memory_maps') else []
            }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        return {'pid': process.pid, 'error': str(e)}

def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics for the AI Workbench
    
    Returns:
        Dictionary containing system metrics
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network I/O
        net_io = psutil.net_io_counters()
        
        # Get system load average if available
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'cpu_times': psutil.cpu_times_percent(interval=1)._asdict(),
                'load_avg': {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                }
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            },
            'system': {
                'boot_time': psutil.boot_time(),
                'users': [u.name for u in psutil.users()],
                'process_count': len(psutil.pids())
            }
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {'error': str(e)}
