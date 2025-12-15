// public/app.js
// ✅ 단계형 UI: Projects(로그인 후) -> Project(Home: Documents/Tasks) -> Document(Versions) -> Version Detail(File Preview)

const DEFAULT_API_PORT = "3000";
const API_BASE =
  window.location.port && window.location.port !== DEFAULT_API_PORT
    ? `http://${window.location.hostname}:${DEFAULT_API_PORT}`
    : "";

// ---------------------- State ----------------------
const state = {
  user: loadUser(),
  token: loadToken(),

  // ✅ 단계형 화면 상태
  stage: "projects", // "projects" | "project" | "document" | "stats"
  projectTab: "documents", // "documents" | "tasks"

  projects: [],
  currentProject: null,
  projectMembers: [],

  documents: [],
  currentDocument: null,

  versions: [],
  tasks: [],

  // ✅ 통계 데이터
  stats: {
    summary: null,
    contributions: [],
    taskStatus: [],
    dailyCommits: [],
    userProjects: [],
  },

  // ✅ 파일 미리보기 blob url 캐시 (versionId -> { url, type, ts })
  previewCache: new Map(),
};

// ---------------------- DOM Helpers ----------------------
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function safeText(el, text) {
  if (el) el.textContent = text;
}
function safeHTML(el, html) {
  if (el) el.innerHTML = html;
}

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function toast(msg, ok = true) {
  const t = $("#toast");
  if (!t) return;
  t.textContent = msg;
  t.className = "toast show " + (ok ? "ok" : "bad");
  setTimeout(() => {
    t.className = "toast";
    t.textContent = "";
  }, 2200);
}

// ---------------------- LocalStorage ----------------------
function loadUser() {
  try {
    return JSON.parse(localStorage.getItem("minigit_user") || "null");
  } catch {
    return null;
  }
}
function saveUser(u) {
  state.user = u;
  localStorage.setItem("minigit_user", JSON.stringify(u));
}
function clearUser() {
  state.user = null;
  localStorage.removeItem("minigit_user");
}
function loadToken() {
  return localStorage.getItem("minigit_token");
}
function saveToken(token) {
  state.token = token;
  localStorage.setItem("minigit_token", token);
}
function clearToken() {
  state.token = null;
  localStorage.removeItem("minigit_token");
}

// ---------------------- ✅ Current Selection UI ----------------------
function resetSelectionUI() {
  const proj = state.currentProject ? state.currentProject.name : "-";
  const doc = state.currentDocument ? state.currentDocument.title : "-";

  safeText($("#selProject"), proj);
  safeText($("#selDocument"), doc);

  [
    "#selProjectName",
    "#currentProject",
    ".js-sel-project",
    "[data-sel='project']",
    "[data-current='project']",
  ].forEach((sel) => $$(sel).forEach((el) => safeText(el, proj)));

  [
    "#selDocumentName",
    "#currentDocument",
    ".js-sel-document",
    "[data-sel='document']",
    "[data-current='document']",
  ].forEach((sel) => $$(sel).forEach((el) => safeText(el, doc)));
}

