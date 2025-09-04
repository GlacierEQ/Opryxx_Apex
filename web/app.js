// Simple animated background (fractal-ish particles)
(function bg() {
  const canvas = document.getElementById('bg');
  const ctx = canvas.getContext('2d');
  let w, h, t = 0;
  const particles = Array.from({ length: 220 }, () => ({ x: Math.random(), y: Math.random(), s: Math.random() * 1.5 + 0.3 }));
  function resize() { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; }
  window.addEventListener('resize', resize); resize();
  function loop() {
    t += 0.003; ctx.clearRect(0, 0, w, h);
    for (const p of particles) {
      const ax = Math.sin((p.x + t) * 6.283) * 0.002;
      const ay = Math.cos((p.y + t * 1.3) * 6.283) * 0.002;
      p.x = (p.x + ax + 1) % 1; p.y = (p.y + ay + 1) % 1;
      const X = p.x * w, Y = p.y * h;
      const g = ctx.createRadialGradient(X, Y, 0, X, Y, 24*p.s);
      g.addColorStop(0, 'rgba(0,255,198,0.25)'); g.addColorStop(1, 'rgba(56,182,255,0.0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(X, Y, 24*p.s, 0, Math.PI*2); ctx.fill();
    }
    requestAnimationFrame(loop);
  }
  loop();
})();

const els = {
  metrics: document.getElementById('metrics'),
  boot: document.getElementById('boot-status'),
  log: document.getElementById('log'),
  ai: document.getElementById('ai'),
  drivers: document.getElementById('drivers'),
  pillOnline: document.getElementById('status-online'),
  pillProgress: document.getElementById('status-progress'),
  pillResult: document.getElementById('status-result'),
  barOverall: document.getElementById('bar-overall'),
  labelOverall: document.getElementById('label-overall'),
  barStep: document.getElementById('bar-step'),
  labelStep: document.getElementById('label-step'),
  btn: {
    monitor: document.getElementById('btn-monitor'),
    stopMonitor: document.getElementById('btn-stop-monitor'),
    plan: document.getElementById('btn-plan'),
    repair: document.getElementById('btn-repair'),
    drivers: document.getElementById('btn-drivers'),
    sfc: document.getElementById('btn-sfc'),
    dism: document.getElementById('btn-dism'),
    chkdsk: document.getElementById('btn-chkdsk'),
    boot: document.getElementById('btn-boot'),
    bcd: document.getElementById('btn-bcd'),
  }
};

let evtMetrics = null, evtLogs = null, ioSocket = null;
let driverRows = [];

function setProgress(text, cls) {
  els.pillProgress.textContent = text;
  els.pillProgress.classList.remove('muted', 'ok', 'err');
  if (cls) els.pillProgress.classList.add(cls);
}
function setResult(text, ok) {
  els.pillResult.textContent = text;
  els.pillResult.classList.remove('muted', 'ok', 'err');
  els.pillResult.classList.add(ok ? 'ok' : 'err');
}

async function fetchJSON(url, opts) {
  const token = localStorage.getItem('OPRYXX_TOKEN');
  const base = opts || {};
  const headers = Object.assign({}, base.headers||{});
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(url, Object.assign({}, base, { headers }));
  const ct = res.headers.get('content-type')||'';
  if (ct.includes('application/json')) {
    const j = await res.json();
    if (!res.ok) throw Object.assign(new Error(j.message||'Request failed'), { data:j });
    return j;
  }
  if (!res.ok) throw new Error('Request failed');
  return null;
}

function renderMetrics(data) {
  const sys = data.system || {};
  const os = data.os || {};
  const vols = data.volumes || [];
  const live = data.live || {};
  function fmtBytes(n){ if(n==null) return 'N/A'; const u=['B','KB','MB','GB','TB']; let i=0; let v=n; while(v>1024 && i<u.length-1){ v/=1024; i++; } return v.toFixed(1)+' '+u[i]; }
  const cVol = vols.find(v => v.DriveLetter==='C') || vols[0] || {};
  els.metrics.innerHTML = `
    <div class="metric"><div class="k">Model</div><div class="v">${(sys.Manufacturer||'N/A')} ${(sys.Model||'')}</div></div>
    <div class="metric"><div class="k">CPU Usage</div><div class="v">${live.cpuPercent!=null ? Math.round(live.cpuPercent)+'%' : 'N/A'}</div></div>
    <div class="metric"><div class="k">Memory</div><div class="v">${fmtBytes(sys.TotalPhysicalMemory||0)}</div></div>
    <div class="metric"><div class="k">RAM Used</div><div class="v">${live.mem ? (fmtBytes(live.mem.used||0)+' / '+fmtBytes(live.mem.total||0)+' ('+(live.mem.percent||0)+'%)') : 'N/A'}</div></div>
    <div class="metric"><div class="k">Logical CPUs</div><div class="v">${sys.NumberOfLogicalProcessors||'N/A'}</div></div>
    <div class="metric"><div class="k">OS</div><div class="v">${os.Caption||'N/A'} (${os.Version||'N/A'})</div></div>
    <div class="metric"><div class="k">C: Size</div><div class="v">${fmtBytes(cVol.Size||0)}</div></div>
    <div class="metric"><div class="k">C: Free</div><div class="v">${fmtBytes(cVol.SizeRemaining||0)}</div></div>
  `;
  const tips = [];
  if ((cVol.SizeRemaining||0) / (cVol.Size||1) < 0.1) tips.push('Low free disk space on system volume. Consider cleanup.');
  if ((sys.NumberOfLogicalProcessors||0) < 4) tips.push('Entry-level CPU detected. Keep background tasks minimal.');
  tips.push('If system instability persists, run Full Repair (Apex).');
  els.ai.innerHTML = tips.map(t => `<div class="tip"><strong>Hint:</strong> ${t}</div>`).join('');
}

function updateOverall(pct){
  if (typeof pct !== 'number' || isNaN(pct)) return;
  pct = Math.max(0, Math.min(100, Math.round(pct)));
  els.barOverall.style.width = pct + '%';
  els.labelOverall.textContent = pct + '%';
}

function updateStepRunning(name, progress){
  els.labelStep.textContent = name || 'Running';
  els.barStep.classList.add('ind');
  if (typeof progress === 'number') {
    els.barStep.classList.remove('ind');
    els.barStep.style.width = Math.max(0, Math.min(100, progress)) + '%';
  } else {
    els.barStep.style.width = '35%';
  }
}

function updateStepDone(){
  els.labelStep.textContent = 'Idle';
  els.barStep.classList.remove('ind');
  els.barStep.style.width = '0%';
}

function renderDrivers(){
  els.drivers.innerHTML = driverRows.map(r => {
    const meta = [];
    if (r.provider) meta.push(r.provider);
    if (r.class) meta.push(r.class);
    if (r.driverVer) meta.push(r.driverVer);
    return `
      <div class="row">
        <div class="status ${r.ok ? 'ok':'err'}">${r.ok?'OK':'ERR'}</div>
        <div class="path" title="${r.inf}">${r.inf}<div class="meta">${meta.join(' • ')}</div></div>
        <div class="code">${r.code!=null ? 'code '+r.code: (r.status||'')}</div>
      </div>
    `;
  }).join('');
}

function appendLog(events) {
  if (!events || !events.length) return;
  const lines = events.map(e => {
    const ts = new Date(e.timestamp||Date.now()).toLocaleTimeString();
    const st = e.status || 'info';
    const step = e.step || 'event';
    const det = e.details ? JSON.stringify(e.details) : '';
    let mark = '.';
    if (st==='ready') mark = 'o'; else if (st==='running') mark='>'; else if (st==='done') mark='OK'; else if (st==='error') mark='ERR';
    // Progress handling
    if (step === 'overall' && st === 'progress') {
      updateOverall(e.details?.percent);
    }
    if (st === 'running') {
      updateStepRunning(step, e.details?.progress);
    }
    if ((st === 'success') || (st?.startsWith && st.startsWith('exit_')) || st==='missing' || st==='skipped' || st==='error') {
      updateStepDone();
    }
    // Driver rows
    if (step === 'Install driver INF' && (st==='success' || st==='error' || (st?.startsWith && st.startsWith('exit_')) || st==='missing' || st==='skipped')) {
      const inf = (e.details && (e.details.inf || e.details.path)) || '';
      const code = (e.details && e.details.exitCode);
      driverRows.push({
        ok: st==='success',
        inf,
        code,
        status: st,
        provider: e.details?.provider,
        class: e.details?.class,
        driverVer: e.details?.driverVer,
      });
      renderDrivers();
    }
    return `[${ts}] ${mark} ${step} ${det}`;
  });
  els.log.textContent += (els.log.textContent ? '\n' : '') + lines.join('\n');
  els.log.scrollTop = els.log.scrollHeight;
}

function startMonitoring() {
  if (window.io && !ioSocket) {
    try {
      ioSocket = window.io();
      ioSocket.on('connect', () => { els.pillOnline.classList.add('ok'); els.pillOnline.textContent = 'Online'; });
      ioSocket.on('disconnect', () => { els.pillOnline.classList.remove('ok'); els.pillOnline.textContent = 'Offline'; });
      ioSocket.on('metrics', (data) => { renderMetrics(data||{}); });
      ioSocket.on('logs', (events) => { appendLog(events||[]); });
    } catch (e) { ioSocket = null; }
  }
  if (!ioSocket) {
    if (!evtMetrics) {
      evtMetrics = new EventSource('/events/metrics');
      evtMetrics.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'metrics') {
          renderMetrics(msg.data || {});
          els.pillOnline.classList.add('ok');
          els.pillOnline.textContent = 'Online';
        }
      };
      evtMetrics.onerror = () => { els.pillOnline.classList.remove('ok'); els.pillOnline.textContent = 'Offline'; };
    }
    if (!evtLogs) {
      evtLogs = new EventSource('/events/logs');
      evtLogs.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'logs') appendLog(msg.data||[]);
      };
    }
  }
}

