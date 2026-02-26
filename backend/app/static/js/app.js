/**
 * APK Manager — Main Application JavaScript
 * Handles: API calls, navigation, project/version/file tree, upload, toast notifications.
 */

// ═══════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════
const state = {
    token: null,
    user: null,
    currentPage: "dashboard",
    selectedFile: null,
};

// ═══════════════════════════════════════════════════════════════
// API CLIENT
// ═══════════════════════════════════════════════════════════════
const API_BASE = "/api";

async function apiRequest(method, path, body = null, isFormData = false) {
    const headers = {};
    if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
    if (!isFormData && body) headers["Content-Type"] = "application/json";

    const opts = { method, headers };
    if (body) opts.body = isFormData ? body : JSON.stringify(body);

    const res = await fetch(API_BASE + path, opts);
    const json = await res.json();
    if (!res.ok || !json.success) {
        throw new Error(json.error || json.detail || "Request failed");
    }
    return json.data;
}

// Upload with XMLHttpRequest for real progress tracking
async function apiUpload(path, formData, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", API_BASE + path);
        if (state.token) xhr.setRequestHeader("Authorization", `Bearer ${state.token}`);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable && onProgress) {
                onProgress(Math.round((e.loaded / e.total) * 100));
            }
        };

        xhr.onload = () => {
            try {
                const json = JSON.parse(xhr.responseText);
                if (xhr.status >= 200 && xhr.status < 300 && json.success) {
                    resolve(json.data);
                } else {
                    reject(new Error(json.error || json.detail || "Upload failed"));
                }
            } catch {
                reject(new Error("Invalid server response"));
            }
        };
        xhr.onerror = () => reject(new Error("Network error during upload"));
        xhr.send(formData);
    });
}

// ═══════════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════
function showToast(title, message = "", type = "info") {
    const icons = {
        success: `<svg viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
        error: `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="16" r="1" fill="currentColor"/></svg>`,
        info: `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="8" r="1" fill="currentColor"/></svg>`,
    };

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
    <div class="toast-icon">${icons[type]}</div>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      ${message ? `<div class="toast-msg">${message}</div>` : ""}
    </div>
    <div class="toast-close" onclick="removeToast(this.parentElement)">
      <svg viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </div>`;

    document.getElementById("toast-container").appendChild(toast);
    setTimeout(() => removeToast(toast), 4500);
}

function removeToast(toast) {
    if (!toast || toast.classList.contains("removing")) return;
    toast.classList.add("removing");
    setTimeout(() => toast.remove(), 280);
}

// ═══════════════════════════════════════════════════════════════
// MODALS
// ═══════════════════════════════════════════════════════════════
function openModal(id) {
    document.getElementById(id).classList.remove("hidden");
}

function closeModal(id) {
    document.getElementById(id).classList.add("hidden");
}

// Close modal on overlay click
document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
            overlay.classList.add("hidden");
        }
    });
});

// ═══════════════════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════════════════
function loadStoredAuth() {
    const token = localStorage.getItem("apk-token");
    const user = localStorage.getItem("apk-user");
    if (token && user) {
        state.token = token;
        state.user = JSON.parse(user);
        return true;
    }
    return false;
}

function saveAuth(token, user) {
    state.token = token;
    state.user = user;
    localStorage.setItem("apk-token", token);
    localStorage.setItem("apk-user", JSON.stringify(user));
}

function clearAuth() {
    state.token = null;
    state.user = null;
    localStorage.removeItem("apk-token");
    localStorage.removeItem("apk-user");
}

async function logout() {
    clearAuth();
    document.getElementById("app").classList.add("hidden");
    document.getElementById("login-screen").classList.remove("hidden");
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("login-btn");
    const spinner = btn.querySelector(".btn-spinner");
    const label = btn.querySelector("span");
    const errorEl = document.getElementById("login-error");

    btn.disabled = true;
    spinner.classList.remove("hidden");
    label.classList.add("hidden");
    errorEl.classList.add("hidden");

    try {
        const data = await apiRequest("POST", "/auth/login", {
            username: document.getElementById("login-username").value.trim(),
            password: document.getElementById("login-password").value,
        });
        saveAuth(data.access_token, data.user);
        initApp();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        label.classList.remove("hidden");
    }
});