// ---------------------- API Helper ----------------------
async function api(path, options = {}) {
  const isAuthRoute = path.startsWith("/auth/");
  const token = isAuthRoute ? null : loadToken(); // ✅ /auth는 토큰 안 붙임
  const url = `${API_BASE}${path}`;
  const isFormData = options.body instanceof FormData;

  const res = await fetch(url, {
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  // ✅ JSON 아닌 응답에도 안전
  let data = {};
  try {
    data = await res.json();
  } catch {
    data = {};
  }

  if (res.status === 401) {
    if (isAuthRoute) {
      throw new Error(data?.message || "로그인 실패");
    }

    // ✅ 세션 만료 처리
    clearToken();
    clearUser();

    state.stage = "projects";
    state.projectTab = "documents";
    state.projects = [];
    state.currentProject = null;
    state.projectMembers = [];
    state.documents = [];
    state.currentDocument = null;
    state.versions = [];
    state.tasks = [];
    state.stats = {
      summary: null,
      contributions: [],
      taskStatus: [],
      dailyCommits: [],
      userProjects: [],
    };
    state.previewCache.clear();

    renderUserHeader();
    resetSelectionUI();
    openAuth(true);
    showLoginPane();
    renderStage();

    throw new Error(data?.message || "인증이 필요합니다. 다시 로그인하세요.");
  }

  if (!res.ok) {
    throw new Error(data?.message || `요청 실패: ${res.status} (${url})`);
  }

  return data;
}

// ---------------------- ✅ File Fetch Helper (Authorization 포함) ----------------------
async function fetchAuthedBlob(url) {
  const token = loadToken();

  const res = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (res.status === 401) {
    clearToken();
    clearUser();

    state.stage = "projects";
    state.projectTab = "documents";
    state.projects = [];
    state.currentProject = null;
    state.projectMembers = [];
    state.documents = [];
    state.currentDocument = null;
    state.versions = [];
    state.tasks = [];
    state.stats = {
      summary: null,
      contributions: [],
      taskStatus: [],
      dailyCommits: [],
      userProjects: [],
    };
    state.previewCache.clear();

    renderUserHeader();
    resetSelectionUI();
    openAuth(true);
    showLoginPane();
    renderStage();

    throw new Error("인증이 필요합니다. 다시 로그인하세요.");
  }

  if (!res.ok) {
    throw new Error(`파일 요청 실패: ${res.status}`);
  }

  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition") || "";

  let filename = null;
  const m = disposition.match(/filename\*=UTF-8''([^;]+)|filename="([^"]+)"/i);
  if (m) filename = decodeURIComponent(m[1] || m[2] || "");

  return { blob, filename, contentType: res.headers.get("Content-Type") || "" };
}

function triggerDownloadFromBlob(blob, filename = "download") {
  const a = document.createElement("a");
  const url = URL.createObjectURL(blob);
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

async function getOrCreatePreviewObjectUrl(versionId, inlineUrl) {
  const hit = state.previewCache.get(versionId);
  const now = Date.now();

  // 5분 캐시
  if (hit && hit.url && now - hit.ts < 5 * 60 * 1000) return hit.url;

  // 기존 url 정리
  if (hit?.url) {
    try { URL.revokeObjectURL(hit.url); } catch {}
  }

  const { blob } = await fetchAuthedBlob(inlineUrl);
  const objUrl = URL.createObjectURL(blob);
  state.previewCache.set(versionId, { url: objUrl, ts: now });
  return objUrl;
}

// ---------------------- Modal Helpers ----------------------
function openModal(modalId, open = true) {
  const m = document.getElementById(modalId);
  if (!m) return;
  m.setAttribute("aria-hidden", open ? "false" : "true");
}
function closeAllModals() {
  ["projectModal", "documentModal", "versionModal", "taskModal", "confirmModal"].forEach((id) =>
    openModal(id, false)
  );
}
function initModalClosers() {
  document.addEventListener("click", (e) => {
    const t = e.target;
    const key = t?.dataset?.close;
    if (!key) return;

    if (key === "1") {
      if (!state.user) return;
      openAuth(false);
      return;
    }

    if (key === "project") openModal("projectModal", false);
    if (key === "document") openModal("documentModal", false);
    if (key === "version") openModal("versionModal", false);
    if (key === "task") openModal("taskModal", false);
    if (key === "confirm") openModal("confirmModal", false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (state.user) openAuth(false);
    closeAllModals();
  });
}

// ✅ confirm 모달 로직
let __confirmHandler = null;
function openConfirm({ title = "확인", message = "", okText = "확인", cancelText = "취소", onConfirm }) {
  safeText($("#confirmTitle"), title);
  safeText($("#confirmMessage"), message);
  safeText($("#confirmOk"), okText);
  safeText($("#confirmCancel"), cancelText);

  __confirmHandler = typeof onConfirm === "function" ? onConfirm : null;
  openModal("confirmModal", true);

  const cancel = $("#confirmCancel");
  if (cancel) cancel.style.display = cancelText ? "" : "none";
}
function initConfirmModal() {
  $("#confirmCancel")?.addEventListener("click", () => openModal("confirmModal", false));
  $("#confirmOk")?.addEventListener("click", async () => {
    const fn = __confirmHandler;
    __confirmHandler = null;
    openModal("confirmModal", false);
    if (fn) await fn();
  });
}

// ---------------------- UI Lock/Unlock ----------------------
function lockMainUI(locked) {
  if ($("#appRoot")) document.body.classList.toggle("locked", locked);
}

function renderUserHeader() {
  const badge = $("#userBadge");
  const btnOpenAuth = $("#btnOpenAuth");
  const btnLogout = $("#btnLogout");

  if (badge) badge.textContent = state.user ? `${state.user.name} (@${state.user.username})` : "Guest";
  if (btnOpenAuth) btnOpenAuth.style.display = state.user ? "none" : "";
  if (btnLogout) btnLogout.style.display = state.user ? "" : "none";

  lockMainUI(!state.user);
  updateQuickActionState();
  resetSelectionUI();
}

// ---------------------- Auth Modal ----------------------
function openAuth(open = true) {
  const modal = $("#authModal");
  if (!modal) return;
  modal.setAttribute("aria-hidden", open ? "false" : "true");
}
function showLoginPane() {
  $("#loginForm") && ($("#loginForm").style.display = "block");
  $("#registerForm") && ($("#registerForm").style.display = "none");
}
function showRegisterPane() {
  $("#loginForm") && ($("#loginForm").style.display = "none");
  $("#registerForm") && ($("#registerForm").style.display = "block");
}

function initAuth() {
  $("#btnLogout")?.addEventListener("click", () => {
    clearToken();
    clearUser();

    state.stage = "projects";
    state.projectTab = "documents";
    state.projects = [];
    state.currentProject = null;
    state.projectMembers = [];
    state.documents = [];
    state.currentDocument = null;
    state.versions = [];
    state.tasks = [];
    state.stats = { summary: null, contributions: [], taskStatus: [], dailyCommits: [], userProjects: [] };
    state.previewCache.clear();

    renderUserHeader();
    resetSelectionUI();
    openAuth(true);
    showLoginPane();
    renderStage();
  });

  $("#authModal")?.addEventListener("click", (e) => {
    const t = e.target;
    if (t?.dataset?.close) {
      if (!state.user) return;
      openAuth(false);
    }
  });

  $("#btnOpenAuth")?.addEventListener("click", () => {
    openAuth(true);
    showLoginPane();
  });

  $("#toRegister")?.addEventListener("click", () => {
    showRegisterPane();
    $("#registerForm")?.querySelector('input[name="username"]')?.focus();
  });
  $("#toLogin")?.addEventListener("click", () => {
    showLoginPane();
    $("#loginForm")?.querySelector('input[name="username"]')?.focus();
  });

  $("#loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const username = form.querySelector('input[name="username"]')?.value?.trim();
    const password = form.querySelector('input[name="password"]')?.value?.trim();

    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });

      if (data.token) saveToken(data.token);

      const u = data.user || data;
      saveUser({ id: u.id, username: u.username, name: u.name || u.username });

      toast("로그인 성공");
      openAuth(false);

      state.stage = "projects";
      state.currentProject = null;
      state.currentDocument = null;

      await loadProjects();
      renderUserHeader();
      resetSelectionUI();
      renderStage();
    } catch (err) {
      console.error(err);
      toast(err.message || "로그인 실패", false);
    }
  });

  $("#registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const username = form.querySelector('input[name="username"]')?.value?.trim();
    const password = form.querySelector('input[name="password"]')?.value?.trim();
    const name = form.querySelector('input[name="name"]')?.value?.trim();

    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ username, password, name }),
      });

      toast("회원가입 성공! 로그인 해주세요.");
      showLoginPane();

      const lu = $("#loginForm")?.querySelector('input[name="username"]');
      const lp = $("#loginForm")?.querySelector('input[name="password"]');
      if (lu) lu.value = username;
      if (lp) lp.value = password;
      lu?.focus();
    } catch (err) {
      console.error(err);
      toast(err.message || "회원가입 실패", false);
    }
  });

  renderUserHeader();
  if (!state.user) {
    openAuth(true);
    showLoginPane();
  }
}

// ---------------------- Sidebar Nav ----------------------
function initSidebarNav() {
  $$(".navbtn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!state.user) return openAuth(true);

      const view = btn.dataset.view;

      $$(".navbtn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      if (view === "projects") {
        state.stage = "projects";
        state.currentProject = null;
        state.currentDocument = null;
        state.versions = [];
        await loadProjects().catch(() => {});
        resetSelectionUI();
        renderStage();
        return;
      }

      if (view === "stats") {
        state.stage = "stats";
        await refreshStage(true);
        return;
      }

      if (view === "documents") {
        if (!state.currentProject) return toast("먼저 프로젝트를 선택하세요.", false);
        state.stage = "project";
        state.projectTab = "documents";
        await refreshStage(true);
        return;
      }
      if (view === "tasks") {
        if (!state.currentProject) return toast("먼저 프로젝트를 선택하세요.", false);
        state.stage = "project";
        state.projectTab = "tasks";
        await refreshStage(true);
        return;
      }
      if (view === "versions") {
        if (!state.currentDocument) return toast("먼저 문서를 선택하세요.", false);
        state.stage = "document";
        await refreshStage(true);
        return;
      }
    });
  });
}

