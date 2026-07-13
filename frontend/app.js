// State Management
let state = {
  apiUrl: 'http://localhost:8000/api/v1',
  token: localStorage.getItem('taskflow_token') || '',
  userEmail: localStorage.getItem('taskflow_email') || '',
  projects: [],
  projectPage: 1,
  projectPageSize: 8,
  projectTotalPages: 1,
  activeProjectId: null,
  activeProjectName: '',
  activeProjectDesc: '',
  tasks: [],
  taskPage: 1,
  taskPageSize: 5,
  taskTotalPages: 1,
  taskStatusFilter: 'All'
};

// UI Elements
const els = {
  apiBaseUrl: document.getElementById('api-base-url'),
  btnSaveApiUrl: document.getElementById('btn-save-api-url'),
  authView: document.getElementById('auth-view'),
  dashboardView: document.getElementById('dashboard-view'),
  tabLogin: document.getElementById('tab-login'),
  tabRegister: document.getElementById('tab-register'),
  formLogin: document.getElementById('form-login'),
  formRegister: document.getElementById('form-register'),
  loginEmail: document.getElementById('login-email'),
  loginPassword: document.getElementById('login-password'),
  registerEmail: document.getElementById('register-email'),
  registerPassword: document.getElementById('register-password'),
  projectList: document.getElementById('project-list'),
  btnNewProject: document.getElementById('btn-new-project'),
  btnProjectPrev: document.getElementById('btn-project-prev'),
  btnProjectNext: document.getElementById('btn-project-next'),
  projectPageNum: document.getElementById('project-page-num'),
  activeProjectName: document.getElementById('active-project-name'),
  activeProjectDesc: document.getElementById('active-project-desc'),
  btnEditProject: document.getElementById('btn-edit-project'),
  btnDeleteProject: document.getElementById('btn-delete-project'),
  btnNewTask: document.getElementById('btn-new-task'),
  taskFilterBar: document.getElementById('task-filter-bar'),
  taskBoardContent: document.getElementById('task-board-content'),
  taskPaginationBar: document.getElementById('task-pagination-bar'),
  btnTaskPrev: document.getElementById('btn-task-prev'),
  btnTaskNext: document.getElementById('btn-task-next'),
  taskPageInfo: document.getElementById('task-page-info'),
  userDisplayEmail: document.getElementById('user-display-email'),
  btnLogout: document.getElementById('btn-logout'),
  toastContainer: document.getElementById('toast-container'),
  
  // Dialogs
  projectDialog: document.getElementById('project-dialog'),
  formProject: document.getElementById('form-project'),
  projectDialogTitle: document.getElementById('project-dialog-title'),
  projectDialogId: document.getElementById('project-dialog-id'),
  projectNameInput: document.getElementById('project-name-input'),
  projectDescInput: document.getElementById('project-desc-input'),
  btnCloseProjectDialog: document.getElementById('btn-close-project-dialog'),
  btnSubmitProjectDialog: document.getElementById('btn-submit-project-dialog'),
  
  taskDialog: document.getElementById('task-dialog'),
  formTask: document.getElementById('form-task'),
  taskDialogTitle: document.getElementById('task-dialog-title'),
  taskDialogId: document.getElementById('task-dialog-id'),
  taskTitleInput: document.getElementById('task-title-input'),
  taskDescInput: document.getElementById('task-desc-input'),
  taskStatusInput: document.getElementById('task-status-input'),
  btnCloseTaskDialog: document.getElementById('btn-close-task-dialog'),
  btnSubmitTaskDialog: document.getElementById('btn-submit-task-dialog'),

  // Diagnostics Telemetry
  statusHealthDot: document.getElementById('status-health-dot'),
  statusHealthText: document.getElementById('status-health-text'),
  telemetryRateKey: document.getElementById('telemetry-rate-key'),
  telemetryRateLimit: document.getElementById('telemetry-rate-limit'),
  telemetryRateRemaining: document.getElementById('telemetry-rate-remaining'),
  telemetryRateRetry: document.getElementById('telemetry-rate-retry'),
  telemetryVerDeprecated: document.getElementById('telemetry-ver-deprecated'),
  telemetryVerSunset: document.getElementById('telemetry-ver-sunset')
};

