const statusSummary = document.querySelector("#status-summary");
const refreshButton = document.querySelector("#refresh-button");
const saveButton = document.querySelector("#save-button");
const phaseBadge = document.querySelector("#phase-badge");
const phaseList = document.querySelector("#phase-list");
const sessionTitle = document.querySelector("#session-title");
const sessionQuestion = document.querySelector("#session-question");
const sessionScope = document.querySelector("#session-scope");
const sessionOutput = document.querySelector("#session-output");
const sessionPhase = document.querySelector("#session-phase");
const sessionStatus = document.querySelector("#session-status");
const sessionNotes = document.querySelector("#session-notes");
const sourceForm = document.querySelector("#source-form");
const sourceUrl = document.querySelector("#source-url");
const sourceTitle = document.querySelector("#source-title");
const sourceType = document.querySelector("#source-type");
const sourceNotes = document.querySelector("#source-notes");
const sourcesList = document.querySelector("#sources-list");
const workerForm = document.querySelector("#worker-form");
const workerProfile = document.querySelector("#worker-profile");
const workerStatus = document.querySelector("#worker-status");
const workerTask = document.querySelector("#worker-task");
const workersList = document.querySelector("#workers-list");
const claimForm = document.querySelector("#claim-form");
const claimText = document.querySelector("#claim-text");
const claimStatus = document.querySelector("#claim-status");
const claimCitation = document.querySelector("#claim-citation");
const claimsList = document.querySelector("#claims-list");
const toast = document.querySelector("#toast");

const state = {
  config: null,
  session: null,
  sources: [],
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }
  return payload;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function copyText(value, successMessage) {
  await navigator.clipboard.writeText(value);
  showToast(successMessage);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 3200);
}

function getPhaseDefinitions() {
  return state.config?.workflows?.[0]?.phases || [];
}

function currentSession() {
  return state.session?.session || {};
}

function updateSummary() {
  const session = currentSession();
  const sourceCount = state.sources.length;
  const workerCount = state.session?.workerQueue?.length || 0;
  const claimCount = state.session?.claims?.length || 0;
  statusSummary.textContent = `${sourceCount} sources, ${workerCount} workers, ${claimCount} claims. Same-tab controls now; deterministic adjacency later.`;
  phaseBadge.textContent = session.status || "active";
  phaseBadge.className = `badge status-${session.status || "active"}`;
}

function renderPhaseOptions() {
  const phases = getPhaseDefinitions();
  sessionPhase.innerHTML = phases
    .map((phase) => `<option value="${escapeHtml(phase.id)}">${escapeHtml(phase.label)}</option>`)
    .join("");
}

function renderPhaseList() {
  const phases = getPhaseDefinitions();
  const activeId = currentSession().phase;
  phaseList.innerHTML = phases
    .map((phase, index) => {
      const active = phase.id === activeId ? "active" : "";
      return `
        <li class="phase-item ${active}">
          <div class="phase-index">${index + 1}</div>
          <div>
            <h3>${escapeHtml(phase.label)}</h3>
            <p>${escapeHtml(phase.gate || "")}</p>
          </div>
        </li>`;
    })
    .join("");
}

function fillSourceTypes() {
  sourceType.innerHTML = (state.config?.sourceTypes || [])
    .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.label)}</option>`)
    .join("");
}

function fillProfiles() {
  workerProfile.innerHTML = (state.config?.profiles || [])
    .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.label)}</option>`)
    .join("");
}

function renderSessionFields() {
  const session = currentSession();
  sessionTitle.value = session.title || "";
  sessionQuestion.value = session.question || "";
  sessionScope.value = session.scope || "";
  sessionOutput.value = session.expectedOutput || "";
  sessionStatus.value = session.status || "active";
  sessionPhase.value = session.phase || getPhaseDefinitions()[0]?.id || "brief";
  sessionNotes.value = (state.session?.notes || [])
    .map((item) => item.text || "")
    .join("\n\n");
}

function renderSources() {
  sourcesList.innerHTML = state.sources.length
    ? state.sources
        .map(
          (source) => `
            <article class="list-card">
              <div class="list-card-header">
                <div>
                  <h3>${escapeHtml(source.title || source.url)}</h3>
                  <p>${escapeHtml(source.type || "source")} · ${escapeHtml(source.status || "queued")}</p>
                </div>
              </div>
              <p class="code-line">${escapeHtml(source.url)}</p>
              ${source.notes ? `<p>${escapeHtml(source.notes)}</p>` : ""}
              <div class="actions">
                <a class="button primary" href="${escapeHtml(source.openPath)}">Open here</a>
                <button type="button" data-copy-command="${escapeHtml(source.waveWebOpenCommand || "")}">Copy Wave command</button>
              </div>
            </article>`
        )
        .join("")
    : `<p class="empty">No sources yet. Add a source to start the queue.</p>`;

  sourcesList.querySelectorAll("[data-copy-command]").forEach((button) => {
    button.addEventListener("click", async () => {
      const command = button.getAttribute("data-copy-command");
      if (!command) {
        showToast("No command available for this source.");
        return;
      }
      await copyText(command, "Wave open command copied.");
    });
  });
}