// ---------------------- Hide “난잡한 메뉴” ----------------------
function simplifySidebarUI() {
  $$(".navbtn").forEach((b) => {
    const v = b.dataset.view;
    if (v === "projects" || v === "stats") b.style.display = "";
    else b.style.display = "none";
  });
}

// ---------------------- Header / Quick Actions ----------------------
function setViewHeader(title, hint) {
  safeText($("#viewTitle"), title);
  safeText($("#viewHint"), hint);
}

function updateQuickActionState() {
  const logged = !!state.user;
  const p = !!state.currentProject;
  const d = !!state.currentDocument;

  const btnProj = $("#btnNewProject");
  const btnDoc = $("#btnNewDoc");
  const btnVer = $("#btnNewVersion");
  const btnTask = $("#btnNewTask");

  if (btnProj) {
    btnProj.disabled = !logged;
    btnProj.style.display = state.stage === "projects" ? "" : "none";
  }
  if (btnDoc) {
    btnDoc.disabled = !logged || !p;
    btnDoc.style.display = state.stage === "project" && state.projectTab === "documents" ? "" : "none";
  }
  if (btnTask) {
    btnTask.disabled = !logged || !p;
    btnTask.style.display = state.stage === "project" && state.projectTab === "tasks" ? "" : "none";
  }
  if (btnVer) {
    btnVer.disabled = !logged || !d;
    btnVer.style.display = state.stage === "document" ? "" : "none";
  }
}

function initQuickActions() {
  $("#btnNewProject")?.addEventListener("click", () => {
    if (!state.user) return openAuth(true);
    openCreateProjectModal();
  });

  $("#btnNewDoc")?.addEventListener("click", () => {
    if (!state.user) return openAuth(true);
    if (!state.currentProject) return toast("프로젝트를 먼저 선택하세요.", false);
    openCreateDocumentModal();
  });

  $("#btnNewVersion")?.addEventListener("click", async () => {
    if (!state.user) return openAuth(true);
    if (!state.currentDocument) return toast("문서를 먼저 선택하세요.", false);
    await openCreateVersionModal();
  });

  $("#btnNewTask")?.addEventListener("click", () => {
    if (!state.user) return openAuth(true);
    if (!state.currentProject) return toast("프로젝트를 먼저 선택하세요.", false);
    openCreateTaskModal();
  });

  $("#btnRefresh")?.addEventListener("click", async () => {
    await refreshStage(true);
  });

  $("#search")?.addEventListener("input", () => renderList());
}

// ---------------------- Data Loaders ----------------------
async function loadProjects() {
  const data = await api(`/projects`);
  state.projects = data.projects || [];
}
async function loadProjectMembers(projectId) {
  const data = await api(`/projects/${projectId}/members`);
  state.projectMembers = data.members || [];
}
async function loadDocuments(projectId) {
  const data = await api(`/documents/project/${projectId}`);
  state.documents = data.documents || [];
}
async function loadVersions(documentId) {
  const data = await api(`/versions/document/${documentId}`);
  state.versions = data.versions || [];
}
async function loadTasks(projectId) {
  const data = await api(`/tasks/project/${projectId}`);
  state.tasks = data.tasks || [];
}

// ✅ Stats Loaders
async function loadStatsForProject(projectId) {
  const [summary, contributions, tasksStatus, daily] = await Promise.all([
    api(`/stats/project/${projectId}/summary`),
    api(`/stats/project/${projectId}/contributions`),
    api(`/stats/project/${projectId}/tasks-status`),
    api(`/stats/project/${projectId}/daily-commits`),
  ]);

  state.stats.summary = summary?.summary || null;
  state.stats.contributions = contributions?.contributions || [];
  state.stats.taskStatus = tasksStatus?.task_status_stats || [];
  state.stats.dailyCommits = daily?.daily_commits || [];
}

async function loadStatsForUser() {
  const data = await api(`/stats/user/projects`);
  state.stats.userProjects = data?.projects || [];
}

// ---------------------- ✅ Breadcrumb ----------------------
function renderBreadcrumb({ includeVersion = false, versionLabel = "" } = {}) {
  const parts = [];

  parts.push({
    label: "Projects",
    onClick: async () => {
      state.stage = "projects";
      state.currentProject = null;
      state.projectMembers = [];
      state.documents = [];
      state.tasks = [];
      state.currentDocument = null;
      state.versions = [];
      resetSelectionUI();
      await loadProjects().catch(() => {});
      renderStage();
    },
  });

  if (state.currentProject) {
    parts.push({
      label: state.currentProject.name,
      onClick: async () => {
        state.stage = "project";
        state.projectTab = "documents";
        state.currentDocument = null;
        state.versions = [];
        resetSelectionUI();
        await refreshStage(true);
      },
    });
  }

  if (state.currentDocument) {
    parts.push({
      label: "Documents",
      onClick: async () => {
        state.stage = "project";
        state.projectTab = "documents";
        state.currentDocument = null;
        state.versions = [];
        resetSelectionUI();
        await refreshStage(true);
      },
    });
    parts.push({
      label: state.currentDocument.title,
      onClick: async () => {
        state.stage = "document";
        resetSelectionUI();
        await refreshStage(true);
      },
    });
  }

  if (includeVersion && versionLabel) {
    parts.push({ label: versionLabel, onClick: null });
  }

  const html = `
    <div class="muted" style="font-size:12px; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
      ${parts
        .map((p, idx) => {
          const isLast = idx === parts.length - 1;
          const clickable = !!p.onClick && !isLast;
          return `
          <span class="${clickable ? "js-crumb clickable" : ""}" data-idx="${idx}"
                style="${clickable ? "cursor:pointer; text-decoration:underline;" : "opacity:.9;"}">
            ${escapeHtml(p.label)}
          </span>
          ${idx < parts.length - 1 ? `<span style="opacity:.6;">></span>` : ""}
        `;
        })
        .join("")}
    </div>
  `;

  return { html, parts };
}

// ---------------------- Rendering ----------------------
function clearMainPanels() {
  safeHTML($("#list"), "");
  safeHTML($("#detail"), `<div class="muted">왼쪽 목록에서 항목을 선택하세요.</div>`);
}

function getSearchKeyword() {
  return ($("#search")?.value || "").trim().toLowerCase();
}

function formatAssigneeLabel(x) {
  return x.assignee_name
    ? `${x.assignee_name} (@${x.assignee_username || "?"})`
    : x.assignee_username || x.assignee_id || "-";
}