// Intercept headers and parse rate limit metadata
function parseTelemetry(headers) {
  // Capture Rate limiting info
  const limit = headers.get('X-RateLimit-Limit') || '100';
  const remaining = headers.get('X-RateLimit-Remaining');
  const retryAfter = headers.get('Retry-After');
  
  // Capture Version warning deprecation details
  const deprecated = headers.get('X-API-Deprecated');
  const sunset = headers.get('Sunset');

  if (limit) els.telemetryRateLimit.textContent = limit;
  if (remaining) els.telemetryRateRemaining.textContent = remaining;
  
  if (retryAfter) {
    els.telemetryRateRetry.textContent = `${retryAfter}s`;
    showToast(`Rate limit triggered. Locked out for ${retryAfter}s`, 'error');
  } else {
    els.telemetryRateRetry.textContent = 'None';
  }

  if (state.token) {
    els.telemetryRateKey.textContent = 'user';
    els.telemetryRateKey.className = 'value badge badge-green';
  } else {
    els.telemetryRateKey.textContent = 'ip';
    els.telemetryRateKey.className = 'value badge';
  }

  if (deprecated === 'true') {
    els.telemetryVerDeprecated.textContent = 'deprecated';
    els.telemetryVerDeprecated.className = 'value badge badge-red';
  } else {
    els.telemetryVerDeprecated.textContent = 'active';
    els.telemetryVerDeprecated.className = 'value badge badge-green';
  }

  els.telemetryVerSunset.textContent = sunset || 'None';
}

// Global API Request handler wrapper
async function apiRequest(path, options = {}) {
  const url = `${state.apiUrl}${path}`;
  
  // Inject headers
  options.headers = options.headers || {};
  if (state.token) {
    options.headers['Authorization'] = `Bearer ${state.token}`;
  }

  try {
    const response = await fetch(url, options);
    
    // Process telemetry headers immediately
    parseTelemetry(response.headers);

    if (response.status === 401) {
      showToast('Session expired or unauthorized. Please login.', 'error');
      logout();
      return null;
    }

    if (response.status === 429) {
      const data = await response.json();
      showToast(data.detail || 'Rate limit exceeded.', 'error');
      return null;
    }

    if (response.status === 204) {
      return true;
    }

    const data = await response.json();
    if (!response.ok) {
      showToast(data.detail || 'Something went wrong.', 'error');
      return null;
    }

    return data;
  } catch (error) {
    showToast('Failed to connect to API server. Ensure it is running.', 'error');
    console.error('Fetch Error:', error);
    updateHealthUI(false);
    return null;
  }
}

// Uptime Check Database Health check
async function verifyHealth() {
  const url = `${state.apiUrl}/health`;
  try {
    const response = await fetch(url);
    parseTelemetry(response.headers);
    
    if (response.ok) {
      const data = await response.json();
      updateHealthUI(data.database === 'healthy');
    } else {
      updateHealthUI(false);
    }
  } catch (error) {
    updateHealthUI(false);
  }
}

function updateHealthUI(isOnline) {
  if (isOnline) {
    els.statusHealthDot.className = 'status-dot status-online';
    els.statusHealthText.textContent = 'ONLINE';
    els.statusHealthText.style.color = '#10b981';
  } else {
    els.statusHealthDot.className = 'status-dot status-offline';
    els.statusHealthText.textContent = 'OFFLINE';
    els.statusHealthText.style.color = '#ef4444';
  }
}

