const titleEl = document.querySelector("#title");
const summaryEl = document.querySelector("#summary");
const instancesEl = document.querySelector("#instances");
const refreshButton = document.querySelector("#refresh");
const toast = document.querySelector("#toast");

async function api(path) {
  const response = await fetch(path);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed: ${response.status}`);
  return payload;
}

function showToast(message) {
  toast.textContent = message;
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

function statusClass(instance) {
  if (!instance.enabled) return "disabled";
  if (instance.error) return "warn";
  return "ready";
}

function statusLabel(instance) {
  if (!instance.enabled) return "disabled";
  if (instance.error) return "needs config";
  return "ready";
}

function cardHtml(instance) {
  const status = statusClass(instance);
  const action = instance.enabled && !instance.error
    ? `<a class="button primary" href="${escapeHtml(instance.openPath)}">Open n8n UI</a>`
    : "";
  const error = instance.error
    ? `<p class="message">${escapeHtml(instance.error)}</p>`
    : "";
  return `
    <article class="card ${status}">
      <div class="card-top">
        <div>
          <h2>${escapeHtml(instance.name)}</h2>
          <p>${escapeHtml(instance.description || "n8n workspace")}</p>
        </div>
        <span class="badge ${status}">${statusLabel(instance)}</span>
      </div>
      <dl>
        <dt>Type</dt><dd>${escapeHtml(instance.kind)}</dd>
        <dt>URL</dt><dd>${escapeHtml(instance.url)}</dd>
      </dl>
      ${error}
      <div class="actions">
        ${action}
      </div>
    </article>
  `;
}

function render(data) {
  titleEl.textContent = data.title || "n8n Launcher";
  const ready = data.instances.filter((item) => item.enabled && !item.error).length;
  summaryEl.textContent = `${ready}/${data.instances.length} instances ready. Opens the official n8n UI in this Wave web pane.`;
  instancesEl.innerHTML = data.instances.length
    ? data.instances.map(cardHtml).join("")
    : `<p class="empty">No n8n instances are configured.</p>`;
}

async function load() {
  refreshButton.disabled = true;
  try {
    render(await api("/api/config"));
  } catch (error) {
    showToast(error.message);
    instancesEl.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", load);
load();
