let ports = [];
let selectedId = null;

const diagram = document.querySelector("#diagram");
const details = document.querySelector("#details");
const summary = document.querySelector("#summary");
const table = document.querySelector("#ports-table");
const toast = document.querySelector("#toast");
const refreshButton = document.querySelector("#refresh");

window.selectPort = (id) => {
  selectedId = id;
  renderDetails();
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed: ${response.status}`);
  return payload;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 3600);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fallbackDiagram() {
  if (!ports.length) {
    diagram.innerHTML = `<div class="empty">No listening TCP ports found.</div>`;
    return;
  }
  diagram.innerHTML = ports.map((item) => `
    <button class="fallback-node" data-id="${escapeHtml(item.id)}">
      <strong>Port ${item.port}</strong><br />
      ${escapeHtml(item.description)}<br />
      <span>${escapeHtml(item.command)} · PID ${item.pid}</span>
    </button>
  `).join("");
  diagram.querySelectorAll("[data-id]").forEach((node) => {
    node.addEventListener("click", () => window.selectPort(node.dataset.id));
  });
}

async function renderMermaid(source) {
  const mermaid = window.mermaid;
  if (!mermaid) {
    fallbackDiagram();
    return;
  }
  mermaid.initialize({ startOnLoad: false, theme: "dark", securityLevel: "loose" });
  const { svg, bindFunctions } = await mermaid.render(`port-map-${Date.now()}`, source);
  diagram.innerHTML = svg;
  bindFunctions?.(diagram);
}

function renderTable() {
  if (!ports.length) {
    table.innerHTML = `<p>No local TCP listeners are visible right now.</p>`;
    return;
  }
  table.innerHTML = `
    <table>
      <thead><tr><th>Port</th><th>What it is</th><th>Process</th><th>Command</th></tr></thead>
      <tbody>
        ${ports.map((item) => `
          <tr>
            <td><button data-id="${escapeHtml(item.id)}" class="port">${item.port}</button></td>
            <td>${escapeHtml(item.description)}<br /><small>${escapeHtml(item.address)}</small></td>
            <td>${escapeHtml(item.command)}<br /><span class="pid">PID ${item.pid}</span></td>
            <td class="cmd">${escapeHtml(item.details)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
  table.querySelectorAll("[data-id]").forEach((node) => {
    node.addEventListener("click", () => window.selectPort(node.dataset.id));
  });
}

function renderDetails() {
  const item = ports.find((candidate) => candidate.id === selectedId);
  if (!item) {
    details.innerHTML = `<h2>Select a port</h2><p>Click any node in the diagram to see what is running there and choose an action.</p>`;
    return;
  }
  details.innerHTML = `
    <h2>Port ${item.port}</h2>
    <p>${escapeHtml(item.description)}</p>
    <dl>
      <dt>Process</dt><dd>${escapeHtml(item.command)} <span class="pid">PID ${item.pid}</span></dd>
      <dt>Listener</dt><dd>${escapeHtml(item.address)}</dd>
      <dt>User</dt><dd>${escapeHtml(item.user)}</dd>
      <dt>Full command</dt><dd>${escapeHtml(item.details)}</dd>
    </dl>
    <div class="actions">
      <button id="send-terminal">Send to Terminal</button>
      <button id="kill-port" class="danger">Kill</button>
    </div>
  `;
  document.querySelector("#send-terminal").addEventListener("click", async () => {
    const result = await api("/api/open-terminal", {
      method: "POST",
      body: JSON.stringify({ port: item.port, pid: item.pid }),
    });
    showToast(result.message);
  });
  document.querySelector("#kill-port").addEventListener("click", async () => {
    if (!confirm(`Stop ${item.command} on port ${item.port} (PID ${item.pid})?`)) return;
    const result = await api("/api/kill", {
      method: "POST",
      body: JSON.stringify({ pid: item.pid }),
    });
    showToast(result.message);
    await loadPorts();
  });
}

async function loadPorts() {
  refreshButton.disabled = true;
  try {
    const data = await api("/api/ports");
    ports = data.ports;
    summary.textContent = `${data.count} listening TCP port${data.count === 1 ? "" : "s"} found · updated ${data.generatedAt}`;
    await renderMermaid(data.mermaid);
    renderTable();
    renderDetails();
  } catch (error) {
    showToast(error.message);
    diagram.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", loadPorts);
loadPorts();
