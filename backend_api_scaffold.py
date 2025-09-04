"""
Minimal backend API scaffold for OPRYXX Apex.

Endpoints (initial):
- GET /metrics: basic system info, reads health_report.json if present
- POST /plan?dryRun=1: run apex.ps1 (dry-run) and return plan.json
- POST /repair: run apex.ps1 live and return run folder path
- GET /logs?run=<run-id>: stream events.json for a run

Requires: Python 3.9+, Flask
Install: pip install flask
Run: python backend_api_scaffold.py
"""
import json
import os
import subprocess
import sys
import time
import shutil
try:
    import psutil  # type: ignore
    PSUTIL_AVAILABLE = True
except Exception:  # pragma: no cover
    PSUTIL_AVAILABLE = False
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, request, send_file, send_from_directory, Response, stream_with_context
try:
    from flask_socketio import SocketIO, emit  # type: ignore
    SOCKETIO_AVAILABLE = True
except Exception:  # pragma: no cover
    SocketIO = None  # type: ignore
    emit = None  # type: ignore
    SOCKETIO_AVAILABLE = False

ROOT = Path(__file__).resolve().parent
PROGRAMDATA = Path(os.environ.get('ProgramData', 'C:/ProgramData'))
LOG_ROOT = PROGRAMDATA / 'Opryxx' / 'Logs'
WEB_ROOT = (Path(getattr(sys, '_MEIPASS', ROOT)) / 'web') if getattr(sys, '_MEIPASS', None) else (ROOT / 'web')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") if SOCKETIO_AVAILABLE else None

"""
NOTE: This file may contain duplicated blocks if it was concatenated in
      the past. Routes below are safe to re-declare in Flask; the last
      definition will take effect. Static UI routes are added here.
"""


# Static UI
@app.get('/')
def index():
    idx = WEB_ROOT / 'index.html'
    if idx.exists():
        return send_from_directory(str(WEB_ROOT), 'index.html')
    return '<h1>OPRYXX API</h1><p>Add web/index.html for dashboard.</p>'


@app.get('/web/<path:path>')
def web_static(path: str):
    return send_from_directory(str(WEB_ROOT), path)

def run_powershell(args: list[str], env: Optional[dict] = None) -> subprocess.CompletedProcess:
    ps = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass'] + args
    envp = os.environ.copy()
    if env:
        envp.update(env)
    return subprocess.run(ps, capture_output=True, text=True, env=envp)


def run_powershell_cmd(command: str, env: Optional[dict] = None) -> subprocess.CompletedProcess:
    return run_powershell(['-Command', command], env=env)


@app.get('/metrics')
def metrics():
    health = ROOT / 'health_report.json'
    if health.exists():
        try:
            return jsonify(json.loads(health.read_text(encoding='utf-8')))
        except Exception:
            pass
    # Fallback minimal metrics
    return jsonify({
        'cwd': str(ROOT),
        'os': sys.platform,
        'python': sys.version,
    })


@app.post('/plan')
def plan():
    dry = request.args.get('dryRun', '1') != '0'
    env = {'OPRYXX_SKIP_ELEVATION': '1'} if dry else None
    args = ['-File', str(ROOT / 'apex.ps1')]
    if dry:
        args.append('-DryRun')
    res = run_powershell(args, env=env)
    # Find the latest run folder
    runs = sorted(LOG_ROOT.glob('run_*'))
    if not runs:
        return jsonify({'ok': False, 'stderr': res.stderr, 'stdout': res.stdout}), 500
    latest = runs[-1]
    plan_file = latest / 'plan.json'
    if not plan_file.exists():
        return jsonify({'ok': False, 'run': str(latest), 'message': 'plan.json not found'}), 404
    return send_file(plan_file, mimetype='application/json')


@app.post('/repair')
def repair():
    err = require_auth()
    if err:
        return err
    res = run_powershell(['-File', str(ROOT / 'apex.ps1')])
    runs = sorted(LOG_ROOT.glob('run_*'))
    latest = runs[-1] if runs else None
    return jsonify({'ok': res.returncode == 0, 'run': str(latest) if latest else None, 'stdout': res.stdout, 'stderr': res.stderr})