function renderList() {
  const listEl = $("#list");
  if (!listEl) return;
  listEl.innerHTML = "";

  const kw = getSearchKeyword();

  let items = [];
  let kind = "";

  if (state.stage === "projects") {
    items = state.projects;
    kind = "project";
  } else if (state.stage === "project") {
    if (state.projectTab === "documents") {
      items = state.documents;
      kind = "document";
    } else {
      items = state.tasks;
      kind = "task";
    }
  } else if (state.stage === "document") {
    items = state.versions;
    kind = "version";
  } else if (state.stage === "stats") {
    items = state.projects;
    kind = "project_stats";
  }

  if (kw) items = items.filter((x) => JSON.stringify(x).toLowerCase().includes(kw));

  if (!items.length) {
    listEl.innerHTML = `<div class="muted">표시할 항목이 없습니다.</div>`;
    return;
  }

  items.forEach((x) => {
    const div = document.createElement("div");
    div.className = "item";

    if (kind === "project") {
      div.innerHTML = `
        <div class="row" style="justify-content:space-between; gap:10px;">
          <div class="name">${escapeHtml(x.name)}</div>
          <div class="meta">id=${x.id}</div>
        </div>
        <div class="meta">${escapeHtml(x.description || "")}</div>
      `;
      div.addEventListener("click", () => onEnterProject(x));
    }

    if (kind === "project_stats") {
      div.innerHTML = `
        <div class="row" style="justify-content:space-between; gap:10px;">
          <div class="name">${escapeHtml(x.name)}</div>
          <div class="meta">id=${x.id}</div>
        </div>
        <div class="meta">${escapeHtml(x.description || "")}</div>
      `;
      div.addEventListener("click", async () => {
        state.currentProject = x;
        state.currentDocument = null;
        state.versions = [];
        resetSelectionUI();
        await refreshStage(true);
      });
    }

    if (kind === "document") {
      div.innerHTML = `
        <div class="row" style="justify-content:space-between; gap:10px;">
          <div class="name">${escapeHtml(x.title)}</div>
          <div class="meta">id=${x.id}</div>
        </div>
        <div class="meta">${escapeHtml(x.description || "")}</div>
      `;
      div.addEventListener("click", () => onEnterDocument(x));
    }

    if (kind === "task") {
      const label = formatAssigneeLabel(x);
      div.innerHTML = `
        <div class="row" style="justify-content:space-between; gap:10px;">
          <div class="name">${escapeHtml(x.title)}</div>
          <div class="meta">[${escapeHtml(x.status)}] id=${x.id}</div>
        </div>
        <div class="meta">${escapeHtml(x.description || "")}</div>
        <div class="meta">assignee: ${escapeHtml(label)}</div>
      `;
      div.addEventListener("click", () => renderTaskDetail(x));
    }

    if (kind === "version") {
      div.innerHTML = `
        <div class="row"><div class="name">v${x.version_no}</div><div class="meta">id=${x.id}</div></div>
        <div class="meta">author: ${escapeHtml(x.author_name || "")} (@${escapeHtml(x.author_username || "")}) / ${escapeHtml(x.created_at || "")}</div>
        <div class="meta">${escapeHtml(x.change_note || "")}</div>
        <div class="meta">${x.file_name ? "📎 " + escapeHtml(x.file_name) : ""}</div>
      `;
      div.addEventListener("click", () => renderVersionDetail(x));
    }

    listEl.appendChild(div);
  });
}

function renderStageDetailPlaceholder() {
  const el = $("#detail");
  if (!el) return;

  if (state.stage === "projects") {
    safeHTML(el, `<div class="muted">프로젝트를 선택하세요.</div>`);
    return;
  }
  if (state.stage === "project") {
    safeHTML(
      el,
      `<div class="muted">${state.projectTab === "documents" ? "문서를 선택하세요." : "태스크를 선택하세요."}</div>`
    );
    return;
  }
  if (state.stage === "document") {
    safeHTML(el, `<div class="muted">버전을 선택하세요.</div>`);
    return;
  }
  if (state.stage === "stats") {
    safeHTML(el, `<div class="muted">통계를 볼 프로젝트를 선택하세요. (왼쪽 목록)</div>`);
    return;
  }
}

// ---------------------- Members Quick ----------------------
async function showMembersQuick() {
  if (!state.currentProject) return;
  try {
    await loadProjectMembers(state.currentProject.id);
    const lines = (state.projectMembers || [])
      .map((m) => {
        const name = m.name || m.username || "member";
        const u = m.username ? `(@${m.username})` : "";
        return `- ${name} ${u}`.trim();
      })
      .join("\n");

    openConfirm({
      title: "프로젝트 멤버",
      message: lines || "멤버가 없습니다.",
      okText: "닫기",
      cancelText: "",
      onConfirm: null,
    });
  } catch (e) {
    toast("멤버 불러오기 실패", false);
  }
}

// ---------------------- Project Home Header ----------------------
function renderProjectHomeHeader() {
  const el = $("#detail");
  if (!el) return;
  const p = state.currentProject;

  const bc = renderBreadcrumb({ includeVersion: false });

  el.innerHTML = `
    <div class="detail">
      ${bc.html}

      <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-top:10px;">
        <div>
          <div style="font-weight:900; font-size:18px;">${escapeHtml(p?.name || "")}</div>
          <div class="muted">${escapeHtml(p?.description || "")}</div>
        </div>

        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
          <button class="btn ${state.projectTab === "documents" ? "" : "ghost"}" id="btnActionDocs" type="button">문서 보기</button>
          <button class="btn ${state.projectTab === "tasks" ? "" : "ghost"}" id="btnActionTasks" type="button">작업 보기</button>
          <button class="btn ghost" id="btnActionMembers" type="button">멤버 보기</button>
          <button class="btn ghost" id="btnGoStats" type="button">통계 보기</button>
          <button class="btn ghost" id="btnBackToProjects" type="button">← 프로젝트 목록</button>
        </div>
      </div>

      <div class="rowbtns" style="margin-top:12px;">
        <button class="btn ${state.projectTab === "documents" ? "" : "ghost"}" id="tabDocs" type="button">문서</button>
        <button class="btn ${state.projectTab === "tasks" ? "" : "ghost"}" id="tabTasks" type="button">태스크</button>
      </div>

      <div class="muted" style="margin-top:10px;">
        왼쪽 목록에서 ${state.projectTab === "documents" ? "문서" : "태스크"}를 선택하세요.
      </div>
    </div>
  `;

  // breadcrumb 클릭
  $$(".js-crumb.clickable").forEach((node) => {
    node.addEventListener("click", async () => {
      const idx = Number(node.dataset.idx);
      const part = bc.parts[idx];
      if (part?.onClick) await part.onClick();
    });
  });

  $("#btnBackToProjects")?.addEventListener("click", async () => {
    state.stage = "projects";
    state.currentProject = null;
    state.projectMembers = [];
    state.documents = [];
    state.tasks = [];
    state.currentDocument = null;
    state.versions = [];
    resetSelectionUI();
    await loadProjects();
    renderStage();
  });

  $("#btnActionDocs")?.addEventListener("click", async () => {
    state.projectTab = "documents";
    await refreshStage(true);
  });
  $("#btnActionTasks")?.addEventListener("click", async () => {
    state.projectTab = "tasks";
    await refreshStage(true);
  });

  // ✅ 탭 버튼(이벤트 없어서 안 눌리던 문제 해결)
  $("#tabDocs")?.addEventListener("click", async () => {
    state.projectTab = "documents";
    await refreshStage(true);
  });
  $("#tabTasks")?.addEventListener("click", async () => {
    state.projectTab = "tasks";
    await refreshStage(true);
  });

  $("#btnActionMembers")?.addEventListener("click", async () => {
    await showMembersQuick();
  });

  $("#btnGoStats")?.addEventListener("click", async () => {
    state.stage = "stats";
    $$(".navbtn").forEach((b) => b.classList.remove("active"));
    $(`.navbtn[data-view="stats"]`)?.classList.add("active");
    await refreshStage(true);
  });
}