// Toast Notifications helper
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-message">${message}</span>
    <button class="toast-close">&times;</button>
  `;
  
  els.toastContainer.appendChild(toast);
  
  const closeBtn = toast.querySelector('.toast-close');
  closeBtn.onclick = () => toast.remove();
  
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Authentication Logic
async function login(email, password) {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const data = await apiRequest('/auth/login', {
    method: 'POST',
    body: params
  });

  if (data && data.access_token) {
    state.token = data.access_token;
    state.userEmail = email;
    localStorage.setItem('taskflow_token', data.access_token);
    localStorage.setItem('taskflow_email', email);
    
    showToast('Signed in successfully.');
    initDashboard();
  }
}

async function register(email, password) {
  const data = await apiRequest('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: jsonStringify({ email, password })
  });

  if (data) {
    showToast('User created! Please sign in.', 'success');
    // Switch tab to login
    els.tabLogin.click();
  }
}

function logout() {
  state.token = '';
  state.userEmail = '';
  localStorage.removeItem('taskflow_token');
  localStorage.removeItem('taskflow_email');
  
  state.activeProjectId = null;
  state.projects = [];
  state.tasks = [];

  els.userDisplayEmail.textContent = 'Not Signed In';
  els.authView.classList.add('active');
  els.dashboardView.classList.remove('active');
  
  // Hide dashboard controls
  hideProjectControls();
}

// CRUD - Project Functions
async function fetchProjects() {
  const path = `/projects/?page=${state.projectPage}&page_size=${state.projectPageSize}`;
  const data = await apiRequest(path);
  if (data) {
    state.projects = data.data;
    state.projectTotalPages = data.pagination.total_pages;
    renderProjects();
  }
}

function renderProjects() {
  els.projectList.innerHTML = '';
  if (state.projects.length === 0) {
    els.projectList.innerHTML = '<p class="empty-state">No projects created yet.</p>';
    els.btnProjectPrev.disabled = true;
    els.btnProjectNext.disabled = true;
    return;
  }

  state.projects.forEach(p => {
    const btn = document.createElement('button');
    btn.className = `project-item ${state.activeProjectId === p.id ? 'active' : ''}`;
    btn.textContent = p.name;
    btn.onclick = () => selectProject(p);
    els.projectList.appendChild(btn);
  });

  els.projectPageNum.textContent = state.projectPage;
  els.btnProjectPrev.disabled = state.projectPage <= 1;
  els.btnProjectNext.disabled = state.projectPage >= state.projectTotalPages;
}

function selectProject(project) {
  state.activeProjectId = project.id;
  state.activeProjectName = project.name;
  state.activeProjectDesc = project.description || '';
  state.taskPage = 1;
  
  // Update board header
  els.activeProjectName.textContent = project.name;
  els.activeProjectDesc.textContent = project.description || 'No description provided.';
  
  // Show board controls
  els.btnEditProject.style.display = 'inline-flex';
  els.btnDeleteProject.style.display = 'inline-flex';
  els.btnNewTask.style.display = 'inline-flex';
  els.taskFilterBar.style.display = 'flex';
  els.taskPaginationBar.style.display = 'flex';

  renderProjects(); // Refresh selection state classes
  fetchTasks();
}

function hideProjectControls() {
  els.activeProjectName.textContent = 'Select a Project';
  els.activeProjectDesc.textContent = 'Create or select a project from the left sidebar to manage tasks.';
  els.btnEditProject.style.display = 'none';
  els.btnDeleteProject.style.display = 'none';
  els.btnNewTask.style.display = 'none';
  els.taskFilterBar.style.display = 'none';
  els.taskPaginationBar.style.display = 'none';
  els.taskBoardContent.innerHTML = `
    <div class="board-welcome-state">
      <div class="illustration-placeholder">📋</div>
      <h3>Manage Your Tasks Seamlessly</h3>
      <p>Sign in, choose a project, and add checklist items. Changes are fully synchronized with the FastAPI backend.</p>
    </div>
  `;
}

// CRUD - Tasks Functions
async function fetchTasks() {
  if (!state.activeProjectId) return;
  let path = `/tasks/?project_id=${state.activeProjectId}&page=${state.taskPage}&page_size=${state.taskPageSize}`;
  if (state.taskStatusFilter !== 'All') {
    path += `&status=${state.taskStatusFilter}`;
  }

  const data = await apiRequest(path);
  if (data) {
    state.tasks = data.data;
    state.taskTotalPages = data.pagination.total_pages;
    renderTasks();
  }
}

function renderTasks() {
  els.taskBoardContent.innerHTML = '';
  if (state.tasks.length === 0) {
    els.taskBoardContent.innerHTML = `
      <div class="board-welcome-state">
        <div class="illustration-placeholder">🔍</div>
        <h3>No Tasks Found</h3>
        <p>No checklist items match the current status filter. Create a new task to get started.</p>
      </div>
    `;
    els.btnTaskPrev.disabled = true;
    els.btnTaskNext.disabled = true;
    return;
  }

  state.tasks.forEach(t => {
    const card = document.createElement('div');
    card.className = 'task-card';
    
    let badgeClass = 'badge-todo';
    if (t.status === 'InProgress') badgeClass = 'badge-inprogress';
    if (t.status === 'Completed') badgeClass = 'badge-completed';

    card.innerHTML = `
      <div class="task-info-group">
        <div class="task-badge-row">
          <span class="task-title">${t.title}</span>
          <span class="badge ${badgeClass}">${t.status}</span>
        </div>
        <span class="task-desc">${t.description || 'No description.'}</span>
      </div>
      <div class="task-actions">
        <button class="btn btn-secondary btn-mini btn-toggle-status" data-id="${t.id}" data-title="${t.title}" data-status="${t.status}">Toggle Status</button>
        <button class="btn btn-secondary btn-mini btn-edit-task" data-id="${t.id}" data-title="${t.title}" data-desc="${t.description || ''}" data-status="${t.status}">Edit</button>
        <button class="btn btn-danger btn-mini btn-delete-task" data-id="${t.id}">Delete</button>
      </div>
    `;
    
    // Task Event bindings
    card.querySelector('.btn-toggle-status').onclick = (e) => {
      const btn = e.target;
      const current = btn.dataset.status;
      let next = 'Todo';
      if (current === 'Todo') next = 'InProgress';
      else if (current === 'InProgress') next = 'Completed';
      
      updateTask(btn.dataset.id, btn.dataset.title, next);
    };

    card.querySelector('.btn-edit-task').onclick = (e) => {
      const btn = e.target;
      openTaskDialog(btn.dataset.id, btn.dataset.title, btn.dataset.desc, btn.dataset.status);
    };

    card.querySelector('.btn-delete-task').onclick = (e) => {
      const id = e.target.dataset.id;
      deleteTask(id);
    };

    els.taskBoardContent.appendChild(card);
  });

  els.taskPageInfo.textContent = `Page ${state.taskPage} of ${state.taskTotalPages || 1}`;
  els.btnTaskPrev.disabled = state.taskPage <= 1;
  els.btnTaskNext.disabled = state.taskPage >= state.taskTotalPages;
}

async function updateTask(id, title, status) {
  const data = await apiRequest(`/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: jsonStringify({ title, status })
  });

  if (data) {
    showToast('Task updated successfully.');
    fetchTasks();
  }
}