function togglePassword() {
    const input = document.getElementById("login-password");
    input.type = input.type === "password" ? "text" : "password";
}

// ═══════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════
function navigate(page) {
    state.currentPage = page;

    // Update nav items
    document.querySelectorAll(".nav-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.page === page);
    });

    // Toggle pages
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    document.getElementById(`page-${page}`).classList.add("active");

    // Update page title
    const titles = { dashboard: "Dashboard", projects: "Projects", users: "Users" };
    document.getElementById("page-title").textContent = titles[page] || page;

    // Close mobile sidebar
    closeSidebarMobile();

    // Load data
    if (page === "dashboard") loadDashboard();
    if (page === "projects") loadProjects();
    if (page === "users") loadUsers();

    return false;
}

// ═══════════════════════════════════════════════════════════════
// SIDEBAR
// ═══════════════════════════════════════════════════════════════
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");
    sidebar.classList.toggle("open");
    overlay.classList.toggle("open");
}

function closeSidebarMobile() {
    document.getElementById("sidebar").classList.remove("open");
    document.getElementById("sidebar-overlay").classList.remove("open");
}

// ═══════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════
async function loadDashboard() {
    try {
        const stats = await apiRequest("GET", "/dashboard/stats");
        document.getElementById("stat-projects").textContent = stats.total_projects;
        document.getElementById("stat-versions").textContent = stats.total_versions;
        document.getElementById("stat-files").textContent = stats.total_files;
        document.getElementById("stat-storage").textContent = formatBytes(stats.total_storage_bytes);

        document.querySelectorAll(".stat-card").forEach((c) => c.classList.remove("loading"));

        // Recent projects
        const projects = await apiRequest("GET", "/projects");
        renderRecentProjects(projects.slice(0, 6));

        // Chart and recent downloads logs
        if (stats.download_trends) renderDownloadsChart(stats.download_trends);
        if (stats.recent_downloads) renderRecentDownloads(stats.recent_downloads);
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

function renderDownloadsChart(trends) {
    const ctx = document.getElementById('downloadsChart');
    if (!ctx) return;

    if (window.downloadsChartInstance) {
        window.downloadsChartInstance.destroy();
    }

    const labels = trends.map(t => t.date);
    const data = trends.map(t => t.count);

    window.downloadsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Downloads',
                data: data,
                borderColor: '#38bdf8', /* var(--primary) doesn't work inside chart directly sometimes, hardcode hex */
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, color: '#94a3b8' } },
                x: { ticks: { color: '#94a3b8' } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function renderRecentDownloads(logs) {
    const tbody = document.getElementById("recent-downloads-list");
    if (!tbody) return;

    if (!logs || !logs.length) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; padding: 1rem; color: var(--text-3); font-style: italic;">No recent downloads.</td></tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr style="border-bottom: 1px solid var(--border);">
            <td style="padding: 0.5rem; color: var(--text-2); font-family: monospace;">${escHtml(log.ip_address)}</td>
            <td style="padding: 0.5rem; color: var(--text-1); font-weight: 500; font-size: 0.85rem;">${escHtml(log.filename)}</td>
            <td style="padding: 0.5rem; text-align: right; color: var(--text-3); font-size: 0.75rem;">${formatDate(log.downloaded_at)}</td>
        </tr>
    `).join("");
}

function renderRecentProjects(projects) {
    const el = document.getElementById("recent-projects-list");
    if (!projects.length) {
        el.innerHTML = `<div class="empty-state"><p>No projects yet. <a href="#" onclick="navigate('projects')">Create one →</a></p></div>`;
        return;
    }
    el.innerHTML = projects
        .map(
            (p) => `
    <div class="project-card" onclick="navigate('projects')">
      <div class="project-card-name">${escHtml(p.name)}</div>
      <div class="project-card-desc">${escHtml(p.description || "No description")}</div>
      <div class="project-card-meta">
        <span class="tag tag-primary">${p.version_count} version${p.version_count !== 1 ? "s" : ""}</span>
        <span>${formatDate(p.created_at)}</span>
      </div>
    </div>`
        )
        .join("");
}

// ═══════════════════════════════════════════════════════════════
// PROJECTS TREE
// ═══════════════════════════════════════════════════════════════
async function loadProjects() {
    const treeEl = document.getElementById("project-tree");
    treeEl.innerHTML = `<div class="empty-state"><div class="skeleton" style="height:80px;border-radius:12px;"></div></div>`;

    try {
        const projects = await apiRequest("GET", "/projects");
        if (!projects.length) {
            treeEl.innerHTML = `
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none"><path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" stroke="currentColor" stroke-width="2"/></svg>
          <p>No projects yet</p>
          ${isAdmin() ? `<button class="btn btn-primary sm" onclick="openCreateProjectModal()">Create First Project</button>` : ""}
        </div>`;
            return;
        }
        treeEl.innerHTML = projects.map(renderProjectNode).join("");
    } catch (err) {
        showToast("Error", err.message, "error");
        treeEl.innerHTML = "";
    }
}

function renderProjectNode(project) {
    const adminActions = isAdmin()
        ? `<button class="btn-icon" onclick="event.stopPropagation(); openCreateVersionModal(${project.id})" title="Add Version">
         <svg viewBox="0 0 24 24" fill="none"><line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
       </button>
       <button class="btn-icon delete" onclick="event.stopPropagation(); deleteProject(${project.id}, '${escHtml(project.name)}')" title="Delete Project">
         <svg viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
       </button>`
        : "";

    return `
  <div class="tree-project" id="proj-${project.id}">
    <div class="tree-project-header" onclick="toggleProject(${project.id})">
      <svg class="tree-toggle-icon" viewBox="0 0 24 24" fill="none">
        <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div style="flex:1">
        <div class="tree-project-name">${escHtml(project.name)}</div>
        ${project.description ? `<div style="font-size:0.78rem;color:var(--text-3)">${escHtml(project.description)}</div>` : ""}
      </div>
      <div class="tree-project-meta">
        <span class="tag tag-primary">${project.version_count} ver</span>
      </div>
      <div class="tree-project-actions">${adminActions}</div>
    </div>
    <div class="tree-project-body">
      <div class="tree-versions" id="versions-${project.id}">
        <div style="text-align:center;padding:1rem;color:var(--text-3);font-size:0.82rem">Loading versions...</div>
      </div>
    </div>
  </div>`;
}

async function toggleProject(projectId) {
    const el = document.getElementById(`proj-${projectId}`);
    const isExpanded = el.classList.contains("expanded");

    if (!isExpanded) {
        el.classList.add("expanded");
        await loadVersions(projectId);
    } else {
        el.classList.remove("expanded");
    }
}

async function loadVersions(projectId) {
    const versionsEl = document.getElementById(`versions-${projectId}`);
    try {
        const versions = await apiRequest("GET", `/projects/${projectId}/versions`);
        if (!versions.length) {
            versionsEl.innerHTML = `
        <div class="empty-state" style="padding:1rem">
          <p>No versions yet</p>
          ${isAdmin() ? `<button class="btn btn-ghost sm" onclick="openCreateVersionModal(${projectId})">Add Version</button>` : ""}
        </div>`;
            return;
        }
        versionsEl.innerHTML = versions.map((v) => renderVersionNode(v, projectId)).join("");
    } catch (err) {
        versionsEl.innerHTML = `<div class="empty-state"><p>Failed to load versions</p></div>`;
    }
}

function renderVersionNode(version, projectId) {
    const adminActions = isAdmin()
        ? `<button class="btn-icon" onclick="event.stopPropagation(); openUploadModal(${version.id})" title="Upload APK" style="color:var(--primary)">
         <svg viewBox="0 0 24 24" fill="none"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
       </button>`
        : "";

    return `
  <div class="tree-version" id="ver-${version.id}">
    <div class="tree-version-header" onclick="toggleVersion(${version.id})">
      <svg class="ver-toggle" viewBox="0 0 24 24" fill="none">
        <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="ver-string">v${escHtml(version.version_string)}</span>
      <span style="font-size:0.75rem;color:var(--text-3)">${version.file_count} file${version.file_count !== 1 ? "s" : ""}</span>
      ${adminActions}
    </div>
    <div class="tree-version-body" id="files-${version.id}">
      <div style="text-align:center;padding:0.75rem;color:var(--text-3);font-size:0.82rem">Loading files...</div>
    </div>
  </div>`;
}

async function toggleVersion(versionId) {
    const el = document.getElementById(`ver-${versionId}`);
    const isExpanded = el.classList.contains("expanded");

    if (!isExpanded) {
        el.classList.add("expanded");
        await loadFiles(versionId);
    } else {
        el.classList.remove("expanded");
    }
}

async function loadFiles(versionId) {
    const filesEl = document.getElementById(`files-${versionId}`);
    try {
        const files = await apiRequest("GET", `/versions/${versionId}/files`);
        if (!files.length) {
            filesEl.innerHTML = `
        <div class="empty-state" style="padding:0.75rem">
          <p>No APK files uploaded</p>
          ${isAdmin() ? `<button class="btn btn-ghost sm" onclick="openUploadModal(${versionId})">Upload APK</button>` : ""}
        </div>`;
            return;
        }
        filesEl.innerHTML = files.map((f) => renderFileRow(f)).join("");
    } catch (err) {
        filesEl.innerHTML = `<div class="empty-state" style="padding:0.75rem"><p>Failed to load files</p></div>`;
    }
}

function renderFileRow(file) {
    const adminDelete = isAdmin()
        ? `<button class="btn-icon delete" onclick="deleteAPKFile(${file.id}, '${escHtml(file.filename)}')" title="Delete">
         <svg viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
       </button>`
        : "";

    return `
  <div class="apk-file-row" id="file-row-${file.id}">
    <div class="apk-file-icon">
      <svg viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="2"/><polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2"/></svg>
    </div>
    <div class="apk-file-info">
      <div class="apk-file-name">${escHtml(file.filename)}</div>
      <div class="apk-file-meta">${formatBytes(file.file_size)} · ${formatDate(file.uploaded_at)}${file.uploader_name ? ` · by ${escHtml(file.uploader_name)}` : ""}</div>
    </div>
    <div class="apk-actions">
      <button class="btn-icon" onclick="copyDownloadLink(${file.id})" title="Copy Link">
        <svg viewBox="0 0 24 24" fill="none"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
      <a class="btn-icon download" href="/api/files/${file.id}/download" onclick="addAuthHeader(event, ${file.id})" title="Download">
        <svg viewBox="0 0 24 24" fill="none"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><polyline points="7 10 12 15 17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </a>
      ${adminDelete}
    </div>
  </div>`;
}

function copyDownloadLink(fileId) {
    const url = `${window.location.origin}/api/files/${fileId}/download?token=${state.token}`;
    navigator.clipboard.writeText(url).then(() => {
        showToast("Copied!", "Download link copied to clipboard", "success");
    }).catch(err => {
        showToast("Error", "Failed to copy link", "error");
    });
}

// Intercept download to add auth header via fetch + blob
function addAuthHeader(event, fileId) {
    event.preventDefault();
    fetch(`/api/files/${fileId}/download`, {
        headers: { Authorization: `Bearer ${state.token}` },
    })
        .then((res) => {
            if (!res.ok) throw new Error("Download failed");
            const disposition = res.headers.get("content-disposition");
            let filename = `file_${fileId}.apk`;
            if (disposition) {
                const match = disposition.match(/filename="?([^"]+)"?/);
                if (match) filename = match[1];
            }
            return res.blob().then((blob) => ({ blob, filename }));
        })
        .then(({ blob, filename }) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        })
        .catch((err) => showToast("Download Failed", err.message, "error"));
}

// ═══════════════════════════════════════════════════════════════
// CREATE PROJECT
// ═══════════════════════════════════════════════════════════════
function openCreateProjectModal() {
    document.getElementById("proj-name").value = "";
    document.getElementById("proj-desc").value = "";
    openModal("create-project-modal");
}

async function submitCreateProject(event) {
    event.preventDefault();
    const name = document.getElementById("proj-name").value.trim();
    const description = document.getElementById("proj-desc").value.trim();

    try {
        await apiRequest("POST", "/projects", { name, description: description || null });
        closeModal("create-project-modal");
        showToast("Success", `Project "${name}" created`, "success");
        loadProjects();
        loadDashboard();
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

async function deleteProject(id, name) {
    if (!confirm(`Delete project "${name}" and ALL its data? This cannot be undone.`)) return;
    try {
        await apiRequest("DELETE", `/projects/${id}`);
        showToast("Deleted", `Project "${name}" deleted`, "success");
        loadProjects();
        loadDashboard();
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

// ═══════════════════════════════════════════════════════════════
// CREATE VERSION
// ═══════════════════════════════════════════════════════════════
function openCreateVersionModal(projectId) {
    document.getElementById("ver-string").value = "";
    document.getElementById("ver-project-id").value = projectId;
    openModal("create-version-modal");
}

async function submitCreateVersion(event) {
    event.preventDefault();
    const projectId = document.getElementById("ver-project-id").value;
    const versionString = document.getElementById("ver-string").value.trim();

    try {
        await apiRequest("POST", `/projects/${projectId}/versions`, { version_string: versionString });
        closeModal("create-version-modal");
        showToast("Success", `Version "${versionString}" created`, "success");

        // Reload this project's versions
        const projEl = document.getElementById(`proj-${projectId}`);
        if (projEl && projEl.classList.contains("expanded")) {
            await loadVersions(projectId);
        }
        loadDashboard();
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

// ═══════════════════════════════════════════════════════════════
// UPLOAD APK
// ═══════════════════════════════════════════════════════════════
function openUploadModal(versionId) {
    document.getElementById("upload-version-id").value = versionId;
    clearFileSelection();
    document.getElementById("upload-progress-container").classList.add("hidden");
    document.getElementById("progress-bar").style.width = "0%";
    openModal("upload-modal");
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".apk")) {
        showToast("Invalid File", "Only .apk files are allowed", "error");
        event.target.value = "";
        return;
    }

    state.selectedFile = file;
    document.getElementById("upload-area").style.display = "none";
    const fileSelectedEl = document.getElementById("file-selected");
    fileSelectedEl.classList.remove("hidden");
    document.getElementById("selected-filename").textContent = file.name;
    document.getElementById("selected-filesize").textContent = formatBytes(file.size);
    document.getElementById("upload-btn").disabled = false;
}

function clearFileSelection() {
    state.selectedFile = null;
    document.getElementById("apk-file-input").value = "";
    document.getElementById("upload-area").style.display = "";
    document.getElementById("file-selected").classList.add("hidden");
    document.getElementById("upload-btn").disabled = true;
}

async function submitUpload() {
    if (!state.selectedFile) return;
    const versionId = document.getElementById("upload-version-id").value;

    const formData = new FormData();
    formData.append("file", state.selectedFile);

    const progressContainer = document.getElementById("upload-progress-container");
    const progressBar = document.getElementById("progress-bar");
    const progressPct = document.getElementById("progress-pct");
    const uploadBtn = document.getElementById("upload-btn");

    progressContainer.classList.remove("hidden");
    uploadBtn.disabled = true;
    document.getElementById("upload-area").style.display = "none";
    document.getElementById("file-selected").classList.add("hidden");

    try {
        await apiUpload(`/versions/${versionId}/upload`, formData, (pct) => {
            progressBar.style.width = `${pct}%`;
            progressPct.textContent = `${pct}%`;
        });

        closeModal("upload-modal");
        showToast("Upload Successful", `${state.selectedFile.name} uploaded`, "success");

        // Reload files in this version
        const verEl = document.getElementById(`ver-${versionId}`);
        if (verEl && verEl.classList.contains("expanded")) {
            await loadFiles(versionId);
        }
        loadDashboard();
    } catch (err) {
        showToast("Upload Failed", err.message, "error");
        progressContainer.classList.add("hidden");
        uploadBtn.disabled = false;
        clearFileSelection();
    }
}

// Drag and drop
const uploadArea = document.getElementById("upload-area");
uploadArea.addEventListener("dragover", (e) => { e.preventDefault(); uploadArea.style.borderColor = "var(--primary)"; });
uploadArea.addEventListener("dragleave", () => { uploadArea.style.borderColor = ""; });
uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = "";
    const file = e.dataTransfer.files[0];
    if (file) {
        const fakeEvent = { target: { files: [file], value: "" } };
        handleFileSelect(fakeEvent);
    }
});

// ═══════════════════════════════════════════════════════════════
// DELETE APK FILE
// ═══════════════════════════════════════════════════════════════
async function deleteAPKFile(fileId, filename) {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;
    try {
        await apiRequest("DELETE", `/files/${fileId}`);
        document.getElementById(`file-row-${fileId}`)?.remove();
        showToast("Deleted", `${filename} deleted`, "success");
        loadDashboard();
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

// ═══════════════════════════════════════════════════════════════
// REGISTER USER (admin only)
// ═══════════════════════════════════════════════════════════════
async function submitRegister(event) {
    event.preventDefault();
    const payload = {
        username: document.getElementById("reg-username").value.trim(),
        email: document.getElementById("reg-email").value.trim(),
        password: document.getElementById("reg-password").value,
        role: document.getElementById("reg-role").value,
    };
    try {
        await apiRequest("POST", "/auth/register", payload);
        closeModal("register-modal");
        showToast("User Created", `${payload.username} has been added`, "success");
        document.getElementById("register-form").reset();
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

// ═══════════════════════════════════════════════════════════════
// USERS MANAGEMENT
// ═══════════════════════════════════════════════════════════════
async function loadUsers() {
    console.log("loadUsers: starting to fetch");
    const tbody = document.getElementById("users-table-body");
    if (!tbody) {
        console.error("loadUsers: could not find users-table-body!");
        return;
    }

    tbody.innerHTML = `<tr><td colspan="5" style="padding: 2rem; text-align: center; color: var(--text-3);">Loading users...</td></tr>`;
    try {
        const users = await apiRequest("GET", "/users");
        console.log("loadUsers: fetch returned", users);
        if (!users || !Array.isArray(users) || !users.length) {
            tbody.innerHTML = `<tr><td colspan="5" style="padding: 2rem; text-align: center; color: var(--text-3);">No users found.</td></tr>`;
            return;
        }
        const htmlStr = users.map(renderUserRow).join("");
        tbody.innerHTML = htmlStr;
        console.log("loadUsers: rendered users successfully");
    } catch (err) {
        console.error("loadUsers: error occurred", err);
        tbody.innerHTML = `<tr><td colspan="5" style="padding: 2rem; text-align: center; color: var(--error);">Failed to load users: ${err.message}</td></tr>`;
        showToast("Error", err.message, "error");
    }
}

function renderUserRow(user) {
    const isSelf = user.id === state.user.id;
    const assignProjectBtn = `<button class="btn-icon" onclick="openAssignProjectsModal(${user.id}, '${escHtml(user.username)}')" title="Assign Projects" style="color:var(--primary)">
             <svg viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
           </button>`;

    const changePwdBtn = `<button class="btn-icon" onclick="openChangePasswordModal(${user.id}, '${escHtml(user.username)}')" title="Change Password" style="color:var(--text-1)">
             <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
           </button>`;

    const deleteBtn = isSelf
        ? `<span style="color:var(--text-3); font-size: 0.8rem; padding: 0 0.5rem">(You)</span>`
        : `<button class="btn-icon delete" onclick="deleteUser(${user.id}, '${escHtml(user.username)}')" title="Delete User">
             <svg viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M19 6v14a2 2 0 01-2 2H7a2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
           </button>`;

    return `
    <tr id="user-row-${user.id}" style="border-bottom: 1px solid var(--border);">
      <td style="padding: 1rem; font-weight: 500;">${escHtml(user.username)}</td>
      <td style="padding: 1rem; color: var(--text-2);">${escHtml(user.email)}</td>
      <td style="padding: 1rem;">
        <span class="tag ${user.role === 'ADMIN' ? 'tag-primary' : 'tag-secondary'}">${user.role}</span>
      </td>
      <td style="padding: 1rem; color: var(--text-2);">${formatDate(user.created_at)}</td>
      <td style="padding: 1rem; text-align: right; display: flex; justify-content: flex-end; gap: 0.25rem;">
        ${assignProjectBtn}
        ${changePwdBtn}
        ${deleteBtn}
      </td>
    </tr>`;
}

async function deleteUser(id, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) return;
    try {
        await apiRequest("DELETE", `/users/${id}`);
        showToast("Deleted", `User "${username}" has been deleted`, "success");
        document.getElementById(`user-row-${id}`)?.remove();
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

function openChangePasswordModal(userId, username) {
    document.getElementById("chpwd-user-id").value = userId;
    document.getElementById("chpwd-username").textContent = username;
    document.getElementById("chpwd-password").value = "";
    openModal("change-pwd-modal");
}

async function submitChangePassword(event) {
    event.preventDefault();
    const userId = document.getElementById("chpwd-user-id").value;
    const password = document.getElementById("chpwd-password").value;

    try {
        await apiRequest("PATCH", `/users/${userId}/password`, { password });
        closeModal("change-pwd-modal");
        showToast("Success", "Password updated successfully", "success");
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

async function openAssignProjectsModal(userId, username) {
    document.getElementById("assign-user-id").value = userId;
    document.getElementById("assign-username").textContent = username;
    const listContainer = document.getElementById("assign-projects-list");
    listContainer.innerHTML = `<div style="text-align: center; color: var(--text-3);">Loading projects...</div>`;
    openModal("assign-projects-modal");

    try {
        const allProjects = await apiRequest("GET", "/projects");
        const userProjects = await apiRequest("GET", `/users/${userId}/projects`);

        if (!allProjects.length) {
            listContainer.innerHTML = `<div style="color: var(--text-3); font-style: italic;">No projects available.</div>`;
            return;
        }

        const htmlStr = allProjects.map(p => {
            const isChecked = userProjects.includes(p.id) ? "checked" : "";
            return `
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer; padding: 0.25rem 0;">
                <input type="checkbox" name="project_ids" value="${p.id}" ${isChecked} />
                <span style="color: var(--text-1); font-weight: 500;">${escHtml(p.name)}</span>
            </label>
            `;
        }).join("");

        listContainer.innerHTML = htmlStr;
    } catch (err) {
        listContainer.innerHTML = `<div style="color: var(--error);">Error: ${err.message}</div>`;
        showToast("Error loading projects", err.message, "error");
    }
}

async function submitAssignProjects(event) {
    event.preventDefault();
    const userId = document.getElementById("assign-user-id").value;
    const checkboxes = document.querySelectorAll('#assign-projects-form input[name="project_ids"]:checked');
    const projectIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

    try {
        await apiRequest("PUT", `/users/${userId}/projects`, { project_ids: projectIds });
        closeModal("assign-projects-modal");
        showToast("Success", "Projects assigned successfully", "success");
    } catch (err) {
        showToast("Error", err.message, "error");
    }
}

// ═══════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════
function isAdmin() {
    return state.user?.role === "ADMIN";
}

function escHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function formatBytes(bytes) {
    if (!bytes) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function formatDate(iso) {
    if (!iso) return "";
    return new Date(iso).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════
function initApp() {
    document.getElementById("login-screen").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");

    // Update user info in sidebar
    const u = state.user;
    document.getElementById("user-name").textContent = u.username;
    document.getElementById("user-role-badge").textContent = u.role;
    document.getElementById("user-avatar").textContent = u.username[0].toUpperCase();

    // Show admin-only elements
    if (isAdmin()) {
        document.querySelectorAll(".admin-only").forEach((el) => el.classList.remove("hidden"));
    }

    navigate("dashboard");
}

// Boot
if (loadStoredAuth()) {
    initApp();
}