// ---------------------- Document Header ----------------------
function renderDocumentHeader() {
  const el = $("#detail");
  if (!el) return;

  const p = state.currentProject;
  const d = state.currentDocument;

  const bc = renderBreadcrumb({ includeVersion: false });

  el.innerHTML = `
    <div class="detail">
      ${bc.html}

      <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-top:10px;">
        <div>
          <div class="muted" style="font-size:12px;">${escapeHtml(p?.name || "")} / 문서</div>
          <div style="font-weight:900; font-size:18px;">${escapeHtml(d?.title || "")}</div>
          <div class="muted">${escapeHtml(d?.description || "")}</div>
        </div>

        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
          <button class="btn" id="btnActionNewVersion" type="button">+ 버전 업로드</button>
          <button class="btn ghost" id="btnBackToProjectHome" type="button">← 문서/태스크</button>
        </div>
      </div>

      <div class="muted" style="margin-top:10px;">
        왼쪽에서 버전을 선택하세요.
      </div>
    </div>
  `;

  $$(".js-crumb.clickable").forEach((node) => {
    node.addEventListener("click", async () => {
      const idx = Number(node.dataset.idx);
      const part = bc.parts[idx];
      if (part?.onClick) await part.onClick();
    });
  });

  $("#btnActionNewVersion")?.addEventListener("click", async () => {
    if (!state.user) return openAuth(true);
    if (!state.currentDocument) return toast("문서를 먼저 선택하세요.", false);
    await openCreateVersionModal();
  });

  $("#btnBackToProjectHome")?.addEventListener("click", async () => {
    state.stage = "project";
    state.currentDocument = null;
    state.versions = [];
    resetSelectionUI();
    await refreshStage(true);
  });
}

// ---------------------- Stats Detail ----------------------
function renderStatsDetail() {
  const el = $("#detail");
  if (!el) return;

  const p = state.currentProject;
  const s = state.stats.summary;
  const contributions = state.stats.contributions || [];
  const taskStatus = state.stats.taskStatus || [];
  const daily = state.stats.dailyCommits || [];
  const userProjects = state.stats.userProjects || [];

  const bc = renderBreadcrumb({ includeVersion: false });

  const taskTotal = taskStatus.reduce((acc, r) => acc + Number(r.count || 0), 0);
  const maxCommit = Math.max(1, ...contributions.map((r) => Number(r.commit_count || 0)));

  el.innerHTML = `
    <div class="detail">
      ${bc.html}

      <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px; margin-top:10px;">
        <div>
          <div class="muted" style="font-size:12px;">통계 / 프로젝트</div>
          <div style="font-weight:900; font-size:18px;">${escapeHtml(p?.name || "(프로젝트 미선택)")}</div>
          <div class="muted">${escapeHtml(p?.description || "")}</div>
        </div>

        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
          <button class="btn ghost" id="btnStatsReload" type="button">새로고침</button>
          <button class="btn ghost" id="btnStatsBack" type="button">← 프로젝트 홈</button>
        </div>
      </div>

      ${
        !p
          ? `<div class="panel" style="margin-top:12px;"><div class="muted">왼쪽 목록에서 통계를 볼 프로젝트를 선택하세요.</div></div>`
          : `
      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">요약</div>
        <div class="row" style="gap:10px; flex-wrap:wrap;">
          <div class="kv" style="min-width:160px;"><span>문서</span><b>${escapeHtml(s?.documents ?? "-")}</b></div>
          <div class="kv" style="min-width:160px;"><span>버전</span><b>${escapeHtml(s?.versions ?? "-")}</b></div>
          <div class="kv" style="min-width:160px;"><span>멤버</span><b>${escapeHtml(s?.members ?? "-")}</b></div>
        </div>
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">태스크 상태</div>
        ${
          taskStatus.length
            ? `<div style="display:flex; flex-direction:column; gap:8px;">
                ${taskStatus
                  .map((r) => {
                    const count = Number(r.count || 0);
                    const pct = taskTotal ? Math.round((count / taskTotal) * 100) : 0;
                    return `
                      <div style="display:flex; gap:10px; align-items:center;">
                        <div class="muted" style="width:110px;">${escapeHtml(r.status)}</div>
                        <div style="flex:1; height:10px; border:1px solid rgba(255,255,255,.15); border-radius:999px; overflow:hidden;">
                          <div style="width:${pct}%; height:100%; background:rgba(255,255,255,.35);"></div>
                        </div>
                        <div class="muted" style="width:70px; text-align:right;">${count} (${pct}%)</div>
                      </div>
                    `;
                  })
                  .join("")}
              </div>`
            : `<div class="muted">태스크 통계가 없습니다.</div>`
        }
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">기여도 (멤버별 커밋 수)</div>
        ${
          contributions.length
            ? `<div style="display:flex; flex-direction:column; gap:8px;">
                ${contributions
                  .map((r) => {
                    const c = Number(r.commit_count || 0);
                    const pct = Math.round((c / maxCommit) * 100);
                    const name = r.name || r.user_id || "user";
                    return `
                      <div style="display:flex; gap:10px; align-items:center;">
                        <div style="width:160px;">${escapeHtml(name)}</div>
                        <div style="flex:1; height:10px; border:1px solid rgba(255,255,255,.15); border-radius:999px; overflow:hidden;">
                          <div style="width:${pct}%; height:100%; background:rgba(255,255,255,.35);"></div>
                        </div>
                        <div class="muted" style="width:120px; text-align:right;">
                          ${c} commits / +${Number(r.lines_added || 0)} -${Number(r.lines_deleted || 0)}
                        </div>
                      </div>
                    `;
                  })
                  .join("")}
              </div>`
            : `<div class="muted">기여도 데이터가 없습니다.</div>`
        }
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">일자별 커밋</div>
        ${
          daily.length
            ? `<div style="display:flex; flex-direction:column; gap:6px;">
                ${daily
                  .map((r) => `<div class="muted">${escapeHtml(r.date)} : ${Number(r.commit_count || 0)} commits</div>`)
                  .join("")}
              </div>`
            : `<div class="muted">일자별 커밋 데이터가 없습니다.</div>`
        }
      </div>
      `
      }

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">내 참여 프로젝트 (로그인 기준)</div>
        ${
          userProjects.length
            ? `<div style="display:flex; flex-direction:column; gap:6px;">
                ${userProjects
                  .map(
                    (r) =>
                      `<div class="muted">- ${escapeHtml(r.project_name)} (id=${r.project_id}) : ${Number(r.commit_count || 0)} commits</div>`
                  )
                  .join("")}
              </div>`
            : `<div class="muted">참여 프로젝트 통계가 없습니다.</div>`
        }
      </div>
    </div>
  `;

  $$(".js-crumb.clickable").forEach((node) => {
    node.addEventListener("click", async () => {
      const idx = Number(node.dataset.idx);
      const part = bc.parts[idx];
      if (part?.onClick) await part.onClick();
    });
  });

  $("#btnStatsReload")?.addEventListener("click", async () => {
    await refreshStage(true);
  });

  $("#btnStatsBack")?.addEventListener("click", async () => {
    if (!state.currentProject) {
      state.stage = "projects";
      await loadProjects().catch(() => {});
      renderStage();
      return;
    }
    state.stage = "project";
    state.projectTab = "documents";
    await refreshStage(true);
  });
}