function stopMonitoring() {
  if (ioSocket) { try { ioSocket.close(); } catch (e) {} ioSocket = null; }
  if (evtMetrics) { evtMetrics.close(); evtMetrics = null; }
  if (evtLogs) { evtLogs.close(); evtLogs = null; }
}

async function runAction(id, url, opts={ method:'POST' }) {
  try {
    setProgress('Working...', 'ok');
    const res = await fetchJSON(url, opts);
    setResult('Success', true);
    appendLog([{ timestamp: Date.now(), step: id, status: 'done', details: res }] );
  } catch (e) {
    setResult('Error', false);
    appendLog([{ timestamp: Date.now(), step: id, status: 'error', details: e.data||e.message }] );
  } finally {
    setProgress('Idle', 'muted');
  }
}

async function loadBootStatus() {
  try {
    const s = await fetchJSON('/boot/status');
    if (s && s.winre) {
      const parts = [];
      parts.push(`WinRE: ${s.winre.enabled===true?'Enabled':s.winre.enabled===false?'Disabled':'Unknown'}`);
      if (s.winre.location) parts.push(`RE: ${s.winre.location}`);
      if (s.bcd) parts.push(`BCD: ${s.bcd.ok?'OK':'Unknown'}`);
      if (s.esp) parts.push(`ESP: ${s.esp.present?'Present':'Missing'}`);
      if (s.secureBoot!==undefined) parts.push(`SecureBoot: ${s.secureBoot===true?'On':s.secureBoot===false?'Off':'Unknown'}`);
      if (s.files) {
        const fl = [];
        if (s.files.winload) fl.push('winload');
        if (s.files.winresume) fl.push('winresume');
        if (s.files.bcdStore) fl.push('BCD');
        parts.push(`Files: ${fl.join(', ')||'N/A'}`);
      }
      els.boot.textContent = parts.join(' | ');
    } else {
      els.boot.textContent = `Recovery dir: ${s.recoveryDirExists?'Yes':'No'} | Boot dir: ${s.bootDirExists?'Yes':'No'} | bcdedit: ${s.tools?.bcdedit?'Yes':'No'} | bootrec: ${s.tools?.bootrec?'Yes':'No'}`;
    }
  } catch (e) { els.boot.textContent = 'Boot status unavailable'; }
}

