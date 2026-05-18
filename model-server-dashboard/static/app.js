const toast = document.querySelector("#toast");
const titleEl = document.querySelector("#title");
const summaryEl = document.querySelector("#summary");
const dashboard = document.querySelector("#dashboard");
const refreshBtn = document.querySelector("#refresh");

// ── helpers ──────────────────────────────────────────────────────────

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 3500);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function copyText(text) {
  navigator.clipboard?.writeText(text).then(
    () => showToast("Copied to clipboard"),
    () => showToast("Failed to copy"),
  );
}

async function api(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

// ── render ───────────────────────────────────────────────────────────

function statusClass(server) {
  if (server.online) return "online";
  if (server.error?.includes("SSH host not configured")) return "warn";
  return "offline";
}

function statusLabel(server) {
  if (server.online) return "online";
  if (server.error?.includes("SSH host not configured")) return "unconfigured";
  return "offline";
}

function cardHtml(server) {
  const cls = statusClass(server);
  const label = statusLabel(server);

  const modelsHtml = server.models?.length > 0
    ? `<div class="models"><ul>${server.models.map(m => `<li>${escapeHtml(m)}</li>`).join("")}</ul></div>`
    : "";

  const errorHtml = server.error
    ? `<div class="error-msg">${escapeHtml(server.error)}</div>`
    : "";

  const deviceHtml = server.health?.device
    ? `<dt>Device</dt><dd>${escapeHtml(server.health.device)}</dd>`
    : "";

  const sampleRateHtml = server.health?.sample_rate
    ? `<dt>Sample rate</dt><dd>${escapeHtml(String(server.health.sample_rate))} Hz</dd>`
    : "";

  const openBtn = server.online
    ? `<button data-action="open-url" data-url="${escapeHtml(server.base_url)}">Open</button>`
    : "";

  const copyModelBtn = server.online && server.models?.length > 0
    ? `<button data-action="copy-model" data-model="${escapeHtml(server.models[0])}">Copy first model</button>`
    : "";

  return `
    <div class="card ${cls}" data-server="${escapeHtml(server.name)}">
      <div class="top">
        <div>
          <div class="server-name">${escapeHtml(server.name)}</div>
          <div class="server-desc">${escapeHtml(server.description)}</div>
        </div>
        <span class="badge ${cls}">${label}</span>
      </div>

      <dl class="meta">
        <dt>Platform</dt><dd>${escapeHtml(server.label ?? "?")}</dd>
        <dt>URL</dt><dd>${escapeHtml(server.base_url)}</dd>
        ${deviceHtml}
        ${sampleRateHtml}
      </dl>

      ${modelsHtml}
      ${errorHtml}

      <div class="actions">
        <button data-action="copy-url" data-url="${escapeHtml(server.base_url)}">Copy URL</button>
        ${openBtn}
        ${copyModelBtn}
      </div>
    </div>
  `;
}

function renderDashboard(data) {
  const grouped = {};
  for (const srv of data.servers) {
    const host = srv.host || "Unknown";
    if (!grouped[host]) grouped[host] = [];
    grouped[host].push(srv);
  }

  const online = data.servers.filter(s => s.online).length;
  const configured = data.servers.filter(s => !s.error?.includes("SSH host not configured")).length;

  titleEl.textContent = data.title || "Model Servers";
  summaryEl.textContent = `${online}/${configured} online · ${data.servers.length} servers · ${data.generatedAt}`;

  let html = "";
  for (const [host, servers] of Object.entries(grouped)) {
    const icon = host === "This Mac" ? "&#x1f5a5;" : "&#x2601;";
    html += `
      <div class="host-group">
        <h2><span class="host-icon">${icon}</span> ${escapeHtml(host)}</h2>
        <div class="server-grid">
          ${servers.map(cardHtml).join("")}
        </div>
      </div>
    `;
  }
  dashboard.innerHTML = html;

  // Wire action buttons
  dashboard.querySelectorAll("[data-action]").forEach(btn => {
    btn.addEventListener("click", e => {
      const action = e.currentTarget.dataset.action;
      if (action === "copy-url") copyText(e.currentTarget.dataset.url);
      else if (action === "open-url") window.open(e.currentTarget.dataset.url, "_blank");
      else if (action === "copy-model") copyText(e.currentTarget.dataset.model);
    });
  });
}

// ── lifecycle ────────────────────────────────────────────────────────

async function load() {
  refreshBtn.disabled = true;
  try {
    const data = await api("/api/servers");
    renderDashboard(data);
  } catch (err) {
    showToast(err.message);
    dashboard.innerHTML = `<p class="error" style="padding:2rem;color:var(--danger)">${escapeHtml(err.message)}</p>`;
  } finally {
    refreshBtn.disabled = false;
  }
}

refreshBtn.addEventListener("click", load);

// Auto-refresh
api("/api/refresh-interval")
  .then(r => {
    const ms = (r.interval || 30) * 1000;
    window.setInterval(load, ms);
  })
  .catch(() => {});

load();