// ---------------------- Selection (Enter) ----------------------
async function onEnterProject(p) {
  state.currentProject = p;
  state.currentDocument = null;
  state.versions = [];
  state.documents = [];
  state.tasks = [];
  state.projectMembers = [];

  state.stage = "project";
  state.projectTab = "documents";

  resetSelectionUI();
  await refreshStage(true);
}

async function onEnterDocument(d) {
  state.currentDocument = d;
  state.versions = [];
  state.stage = "document";

  resetSelectionUI();
  await refreshStage(true);
}

// ---------------------- Stage Render ----------------------
function renderStage() {
  if (!state.user) {
    clearMainPanels();
    resetSelectionUI();
    return;
  }

  updateQuickActionState();
  resetSelectionUI();

  if (state.stage === "projects") {
    setViewHeader("프로젝트", "내가 속한 프로젝트 목록만 표시합니다.");
    renderList();
    renderStageDetailPlaceholder();
    return;
  }

  if (state.stage === "project") {
    setViewHeader("프로젝트", state.projectTab === "documents" ? "문서 목록" : "태스크 목록");
    renderList();
    renderProjectHomeHeader();
    return;
  }

  if (state.stage === "document") {
    setViewHeader("버전", "선택한 문서의 버전 목록");
    renderList();
    renderDocumentHeader();
    return;
  }

  if (state.stage === "stats") {
    setViewHeader("통계", "프로젝트 요약/기여도/태스크/일자별 커밋");
    renderList();
    if (!state.currentProject) renderStageDetailPlaceholder();
    else renderStatsDetail();
    return;
  }
}

async function refreshStage(forceLoad = false) {
  if (!state.user) return;

  try {
    if (state.stage === "projects") {
      if (forceLoad) await loadProjects();
      renderStage();
      return;
    }

    if (state.stage === "project") {
      if (!state.currentProject) {
        state.stage = "projects";
        await loadProjects();
        renderStage();
        return;
      }

      if (state.projectTab === "documents") await loadDocuments(state.currentProject.id);
      else await loadTasks(state.currentProject.id);

      renderStage();
      return;
    }

    if (state.stage === "document") {
      if (!state.currentDocument) {
        state.stage = "project";
        renderStage();
        return;
      }
      await loadVersions(state.currentDocument.id);
      renderStage();
      return;
    }

    if (state.stage === "stats") {
      await loadProjects().catch(() => {});
      await loadStatsForUser().catch(() => {});
      if (state.currentProject) {
        await loadStatsForProject(state.currentProject.id);
      }
      renderStage();
      return;
    }
  } catch (e) {
    console.error(e);
    toast(e.message || "불러오기 실패", false);
  }
}

// ---------------------- Version / Task Detail ----------------------
function getFileDownloadUrl(v) {
  if (!v?.id) return "";
  return `${API_BASE}/files/version/${v.id}`;
}
function getFileInlineUrl(v) {
  if (!v?.id) return "";
  return `${API_BASE}/files/version/${v.id}/inline`;
}

function buildPreviewHtml(v) {
  if (!v.file_path) return `<div class="muted">(업로드 파일 없음)</div>`;

  const t = (v.file_type || "").toLowerCase();

  // ✅ iframe/img에 직접 /files 를 넣으면 Authorization이 안 붙어서 401 뜸
  // => 여기서는 "로딩 버튼 + 컨테이너"만 만들어두고,
  //    renderVersionDetail에서 blob URL로 실제 미리보기를 채움.
  if (t.startsWith("image/")) {
    return `
      <div id="filePreview" class="muted" style="border:1px solid rgba(255,255,255,.15); padding:10px; border-radius:10px;">
        <div class="row" style="justify-content:space-between; align-items:center;">
          <div>이미지 미리보기</div>
          <button class="btn ghost" id="btnLoadPreview" type="button">미리보기 로드</button>
        </div>
        <div id="filePreviewBody" style="margin-top:10px;"></div>
      </div>
    `;
  }

  if (t === "application/pdf") {
    return `
      <div id="filePreview" class="muted" style="border:1px solid rgba(255,255,255,.15); padding:10px; border-radius:10px;">
        <div class="row" style="justify-content:space-between; align-items:center;">
          <div>PDF 미리보기</div>
          <button class="btn ghost" id="btnLoadPreview" type="button">미리보기 로드</button>
        </div>
        <div id="filePreviewBody" style="margin-top:10px;"></div>
      </div>
    `;
  }

  if (t.startsWith("text/") || t.includes("json") || t.includes("xml") || t.includes("csv")) {
    return `
      <div class="muted" style="margin-bottom:6px;">텍스트 파일 미리보기는 '텍스트 로드' 버튼을 눌러주세요.</div>
      <pre id="txtPreview" class="muted" style="white-space:pre-wrap; max-height:420px; overflow:auto; border:1px solid rgba(255,255,255,.15); padding:10px; border-radius:10px;"></pre>
      <div class="row" style="justify-content:flex-end; gap:8px; margin-top:10px;">
        <button class="btn ghost" id="btnLoadText" type="button">텍스트 로드</button>
      </div>
    `;
  }

  return `<div class="muted">미리보기를 지원하지 않는 파일 형식입니다. 다운로드로 확인하세요.</div>`;
}