async function deleteTask(id) {
  if (confirm('Delete task?')) {
    const success = await apiRequest(`/tasks/${id}`, { method: 'DELETE' });
    if (success) {
      showToast('Task deleted successfully.');
      fetchTasks();
    }
  }
}

// Dialog helpers
function openProjectDialog(id = '', name = '', desc = '') {
  els.projectDialogId.value = id;
  els.projectNameInput.value = name;
  els.projectDescInput.value = desc;
  els.projectDialogTitle.textContent = id ? 'Edit Project' : 'Create Project';
  els.btnSubmitProjectDialog.textContent = id ? 'Update' : 'Create';
  els.projectDialog.showModal();
}

function openTaskDialog(id = '', title = '', desc = '', status = 'Todo') {
  els.taskDialogId.value = id;
  els.taskTitleInput.value = title;
  els.taskDescInput.value = desc;
  els.taskStatusInput.value = status;
  els.taskDialogTitle.textContent = id ? 'Edit Task' : 'Add Task';
  els.btnSubmitTaskDialog.textContent = id ? 'Update' : 'Add Task';
  els.taskDialog.showModal();
}

function jsonStringify(obj) {
  return JSON.stringify(obj);
}

// Initializer
function initDashboard() {
  els.userDisplayEmail.textContent = state.userEmail;
  els.authView.classList.remove('active');
  els.dashboardView.classList.add('active');
  
  state.projectPage = 1;
  fetchProjects();
}