@app.get('/logs')
def logs():
    run_id = request.args.get('run')
    if not run_id:
        runs = sorted(LOG_ROOT.glob('run_*'))
        if not runs:
            return jsonify({'ok': False, 'message': 'no runs'}), 404
        folder = runs[-1]
    else:
        folder = LOG_ROOT / run_id
    events = folder / 'events.json'
    if not events.exists():
        return jsonify({'ok': False, 'message': 'events.json not found'}), 404
    return send_file(events, mimetype='application/json')


# --- Security (simple token) -------------------------------------------------
def require_auth():
    token = os.environ.get('OPRYXX_API_TOKEN')
    if not token:
        return None
    header = request.headers.get('Authorization', '')
    if header.startswith('Bearer '):
        supplied = header.split(' ', 1)[1]
        if supplied == token:
            return None
    return jsonify({'ok': False, 'message': 'Unauthorized'}), 401


# --- Actions (SFC/DISM/CHKDSK) ----------------------------------------------
def run_cmdline(cmd: list[str]) -> dict:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return {'ok': proc.returncode == 0, 'code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


@app.post('/actions/sfc')
def action_sfc():
    err = require_auth()
    if err:
        return err
    # Requires elevated privileges in most environments
    return jsonify(run_cmdline(['cmd', '/c', 'sfc', '/scannow']))


@app.post('/actions/dism')
def action_dism():
    err = require_auth()
    if err:
        return err
    return jsonify(run_cmdline(['DISM', '/Online', '/Cleanup-Image', '/RestoreHealth']))


@app.post('/actions/chkdsk')
def action_chkdsk():
    err = require_auth()
    if err:
        return err
    drive = os.environ.get('SystemDrive', 'C:')
    return jsonify(run_cmdline(['chkdsk', drive, '/scan']))


@app.post('/drivers/install')
def drivers_install():
    err = require_auth()
    if err:
        return err
    script = ROOT / 'install_model_drivers.ps1'
    if not script.exists():
        return jsonify({'ok': False, 'message': 'install_model_drivers.ps1 not found'}), 404
    res = run_powershell(['-File', str(script)])
    return jsonify({'ok': res.returncode == 0, 'stdout': res.stdout, 'stderr': res.stderr})


@app.post('/boot/recover')
def boot_recover():
    err = require_auth()
    if err:
        return err
    # Placeholder: recovery steps are environment-sensitive and potentially disruptive
    return jsonify({'ok': False, 'message': 'Boot recovery not implemented in API. Use Apex or WinRE.'}), 501


@app.get('/boot/status')
def boot_status():
    # Try rich diagnostics via module
    lib = ROOT / 'lib' / 'Opryxx.Repair.psm1'
    if lib.exists():
        cmd = f"Import-Module '{lib.as_posix()}' -Force; Get-OpryxxBootDiagnostics | ConvertTo-Json -Depth 6"
        res = run_powershell_cmd(cmd)
        if res.returncode == 0 and res.stdout.strip():
            try:
                return jsonify(json.loads(res.stdout))
            except Exception:
                pass
    # Fallback minimal hints
    recovery_dir = Path(os.environ.get('SystemDrive', 'C:')) / 'Recovery'
    boot_dir = Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'Boot'
    tools = {
        'bcdedit': shutil.which('bcdedit') is not None,
        'bootrec': shutil.which('bootrec') is not None,
    }
    return jsonify({'recoveryDirExists': recovery_dir.exists(), 'bootDirExists': boot_dir.exists(), 'tools': tools})


@app.post('/boot/winre/enable')
def boot_winre_enable():
    err = require_auth()
    if err:
        return err
    lib = ROOT / 'lib' / 'Opryxx.Repair.psm1'
    if not lib.exists():
        return jsonify({'ok': False, 'message': 'Repair module not found'}), 500
    cmd = f"Import-Module '{lib.as_posix()}' -Force; Enable-OpryxxWinRE | ConvertTo-Json -Depth 4"
    res = run_powershell_cmd(cmd)
    try:
        data = json.loads(res.stdout) if res.stdout.strip() else {}
    except Exception:
        data = {'stdout': res.stdout, 'stderr': res.stderr}
    data.setdefault('ok', res.returncode == 0 and bool(data.get('ok', True)))
    return jsonify(data)


@app.post('/boot/bcd/rebuild')
def boot_bcd_rebuild():
    err = require_auth()
    if err:
        return err
    confirm = request.args.get('confirm') or (request.get_json(silent=True) or {}).get('confirm')
    if confirm != 'REBUILD':
        return jsonify({'ok': False, 'message': 'Confirmation required. Send confirm=REBUILD'}), 400
    lib = ROOT / 'lib' / 'Opryxx.Repair.psm1'
    if not lib.exists():
        return jsonify({'ok': False, 'message': 'Repair module not found'}), 500
    cmd = f"Import-Module '{lib.as_posix()}' -Force; Invoke-OpryxxBcdRebuildSafe | ConvertTo-Json -Depth 6"
    res = run_powershell_cmd(cmd)
    try:
        data = json.loads(res.stdout) if res.stdout.strip() else {}
    except Exception:
        data = {'stdout': res.stdout, 'stderr': res.stderr}
    if 'ok' not in data:
        data['ok'] = res.returncode == 0
    return jsonify(data)


# --- SSE (real-time) ---------------------------------------------------------
def sse_format(data_obj: dict) -> str:
    return f"data: {json.dumps(data_obj)}\n\n"


@app.get('/events/metrics')
def events_metrics():
    def gen():
        while True:
            try:
                data = compose_metrics()
            except Exception:
                data = {'ok': True}
            yield sse_format({'type': 'metrics', 'data': data, 'ts': time.time()})
            time.sleep(1.0)
    return Response(stream_with_context(gen()), mimetype='text/event-stream')


@app.get('/events/logs')
def events_logs():
    run_id = request.args.get('run')
    if not run_id:
        runs = sorted(LOG_ROOT.glob('run_*'))
        folder = runs[-1] if runs else None
    else:
        folder = LOG_ROOT / run_id

    def read_events(path: Path) -> list:
        try:
            return json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
        except Exception:
            return []

    def gen():
        last_len = 0
        while True:
            if not folder:
                yield sse_format({'type': 'logs', 'data': [], 'ts': time.time()})
                time.sleep(2.0)
                continue
            events_path = folder / 'events.json'
            ev = read_events(events_path)
            if len(ev) > last_len:
                new = ev[last_len:]
                last_len = len(ev)
                yield sse_format({'type': 'logs', 'data': new, 'ts': time.time()})
            time.sleep(2.0)
    return Response(stream_with_context(gen()), mimetype='text/event-stream')


# --- Socket.IO background tasks ---------------------------------------------
def _read_health() -> dict:
    health = ROOT / 'health_report.json'
    if health.exists():
        try:
            return json.loads(health.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def compose_metrics() -> dict:
    base = _read_health()
    out = base if isinstance(base, dict) else {}
    if PSUTIL_AVAILABLE:
        try:
            vm = psutil.virtual_memory()
            out.setdefault('live', {})
            out['live'].update({
                'cpuPercent': psutil.cpu_percent(interval=None),
                'mem': {
                    'total': getattr(vm, 'total', None),
                    'available': getattr(vm, 'available', None),
                    'used': getattr(vm, 'used', None),
                    'percent': getattr(vm, 'percent', None),
                },
                'bootTime': getattr(psutil, 'boot_time', lambda: None)(),
            })
        except Exception:
            pass
    return out


def _metrics_loop():
    while True:
        try:
            data = compose_metrics()
            if socketio:
                socketio.emit('metrics', data)
        except Exception:
            pass
        time.sleep(1.0)


def _logs_loop():
    last_len = 0
    last_folder = None
    while True:
        try:
            runs = sorted(LOG_ROOT.glob('run_*'))
            folder = runs[-1] if runs else None
            if folder != last_folder:
                last_folder = folder
                last_len = 0
            if folder:
                events_path = folder / 'events.json'
                if events_path.exists():
                    try:
                        ev = json.loads(events_path.read_text(encoding='utf-8'))
                    except Exception:
                        ev = []
                    if isinstance(ev, list) and len(ev) > last_len:
                        new = ev[last_len:]
                        last_len = len(ev)
                        if socketio:
                            socketio.emit('logs', new)
        except Exception:
            pass
        time.sleep(2.0)


if __name__ == '__main__':
    # Start Socket.IO background tasks if available
    if socketio:
        socketio.start_background_task(_metrics_loop)
        socketio.start_background_task(_logs_loop)
        socketio.run(app, host='127.0.0.1', port=5050, debug=True)
    else:
        app.run(host='127.0.0.1', port=5050, debug=True)