// Wire up controls
els.btn.monitor.addEventListener('click', startMonitoring);
els.btn.stopMonitor.addEventListener('click', stopMonitoring);
els.btn.plan.addEventListener('click', () => runAction('plan', '/plan?dryRun=1'));
els.btn.repair.addEventListener('click', () => runAction('repair', '/repair'));
els.btn.drivers.addEventListener('click', () => runAction('drivers', '/drivers/install'));
els.btn.sfc.addEventListener('click', () => runAction('sfc', '/actions/sfc'));
els.btn.dism.addEventListener('click', () => runAction('dism', '/actions/dism'));
els.btn.chkdsk.addEventListener('click', () => runAction('chkdsk', '/actions/chkdsk'));
els.btn.boot.addEventListener('click', async () => {
  await runAction('winre_enable', '/boot/winre/enable');
  loadBootStatus();
});

els.btn.bcd.addEventListener('click', async () => {
  const txt = prompt('Type REBUILD to confirm rebuilding the BCD store (a backup will be exported).');
  if (txt !== 'REBUILD') return;
  try {
    setProgress('Working...', 'ok');
    const res = await fetchJSON('/boot/bcd/rebuild', { method:'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ confirm: 'REBUILD' })});
    setResult('Success', true);
    appendLog([{ timestamp: Date.now(), step: 'bcd_rebuild', status: 'done', details: res }] );
  } catch (e) {
    setResult('Error', false);
    appendLog([{ timestamp: Date.now(), step: 'bcd_rebuild', status: 'error', details: e.data||e.message }] );
  } finally { setProgress('Idle', 'muted'); }
});

// Initial load
(async function init(){
  try { const m = await fetchJSON('/metrics'); renderMetrics(m); els.pillOnline.classList.add('ok'); } catch (e) {}
  loadBootStatus();
  startMonitoring();
})();