async function loadPreviewIntoDom(v) {
  if (!v?.file_path) return;
  const body = $("#filePreviewBody");
  if (!body) return;

  body.innerHTML = `<div class="muted">로딩중...</div>`;

  try {
    const inlineUrl = getFileInlineUrl(v);
    const objUrl = await getOrCreatePreviewObjectUrl(v.id, inlineUrl);
    const t = (v.file_type || "").toLowerCase();

    if (t.startsWith("image/")) {
      body.innerHTML = `<img src="${escapeHtml(objUrl)}" alt="preview" style="max-width:100%; border-radius:10px;" />`;
      return;
    }

    if (t === "application/pdf") {
      body.innerHTML = `<iframe src="${escapeHtml(objUrl)}" style="width:100%; height:520px; border:1px solid rgba(255,255,255,.15); border-radius:10px;"></iframe>`;
      return;
    }

    body.innerHTML = `<div class="muted">이 형식은 미리보기 로더가 지원하지 않습니다.</div>`;
  } catch (e) {
    console.error(e);
    body.innerHTML = `<div class="muted">미리보기 로드 실패</div>`;
  }
}

function renderVersionDetail(v) {
  const el = $("#detail");
  if (!el) return;

  const bc = renderBreadcrumb({ includeVersion: true, versionLabel: `v${v.version_no}` });

  const contentText = (v.content || "").trim();
  const showContent = contentText ? escapeHtml(contentText.slice(0, 3000)) : "";

  el.innerHTML = `
    <div class="detail">
      ${bc.html}

      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
        <div>
          <div class="muted" style="font-size:12px;">${escapeHtml(state.currentProject?.name || "")} / ${escapeHtml(
            state.currentDocument?.title || ""
          )}</div>
          <div style="font-weight:900; font-size:18px;">v${v.version_no}</div>
          <div class="muted">author: ${escapeHtml(v.author_name || "")} (@${escapeHtml(v.author_username || "")}) / ${escapeHtml(
            v.created_at || ""
          )}</div>
        </div>
        <button class="btn ghost" id="btnBackToVersions" type="button">← 버전 목록</button>
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">change_note</div>
        <div>${escapeHtml(v.change_note || "(없음)")}</div>
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">content</div>
        ${
          showContent
            ? `<div class="muted" style="white-space:pre-wrap;">${showContent}</div>`
            : `<div class="muted">(content가 비어있습니다)</div>`
        }
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">파일</div>
        <div class="meta">${v.file_name ? "📎 " + escapeHtml(v.file_name) : "(없음)"}</div>

        <div class="row" style="justify-content:flex-end; gap:8px; margin-top:8px;">
          ${v.file_path ? `<button class="btn ghost" id="btnDownloadFile" type="button">⬇ 다운로드</button>` : ""}
          ${v.file_path ? `<button class="btn ghost" id="btnOpenFileNewTab" type="button">↗ 새창</button>` : ""}
        </div>

        <div style="margin-top:12px;">
          ${buildPreviewHtml(v)}
        </div>
      </div>
    </div>
  `;

  $$(".js-crumb.clickable").forEach((node) => {
    node.addEventListener("click", async () => {
      const idx = Number(node.dataset.idx);
      const part = bc.parts[idx];
      if (part?.onClick) await part.onClick();
    });
  });

  $("#btnBackToVersions")?.addEventListener("click", () => {
    renderDocumentHeader();
  });

  // ✅ 다운로드 (Authorization 포함)
  $("#btnDownloadFile")?.addEventListener("click", async () => {
    try {
      const url = getFileDownloadUrl(v);
      const { blob, filename } = await fetchAuthedBlob(url);
      triggerDownloadFromBlob(blob, filename || v.file_name || `version_${v.id}`);
    } catch (e) {
      console.error(e);
      toast("다운로드 실패", false);
    }
  });

  // ✅ 새창 (Authorization 포함 -> blob url로 오픈)
  $("#btnOpenFileNewTab")?.addEventListener("click", async () => {
    try {
      const url = getFileInlineUrl(v);
      const { blob } = await fetchAuthedBlob(url);
      const blobUrl = URL.createObjectURL(blob);
      window.open(blobUrl, "_blank", "noopener,noreferrer");
      setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
    } catch (e) {
      console.error(e);
      toast("새창 열기 실패", false);
    }
  });

  // ✅ 미리보기 로드 버튼
  $("#btnLoadPreview")?.addEventListener("click", async () => {
    await loadPreviewIntoDom(v);
  });

  // ✅ 텍스트 로드도 inline 라우터에서 가져오기
  $("#btnLoadText")?.addEventListener("click", async () => {
    if (!v.file_path) return;
    try {
      const url = getFileInlineUrl(v);
      const token = loadToken();
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error("텍스트 로드 실패");
      const txt = await res.text();
      const pre = $("#txtPreview");
      if (pre) pre.textContent = txt.slice(0, 30000);
    } catch {
      toast("텍스트 로드 실패", false);
    }
  });
}

function renderTaskDetail(t) {
  const el = $("#detail");
  if (!el) return;

  const label = formatAssigneeLabel(t);

  el.innerHTML = `
    <div class="detail">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div class="muted" style="font-size:12px;">${escapeHtml(state.currentProject?.name || "")} / 태스크</div>
          <div style="font-weight:900; font-size:18px;">${escapeHtml(t.title)}</div>
          <div class="muted">status=${escapeHtml(t.status)} / id=${t.id}</div>
        </div>
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">description</div>
        <div>${escapeHtml(t.description || "(없음)")}</div>
      </div>

      <div class="panel" style="margin-top:12px;">
        <div class="panel-title">assignee</div>
        <div>${escapeHtml(label)}</div>
      </div>
    </div>
  `;
}

