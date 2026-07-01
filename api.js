// api.js — 基于 fetch 的 API 层，替换 data.js
// 所有 CRUD 函数都是 async，调用后端 API

// ===================== 配置 =====================
const API_BASE = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('qingtian_token');
}

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

async function apiRequest(method, path, body) {
  const url = API_BASE + path;
  const options = { method, headers: getAuthHeaders() };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(url, options);
  if (!res.ok) {
    let detail = '请求失败: ' + res.status;
    try { const err = await res.json(); detail = err.detail || detail; } catch (e) {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ===================== 认证 =====================

async function doLogin(email, password) {
  const res = await fetch(API_BASE + '/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, password: password }),
  });
  if (!res.ok) {
    let detail = '登录失败: ' + res.status;
    try { const err = await res.json(); detail = err.detail || detail; } catch (e) {}
    throw new Error(detail);
  }
  const data = await res.json();
  localStorage.setItem('qingtian_token', data.access_token);
  localStorage.setItem('qingtian_user', JSON.stringify(data.user));
  return data.user;
}

function getCurrentUser() {
  var stored = localStorage.getItem('qingtian_user');
  return stored ? JSON.parse(stored) : null;
}

function requireLogin() {
  var user = getCurrentUser();
  var token = getToken();
  if (!user || !token) {
    window.location.href = 'index.html';
    return null;
  }
  return user;
}

function logout() {
  localStorage.removeItem('qingtian_token');
  localStorage.removeItem('qingtian_user');
  window.location.href = 'index.html';
}

// ===================== 项目 CRUD =====================

async function fetchProjects(keyword) {
  var params = keyword ? '?keyword=' + encodeURIComponent(keyword) : '';
  return apiRequest('GET', '/api/projects' + params);
}

async function fetchProject(projectId) {
  return apiRequest('GET', '/api/projects/' + projectId);
}

async function createProject(name, description, color) {
  return apiRequest('POST', '/api/projects', {
    name: name,
    description: description || '',
    color: color || '#4F46E5',
  });
}

async function updateProjectById(projectId, updates) {
  var body = {};
  if (updates.name !== undefined) body.name = updates.name;
  if (updates.desc !== undefined) body.description = updates.desc;
  if (updates.description !== undefined) body.description = updates.description;
  if (updates.color !== undefined) body.color = updates.color;
  return apiRequest('PUT', '/api/projects/' + projectId, body);
}

async function deleteProjectById(projectId) {
  return apiRequest('DELETE', '/api/projects/' + projectId);
}

// ===================== 任务 CRUD =====================

async function fetchProjectTasks(pid, filters) {
  filters = filters || {};
  var params = new URLSearchParams();
  if (filters.status) params.set('status', filters.status);
  if (filters.priority) params.set('priority', filters.priority);
  if (filters.assignee_id) params.set('assignee_id', filters.assignee_id);
  var qs = params.toString();
  return apiRequest('GET', '/api/projects/' + pid + '/tasks' + (qs ? '?' + qs : ''));
}

async function fetchMyTasks(limit) {
  limit = limit || 50;
  return apiRequest('GET', '/api/tasks/my?limit=' + limit);
}

async function fetchTask(taskId) {
  return apiRequest('GET', '/api/tasks/' + taskId);
}

async function createNewTask(pid, title, priority, assignee_id, due_date, description) {
  return apiRequest('POST', '/api/projects/' + pid + '/tasks', {
    title: title,
    priority: priority || 'medium',
    assignee_id: assignee_id || null,
    due_date: due_date || '',
    description: description || '',
  });
}

async function updateTaskById(taskId, updates) {
  var body = {};
  if (updates.title !== undefined) body.title = updates.title;
  if (updates.status !== undefined) body.status = updates.status;
  if (updates.priority !== undefined) body.priority = updates.priority;
  if (updates.assignee !== undefined) body.assignee_id = updates.assignee;
  if (updates.assignee_id !== undefined) body.assignee_id = updates.assignee_id;
  if (updates.due !== undefined) body.due_date = updates.due;
  if (updates.due_date !== undefined) body.due_date = updates.due_date;
  if (updates.desc !== undefined) body.description = updates.desc;
  if (updates.description !== undefined) body.description = updates.description;
  return apiRequest('PUT', '/api/tasks/' + taskId, body);
}

async function deleteTaskById(taskId) {
  return apiRequest('DELETE', '/api/tasks/' + taskId);
}

async function cycleTaskStatus(taskId) {
  var task = await fetchTask(taskId);
  var order = ['todo', 'in_progress', 'done'];
  var currentIdx = order.indexOf(task.status);
  var nextStatus = order[(currentIdx + 1) % order.length];
  return apiRequest('PATCH', '/api/tasks/' + taskId + '/status', { status: nextStatus });
}

// ===================== 评论 CRUD =====================

async function fetchTaskComments(taskId) {
  return apiRequest('GET', '/api/tasks/' + taskId + '/comments');
}

async function addCommentToTask(taskId, text) {
  return apiRequest('POST', '/api/tasks/' + taskId + '/comments', { text: text });
}

async function deleteCommentById(commentId) {
  return apiRequest('DELETE', '/api/comments/' + commentId);
}

// ===================== 仪表盘 =====================

async function fetchDashboardStats() {
  return apiRequest('GET', '/api/dashboard/stats');
}

async function fetchMyDashboardTasks(limit) {
  return apiRequest('GET', '/api/dashboard/my-tasks?limit=' + (limit || 5));
}

async function fetchRecentProjects(limit) {
  return apiRequest('GET', '/api/dashboard/recent-projects?limit=' + (limit || 3));
}

// ===================== 页面加载辅助 =====================

var _cacheProjects = null;
var _cacheTasks = {};
var _cacheComments = {};

async function loadDashboardData() {
  // 并行加载仪表盘所需的所有数据
  var results = await Promise.all([
    fetchProjects(),
    fetchDashboardStats(),
    fetchMyDashboardTasks(5),
    fetchRecentProjects(3),
  ]);
  return {
    projects: results[0],
    stats: results[1],
    myTasks: results[2],
    recentProjects: results[3],
  };
}

// ===================== 工具函数 =====================

function getTodayStr() {
  var now = new Date();
  return now.getFullYear() + ' 年 ' + (now.getMonth() + 1) + ' 月 ' + now.getDate() + ' 日';
}

function priorityLabel(p) {
  return p === 'high' ? '高' : p === 'medium' ? '中' : '低';
}

function statusLabel(s) {
  var map = { todo: '📋 待办', in_progress: '🔄 进行中', done: '✅ 已完成' };
  return map[s] || s;
}

function getAssigneeDisplay(task) {
  if (task.assignee && task.assignee.name) return task.assignee.name;
  return task.assignee_id || '?';
}

function getCommentAuthorDisplay(c) {
  if (c.author && c.author.name) return c.author.name;
  return c.author_id || '?';
}

// ===================== Toast 通知 =====================

function showToast(message, type) {
  type = type || 'success';
  var toast = document.createElement('div');
  toast.style.cssText = [
    'position: fixed; top: 20px; right: 20px; z-index: 9999;',
    'padding: 12px 20px; border-radius: 8px; font-size: 14px; font-weight: 500;',
    'box-shadow: 0 8px 24px rgba(0,0,0,0.15);',
    'color: #fff; max-width: 360px;',
    'transform: translateX(120%); transition: transform 0.3s ease;',
    'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;',
  ].join(' ');
  var colors = {
    success: '#059669', error: '#DC2626', warning: '#D97706', info: '#4F46E5',
  };
  toast.style.background = colors[type] || colors.info;
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(function () { toast.style.transform = 'translateX(0)'; });
  setTimeout(function () {
    toast.style.transform = 'translateX(120%)';
    setTimeout(function () { toast.remove(); }, 300);
  }, 3000);
}

// ===================== 确认弹窗 =====================

function showConfirm(message, onConfirm, onCancel) {
  var overlay = document.createElement('div');
  overlay.style.cssText = [
    'position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 10000;',
    'display: flex; align-items: center; justify-content: center;',
    'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;',
  ].join(' ');
  overlay.innerHTML = [
    '<div style="background:#fff;border-radius:12px;padding:24px;width:380px;box-shadow:0 20px 60px rgba(0,0,0,0.2);">',
    '  <p style="font-size:15px;color:#374151;margin-bottom:20px;line-height:1.5;">' + message + '</p>',
    '  <div style="display:flex;gap:8px;justify-content:flex-end;">',
    '    <button class="confirm-cancel-btn" style="padding:8px 16px;border-radius:8px;border:1px solid #D1D5DB;background:#fff;color:#374151;font-size:14px;cursor:pointer;font-family:inherit;">取消</button>',
    '    <button class="confirm-ok-btn" style="padding:8px 16px;border-radius:8px;border:none;background:#DC2626;color:#fff;font-size:14px;cursor:pointer;font-family:inherit;">确认</button>',
    '  </div>',
    '</div>',
  ].join('');
  document.body.appendChild(overlay);
  overlay.querySelector('.confirm-cancel-btn').onclick = function () {
    overlay.remove();
    if (onCancel) onCancel();
  };
  overlay.querySelector('.confirm-ok-btn').onclick = function () {
    overlay.remove();
    if (onConfirm) onConfirm();
  };
  overlay.addEventListener('click', function (e) {
    if (e.target === this) { overlay.remove(); if (onCancel) onCancel(); }
  });
}