// Event Bindings setup
function setupEventListeners() {
  // Apply API URL
  els.btnSaveApiUrl.onclick = () => {
    state.apiUrl = els.apiBaseUrl.value.trim();
    showToast(`Base API URL changed to ${state.apiUrl}`);
    verifyHealth();
    if (state.token) {
      fetchProjects();
    }
  };

  // Auth Tabs Toggle
  els.tabLogin.onclick = () => {
    els.tabLogin.classList.add('active');
    els.tabRegister.classList.remove('active');
    els.formLogin.classList.add('active');
    els.formRegister.classList.remove('active');
  };
  
  els.tabRegister.onclick = () => {
    els.tabRegister.classList.add('active');
    els.tabLogin.classList.remove('active');
    els.formRegister.classList.add('active');
    els.formLogin.classList.remove('active');
  };

  // Auth Submit
  els.formLogin.onsubmit = (e) => {
    e.preventDefault();
    login(els.loginEmail.value, els.loginPassword.value);
  };
  
  els.formRegister.onsubmit = (e) => {
    e.preventDefault();
    register(els.registerEmail.value, els.registerPassword.value);
  };

  els.btnLogout.onclick = () => {
    logout();
    showToast('Logged out.');
  };

  // Sidebar navigation Project pagination
  els.btnProjectPrev.onclick = () => {
    if (state.projectPage > 1) {
      state.projectPage--;
      fetchProjects();
    }
  };
  
  els.btnProjectNext.onclick = () => {
    if (state.projectPage < state.projectTotalPages) {
      state.projectPage++;
      fetchProjects();
    }
  };

  // CRUD: Project Action clicks
  els.btnNewProject.onclick = () => openProjectDialog();
  
  els.btnEditProject.onclick = () => {
    openProjectDialog(state.activeProjectId, state.activeProjectName, state.activeProjectDesc);
  };

  els.btnDeleteProject.onclick = async () => {
    if (confirm(`Are you sure you want to delete project "${state.activeProjectName}"? All its tasks will be deleted.`)) {
      const success = await apiRequest(`/projects/${state.activeProjectId}`, { method: 'DELETE' });
      if (success) {
        showToast('Project deleted successfully.');
        state.activeProjectId = null;
        hideProjectControls();
        fetchProjects();
      }
    }
  };

  // Dialog Project submits
  els.btnCloseProjectDialog.onclick = () => els.projectDialog.close();
  els.formProject.onsubmit = async (e) => {
    e.preventDefault();
    const id = els.projectDialogId.value;
    const name = els.projectNameInput.value.trim();
    const description = els.projectDescInput.value.trim();

    let data;
    if (id) {
      // Edit mode
      data = await apiRequest(`/projects/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify({ name, description })
      });
    } else {
      // Create mode
      data = await apiRequest('/projects/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify({ name, description })
      });
    }

    if (data) {
      showToast(id ? 'Project modified.' : 'Project created successfully.');
      els.projectDialog.close();
      
      if (id) {
        state.activeProjectName = name;
        state.activeProjectDesc = description;
        els.activeProjectName.textContent = name;
        els.activeProjectDesc.textContent = description || 'No description.';
      }
      fetchProjects();
    }
  };

  // CRUD: Task Actions
  els.btnNewTask.onclick = () => openTaskDialog();

  els.btnCloseTaskDialog.onclick = () => els.taskDialog.close();
  els.formTask.onsubmit = async (e) => {
    e.preventDefault();
    const id = els.taskDialogId.value;
    const title = els.taskTitleInput.value.trim();
    const description = els.taskDescInput.value.trim();
    const statusVal = els.taskStatusInput.value;

    let data;
    if (id) {
      // Update task
      data = await apiRequest(`/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify({ title, description, status: statusVal })
      });
    } else {
      // Create task
      data = await apiRequest('/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify({
          title,
          description,
          status: statusVal,
          project_id: state.activeProjectId
        })
      });
    }

    if (data) {
      showToast(id ? 'Task modified.' : 'Task created successfully.');
      els.taskDialog.close();
      fetchTasks();
    }
  };

  // Task Filter buttons
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.onclick = (e) => {
      filterBtns.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.taskStatusFilter = e.target.dataset.status;
      state.taskPage = 1;
      fetchTasks();
    };
  });

  // Task Pagination clicks
  els.btnTaskPrev.onclick = () => {
    if (state.taskPage > 1) {
      state.taskPage--;
      fetchTasks();
    }
  };
  
  els.btnTaskNext.onclick = () => {
    if (state.taskPage < state.taskTotalPages) {
      state.taskPage++;
      fetchTasks();
    }
  };
}

// Initial Bootstrapping
window.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  verifyHealth();
  
  // Set intervals to keep health status updated
  setInterval(verifyHealth, 15000);

  if (state.token) {
    initDashboard();
  }
});