// ---------------------- Create Modals ----------------------
function openCreateProjectModal() {
  const form = $("#projectCreateForm");
  if (form) form.reset();
  openModal("projectModal", true);
  setTimeout(() => form?.querySelector('input[name="name"]')?.focus(), 0);
}
function openCreateDocumentModal() {
  const form = $("#documentCreateForm");
  if (form) form.reset();
  openModal("documentModal", true);
  setTimeout(() => form?.querySelector('input[name="title"]')?.focus(), 0);
}
async function openCreateVersionModal() {
  const form = $("#versionCreateForm");
  if (form) form.reset();

  if (state.currentProject) {
    await loadTasks(state.currentProject.id).catch(() => {});
    const sel = $("#versionTaskSelect");
    if (sel) {
      sel.innerHTML = `<option value="">태스크를 선택하세요</option>`;
      (state.tasks || []).forEach((t) => {
        const opt = document.createElement("option");
        opt.value = String(t.id);
        opt.textContent = `[${t.status}] ${t.title} (id=${t.id})`;
        sel.appendChild(opt);
      });
    }
  }

  openModal("versionModal", true);
  setTimeout(() => form?.querySelector('select[name="task_id"]')?.focus(), 0);
}
function openCreateTaskModal() {
  const form = $("#taskCreateForm");
  if (form) form.reset();
  openModal("taskModal", true);
  setTimeout(() => form?.querySelector('input[name="title"]')?.focus(), 0);
}

function setSubmitting(form, submitting) {
  const btn = form?.querySelector('button[type="submit"]');
  if (!btn) return;
  btn.disabled = submitting;
  btn.dataset._label ||= btn.textContent;
  btn.textContent = submitting ? "처리중..." : btn.dataset._label;
}

function initCreateForms() {
  $("#projectCreateForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.user) return openAuth(true);

    const form = e.currentTarget;
    const name = form.querySelector('input[name="name"]')?.value?.trim();
    const description = form.querySelector('textarea[name="description"]')?.value?.trim() || "";
    if (!name) return toast("프로젝트 이름은 필수입니다.", false);

    try {
      setSubmitting(form, true);
      await api("/projects", {
        method: "POST",
        body: JSON.stringify({ name, description, owner_id: state.user.id }),
      });

      toast("프로젝트 생성 성공");
      openModal("projectModal", false);

      await loadProjects();
      state.stage = "projects";
      renderStage();
    } catch (err) {
      console.error(err);
      toast(err.message || "프로젝트 생성 실패", false);
    } finally {
      setSubmitting(form, false);
    }
  });

  $("#documentCreateForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.user) return openAuth(true);
    if (!state.currentProject) return toast("프로젝트를 먼저 선택하세요.", false);

    const form = e.currentTarget;
    const title = form.querySelector('input[name="title"]')?.value?.trim();
    const description = form.querySelector('textarea[name="description"]')?.value?.trim() || "";
    if (!title) return toast("문서 제목은 필수입니다.", false);

    try {
      setSubmitting(form, true);
      await api("/documents", {
        method: "POST",
        body: JSON.stringify({
          project_id: state.currentProject.id,
          title,
          description,
          owner_id: state.user.id,
        }),
      });

      toast("문서 생성 성공");
      openModal("documentModal", false);

      await loadDocuments(state.currentProject.id);
      state.stage = "project";
      state.projectTab = "documents";
      renderStage();
    } catch (err) {
      console.error(err);
      toast(err.message || "문서 생성 실패", false);
    } finally {
      setSubmitting(form, false);
    }
  });

  $("#versionCreateForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.user) return openAuth(true);
    if (!state.currentDocument) return toast("문서를 먼저 선택하세요.", false);
    if (!state.currentProject) return toast("프로젝트를 먼저 선택하세요.", false);

    const form = e.currentTarget;
    const task_id = form.querySelector('select[name="task_id"]')?.value?.trim();
    const change_note = form.querySelector('input[name="change_note"]')?.value?.trim() || "";
    const content = form.querySelector('textarea[name="content"]')?.value?.trim() || "";
    const fileInput = form.querySelector('input[name="file"]');

    if (!task_id) return toast("태스크 선택은 필수입니다.", false);
    if (!change_note) return toast("change_note(커밋 메시지)는 필수입니다.", false);
    if (!fileInput || !fileInput.files || !fileInput.files[0]) return toast("파일은 필수입니다.", false);

    try {
      setSubmitting(form, true);

      const fd = new FormData();
      fd.append("task_id", String(task_id));
      fd.append("change_note", change_note);
      fd.append("content", content);
      fd.append("file", fileInput.files[0]);

      fd.append("document_id", String(state.currentDocument.id));
      await api(`/versions`, {
        method: "POST",
        body: fd,
      });

      toast("버전 업로드 성공");
      openModal("versionModal", false);

      await loadVersions(state.currentDocument.id);
      state.stage = "document";
      renderStage();
    } catch (err) {
      console.error(err);
      toast(err.message || "버전 업로드 실패", false);
    } finally {
      setSubmitting(form, false);
    }
  });

  $("#taskCreateForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.user) return openAuth(true);
    if (!state.currentProject) return toast("프로젝트를 먼저 선택하세요.", false);

    const form = e.currentTarget;
    const title = form.querySelector('input[name="title"]')?.value?.trim();
    const description = form.querySelector('textarea[name="description"]')?.value?.trim() || "";
    const assignee_username = form.querySelector('input[name="assignee_username"]')?.value?.trim() || "";
    if (!title) return toast("태스크 제목은 필수입니다.", false);

    try {
      setSubmitting(form, true);
      const body = { project_id: state.currentProject.id, title, description };
      if (assignee_username) body.assignee_username = assignee_username;

      await api("/tasks", { method: "POST", body: JSON.stringify(body) });

      toast("태스크 생성 성공");
      openModal("taskModal", false);

      await loadTasks(state.currentProject.id);
      state.stage = "project";
      state.projectTab = "tasks";
      renderStage();
    } catch (err) {
      console.error(err);
      toast(err.message || "태스크 생성 실패", false);
    } finally {
      setSubmitting(form, false);
    }
  });
}

// ---------------------- Boot ----------------------
document.addEventListener("DOMContentLoaded", async () => {
  initAuth();
  initQuickActions();
  initSidebarNav();
  initModalClosers();
  initConfirmModal();
  initCreateForms();

  simplifySidebarUI();

  clearMainPanels();
  resetSelectionUI();

  if (state.user && !state.token) {
    toast("세션이 만료되었습니다. 다시 로그인하세요.", false);
    clearUser();
    renderUserHeader();
    openAuth(true);
    showLoginPane();
    return;
  }

  if (state.user) {
    state.stage = "projects";
    await loadProjects().catch(() => {});
    $$(".navbtn").forEach((b) => b.classList.remove("active"));
    $(`.navbtn[data-view="projects"]`)?.classList.add("active");
    renderStage();
  } else {
    renderStage();
  }
});