function renderWorkers() {
  const profilesById = new Map((state.config?.profiles || []).map((profile) => [profile.id, profile]));
  const queue = state.session?.workerQueue || [];
  workersList.innerHTML = queue.length
    ? queue
        .map((item) => {
          const profile = profilesById.get(item.profileId);
          return `
            <article class="list-card">
              <div class="list-card-header">
                <div>
                  <h3>${escapeHtml(profile?.label || item.profileId || "Worker")}</h3>
                  <p>${escapeHtml(item.status || "queued")}</p>
                </div>
              </div>
              <p>${escapeHtml(item.task || "")}</p>
              ${profile?.description ? `<p>${escapeHtml(profile.description)}</p>` : ""}
            </article>`;
        })
        .join("")
    : `<p class="empty">No workers queued. Keep worker roles bounded and explicit.</p>`;
}

function renderClaims() {
  const claims = state.session?.claims || [];
  claimsList.innerHTML = claims.length
    ? claims
        .map(
          (claim) => `
            <article class="list-card">
              <div class="list-card-header">
                <div>
                  <h3>${escapeHtml(claim.status || "unresolved")}</h3>
                  <p>${escapeHtml(claim.citation || "No citation note")}</p>
                </div>
              </div>
              <p>${escapeHtml(claim.text || "")}</p>
            </article>`
        )
        .join("")
    : `<p class="empty">No claims yet. Add claims only after evidence is recorded.</p>`;
}

function renderAll() {
  renderPhaseOptions();
  renderPhaseList();
  fillSourceTypes();
  fillProfiles();
  renderSessionFields();
  renderSources();
  renderWorkers();
  renderClaims();
  updateSummary();
}

async function loadAll() {
  refreshButton.disabled = true;
  try {
    const [config, sessionResult, sourcesResult] = await Promise.all([
      api("/api/config"),
      api("/api/state"),
      api("/api/sources"),
    ]);
    state.config = config;
    state.session = sessionResult.state;
    state.sources = sourcesResult.sources;
    renderAll();
  } catch (error) {
    statusSummary.textContent = error.message;
    showToast(error.message);
  } finally {
    refreshButton.disabled = false;
  }
}

function collectSessionPatch() {
  return {
    session: {
      title: sessionTitle.value.trim(),
      question: sessionQuestion.value.trim(),
      scope: sessionScope.value.trim(),
      expectedOutput: sessionOutput.value.trim(),
      phase: sessionPhase.value,
      status: sessionStatus.value,
    },
    notes: sessionNotes.value.trim()
      ? [{ id: "operator-notes", text: sessionNotes.value.trim() }]
      : [],
  };
}

async function saveSession() {
  await api("/api/state", {
    method: "PATCH",
    body: JSON.stringify(collectSessionPatch()),
  });
  showToast("Session saved.");
  await loadAll();
}

refreshButton.addEventListener("click", loadAll);
saveButton.addEventListener("click", saveSession);

sourceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/sources", {
      method: "POST",
      body: JSON.stringify({
        url: sourceUrl.value,
        title: sourceTitle.value,
        type: sourceType.value,
        notes: sourceNotes.value,
      }),
    });
    sourceForm.reset();
    showToast("Source added.");
    await loadAll();
  } catch (error) {
    showToast(error.message);
  }
});

workerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/worker-queue", {
      method: "POST",
      body: JSON.stringify({
        profileId: workerProfile.value,
        status: workerStatus.value,
        task: workerTask.value.trim(),
      }),
    });
    workerTask.value = "";
    showToast("Worker queued.");
    await loadAll();
  } catch (error) {
    showToast(error.message);
  }
});

claimForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/claims", {
      method: "POST",
      body: JSON.stringify({
        text: claimText.value.trim(),
        status: claimStatus.value,
        citation: claimCitation.value.trim(),
      }),
    });
    claimText.value = "";
    claimCitation.value = "";
    showToast("Claim added.");
    await loadAll();
  } catch (error) {
    showToast(error.message);
  }
});

for (const element of [sessionTitle, sessionQuestion, sessionScope, sessionOutput, sessionPhase, sessionStatus, sessionNotes]) {
  element.addEventListener("change", saveSession);
}

loadAll();
