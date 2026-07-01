// 晴天项目协作 - 共享数据
// 所有页面通过 <script src="data.js"> 加载

// ===================== 原始数据（不要改动） =====================

let PROJECTS = [
  {
    id: 'p1',
    name: '穗穗念（追星日记小程序）',
    desc: '面向追星女孩的轻量级微信小程序，记录与偶像相关的每一次心动瞬间。v1.0 初穗版上线微信登录、云同步、物料记录等核心功能。',
    progress: 55,
    color: '#4F46E5',
    members: ['L', 'Z', 'W'],
    tasks: { todo: 4, in_progress: 4, done: 2 }
  },
  {
    id: 'p2',
    name: '小红书 AI 产品经理博主',
    desc: '「学 AI → 造工具 → 发小红书」内容输出计划。双栏目：费曼漫画讲 AI + Vibecoding 大字报，Hermes Agent 6人协同流水线。',
    progress: 30,
    color: '#059669',
    members: ['L', 'Q', 'Y', 'G'],
    tasks: { todo: 5, in_progress: 4, done: 2 }
  },
];

let TASKS = [
  // ===== 穗穗念 (p1) =====
  { id: 't1',  pid: 'p1', title: 'F-01 微信登录 — 微信一键授权登录',          status: 'done',        priority: 'high',   assignee: 'Z', due: '06-15', desc: '已完成微信登录授权流程，基础库 ≥2.24.0 兼容验证通过' },
  { id: 't2',  pid: 'p1', title: 'F-02 云同步 — 微信云开发数据同步',            status: 'done',        priority: 'high',   assignee: 'Z', due: '06-20', desc: '云数据库 + 云存储方案已落地，测试环境通过' },
  { id: 't3',  pid: 'p1', title: 'F-03 我的主页 — 个人追星主页设计与开发',     status: 'in_progress', priority: 'high',   assignee: 'L', due: '06-28', desc: '个人主页含：统计卡片、物料展示、隐私开关入口（P0）' },
  { id: 't4',  pid: 'p1', title: 'F-04 物料记录 — 物料/周边记录核心功能',       status: 'in_progress', priority: 'high',   assignee: 'W', due: '07-02', desc: '图片上传 + 分类标签 + 购买信息录入（P0）' },
  { id: 't5',  pid: 'p1', title: 'F-09 艺人库 — 艺人信息库（含 isOshi 标记）', status: 'in_progress', priority: 'high',   assignee: 'Z', due: '07-05', desc: '艺人信息库 + user_artists 关联表（P0）' },
  { id: 't6',  pid: 'p1', title: 'F-05 周边管理 — 周边物品管理功能',            status: 'todo',        priority: 'high',   assignee: 'W', due: '07-10', desc: '展示柜（柜子）管理 + 物品增删改（P0）' },
  { id: 't7',  pid: 'p1', title: 'F-08 物品隐私设置 — 隐私控制开关',            status: 'todo',        priority: 'medium', assignee: 'L', due: '07-12', desc: '公开/私密两级权限，不设「仅好友可见」（P0）' },
  { id: 't8',  pid: 'p1', title: 'F-14 账号注销 — 微信账号注销流程',            status: 'todo',        priority: 'medium', assignee: 'Z', due: '07-15', desc: '注销申请 → 确认 → 数据清理全流程（P0）' },
  { id: 't9',  pid: 'p1', title: 'F-06 花销统计 — 追星花销统计（v1.1）',       status: 'in_progress', priority: 'low',    assignee: 'W', due: '08-01', desc: '月度/年度花销统计 + 分类汇总（P1）' },
  { id: 't10', pid: 'p1', title: 'F-07 个人展示柜 — 演唱会票根/周边展示（v1.1）', status: 'todo',       priority: 'low',    assignee: 'L', due: '08-10', desc: '演唱会记录 + 展示柜自定义排序（P1）' },

  // ===== 小红书博主 (p2) =====
  { id: 't11', pid: 'p2', title: '栏目一选题规划 — 费曼漫画讲 AI 全14个选题排期', status: 'done',       priority: 'high',   assignee: 'Q', due: '06-18', desc: 'P0/P1/P2/P3 四级选题池已定义，动态调整原则已对齐' },
  { id: 't12', pid: 'p2', title: '栏目二框架 — Vibecoding 大字报 10个方向',      status: 'done',        priority: 'high',   assignee: 'Q', due: '06-20', desc: 'Vibecoding 大字报框架 + 工具展示模板' },
  { id: 't13', pid: 'p2', title: '漫画：Agent = 大脑+手+工具 — 三格漫画拆解AI Agent', status: 'in_progress', priority: 'high', assignee: 'Q', due: '06-30', desc: '关联 Hermes Agent 架构 + Agent 协作流程图' },
  { id: 't14', pid: 'p2', title: '工具：Prompt 模板管理 CLI 初版',                status: 'in_progress', priority: 'high',   assignee: 'G', due: '07-02', desc: 'Prompt 模板 CRUD + 分类管理 CLI 工具（栏目二素材）' },
  { id: 't15', pid: 'p2', title: '漫画：RAG 检索增强生成 = 考试开卷教材',          status: 'in_progress', priority: 'medium', assignee: 'Q', due: '07-05', desc: '关联 RAG 学习路径 + 知识库助手工具展示' },
  { id: 't16', pid: 'p2', title: '工具：个人知识库助手 CLI',                       status: 'todo',        priority: 'low',    assignee: 'G', due: '07-15', desc: 'RAG 实践工具 — 从本地文档构建知识库并查询' },
  { id: 't17', pid: 'p2', title: '漫画：Prompt 不是咒语，是外卖备注',              status: 'in_progress', priority: 'medium', assignee: 'Q', due: '07-08', desc: 'Prompt Engineering 入门漫画 + CLI 工具截图' },
  { id: 't18', pid: 'p2', title: '大字报：第一期 — Vibecoding 入门指南',          status: 'todo',        priority: 'medium', assignee: 'Y', due: '07-10', desc: '大字报格式：纯色底 + 大字 + 量化数据/时间线' },
  { id: 't19', pid: 'p2', title: '发布流程自动化 — Hermes cron + 检查清单',        status: 'todo',        priority: 'medium', assignee: 'L', due: '07-08', desc: 'Cron 定时提醒 + 发布前检查流程 + 双签放行机制' },
  { id: 't20', pid: 'p2', title: '漫画：大模型到底是个啥 — 图书馆管理员比喻',       status: 'todo',        priority: 'medium', assignee: 'Q', due: '07-12', desc: 'LLM 基础入门漫画 + llama.cpp 终端截图' },
];

let COMMENTS = [
  // 穗穗念评论
  { id: 'c1', taskId: 't3', author: 'Z', time: '06-26 10:30', text: '我的主页统计卡片需要对接云数据库聚合查询，API 已经在写了' },
  { id: 'c2', taskId: 't3', author: 'L', time: '06-26 11:15', text: '隐私开关和主页联调注意：默认所有数据为私密状态' },
  { id: 'c3', taskId: 't4', author: 'W', time: '06-27 09:00', text: '物料记录上传图片用的云存储，需要确认免费额度够不够' },
  { id: 'c4', taskId: 't4', author: 'Z', time: '06-27 09:45', text: '云开发免费额度每个月 5GB 存储 + 500MB 流量，初期够用' },
  { id: 'c5', taskId: 't5', author: 'L', time: '06-25 16:20', text: '艺人库的 isOshi 字段关联表 PRD v1.2 重新设计过，先看文档再开发' },

  // 小红书博主评论
  { id: 'c6', taskId: 't13', author: 'G', time: '06-28 14:00', text: '漫画分镜我看了，Agent 流程图部分可以和实际 Hermes 架构截图对比，效果更好' },
  { id: 'c7', taskId: 't13', author: 'Q', time: '06-28 15:30', text: '好的，我把三个 Agent profile 的协作流程截图加上' },
  { id: 'c8', taskId: 't14', author: 'L', time: '06-27 20:00', text: 'Prompt 模板 CLI 考虑加个 --export 参数导出为 Notion/json，方便后续发布用' },
  { id: 'c9', taskId: 't14', author: 'G', time: '06-27 22:10', text: '好思路，可以在 CLI 里加 markdown export，直接贴小红书' },
  { id: 'c10', taskId: 't17', author: 'Y', time: '06-29 10:00', text: '这篇漫画可以和 t14 CLI 工具联动发布，同一天推漫画+工具使用展示' },
];

// ===================== localStorage 持久化 =====================

function getNextId(prefix, arr) {
  let max = 0;
  arr.forEach(item => {
    if (item.id.startsWith(prefix)) {
      const num = parseInt(item.id.slice(prefix.length));
      if (num > max) max = num;
    }
  });
  return prefix + (max + 1);
}

function saveData() {
  localStorage.setItem('qingtian_projects', JSON.stringify(PROJECTS));
  localStorage.setItem('qingtian_tasks', JSON.stringify(TASKS));
  localStorage.setItem('qingtian_comments', JSON.stringify(COMMENTS));
}

function loadData() {
  const savedProjects = localStorage.getItem('qingtian_projects');
  const savedTasks = localStorage.getItem('qingtian_tasks');
  const savedComments = localStorage.getItem('qingtian_comments');
  if (savedProjects) PROJECTS = JSON.parse(savedProjects);
  if (savedTasks) TASKS = JSON.parse(savedTasks);
  if (savedComments) COMMENTS = JSON.parse(savedComments);
}

function resetData() {
  // 从数据源重新初始化
  localStorage.removeItem('qingtian_projects');
  localStorage.removeItem('qingtian_tasks');
  localStorage.removeItem('qingtian_comments');
  window.location.reload();
}

// 首次加载：如果没有 localStorage 数据，把默认数据写入
(function initData() {
  if (!localStorage.getItem('qingtian_projects')) {
    saveData();
  } else {
    loadData();
  }
})();

// ===================== Toast 通知 =====================

function showToast(message, type) {
  type = type || 'success';
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed; top: 20px; right: 20px; z-index: 9999;
    padding: 12px 20px; border-radius: 8px; font-size: 14px; font-weight: 500;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    color: #fff; max-width: 360px;
    transform: translateX(120%); transition: transform 0.3s ease;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  `;
  const colors = {
    success: '#059669', error: '#DC2626', warning: '#D97706', info: '#4F46E5'
  };
  toast.style.background = colors[type] || colors.info;
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; });
  setTimeout(() => {
    toast.style.transform = 'translateX(120%)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===================== 确认弹窗 =====================

function showConfirm(message, onConfirm, onCancel) {
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 10000;
    display: flex; align-items: center; justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  `;
  overlay.innerHTML = `
    <div style="background:#fff;border-radius:12px;padding:24px;width:380px;box-shadow:0 20px 60px rgba(0,0,0,0.2);">
      <p style="font-size:15px;color:#374151;margin-bottom:20px;line-height:1.5;">${message}</p>
      <div style="display:flex;gap:8px;justify-content:flex-end;">
        <button class="confirm-cancel-btn" style="padding:8px 16px;border-radius:8px;border:1px solid #D1D5DB;background:#fff;color:#374151;font-size:14px;cursor:pointer;font-family:inherit;">取消</button>
        <button class="confirm-ok-btn" style="padding:8px 16px;border-radius:8px;border:none;background:#DC2626;color:#fff;font-size:14px;cursor:pointer;font-family:inherit;">确认</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.querySelector('.confirm-cancel-btn').onclick = function() {
    overlay.remove();
    if (onCancel) onCancel();
  };
  overlay.querySelector('.confirm-ok-btn').onclick = function() {
    overlay.remove();
    if (onConfirm) onConfirm();
  };
  overlay.addEventListener('click', function(e) {
    if (e.target === this) { overlay.remove(); if (onCancel) onCancel(); }
  });
}

// ===================== CRUD: 任务 =====================

function createTask(pid, title, priority, assignee, due, desc) {
  const id = getNextId('t', TASKS);
  const newTask = {
    id: id,
    pid: pid,
    title: title,
    status: 'todo',
    priority: priority || 'medium',
    assignee: assignee || '?',
    due: due || '',
    desc: desc || ''
  };
  TASKS.push(newTask);
  // 更新项目的 tasks 计数
  recalcProjectTaskCounts(pid);
  saveData();
  showToast('任务已创建');
  return newTask;
}

function updateTask(taskId, updates) {
  const task = TASKS.find(t => t.id === taskId);
  if (!task) { showToast('任务未找到', 'error'); return null; }
  const oldPid = task.pid;
  Object.assign(task, updates);
  // 如果项目变了，重新计算两个项目的计数
  recalcProjectTaskCounts(task.pid);
  if (task.pid !== oldPid) recalcProjectTaskCounts(oldPid);
  saveData();
  showToast('任务已更新');
  return task;
}

function deleteTask(taskId) {
  const idx = TASKS.findIndex(t => t.id === taskId);
  if (idx === -1) { showToast('任务未找到', 'error'); return; }
  const task = TASKS[idx];
  // 删除关联评论
  COMMENTS = COMMENTS.filter(c => c.taskId !== taskId);
  TASKS.splice(idx, 1);
  recalcProjectTaskCounts(task.pid);
  saveData();
  showToast('任务已删除', 'warning');
}

function cycleStatus(taskId) {
  const task = TASKS.find(t => t.id === taskId);
  if (!task) { showToast('任务未找到', 'error'); return null; }
  const order = ['todo', 'in_progress', 'done'];
  const currentIdx = order.indexOf(task.status);
  const nextStatus = order[(currentIdx + 1) % order.length];
  task.status = nextStatus;
  recalcProjectTaskCounts(task.pid);
  saveData();
  const statusMap = { todo: '📋 待办', in_progress: '🔄 进行中', done: '✅ 已完成' };
  showToast(`状态已切换为 ${statusMap[nextStatus]}`);
  return task;
}

// ===================== CRUD: 项目 =====================

function createProject(name, desc, color) {
  const id = getNextId('p', PROJECTS);
  const newProject = {
    id: id,
    name: name,
    desc: desc || '',
    progress: 0,
    color: color || '#4F46E5',
    members: [],
    tasks: { todo: 0, in_progress: 0, done: 0 }
  };
  PROJECTS.push(newProject);
  saveData();
  showToast('项目已创建');
  return newProject;
}

function updateProject(projectId, updates) {
  const proj = PROJECTS.find(p => p.id === projectId);
  if (!proj) { showToast('项目未找到', 'error'); return null; }
  Object.assign(proj, updates);
  saveData();
  showToast('项目已更新');
  return proj;
}

function deleteProject(projectId) {
  const idx = PROJECTS.findIndex(p => p.id === projectId);
  if (idx === -1) { showToast('项目未找到', 'error'); return; }
  // 删除该项目所有任务和评论
  const tasksToDelete = TASKS.filter(t => t.pid === projectId);
  tasksToDelete.forEach(t => {
    COMMENTS = COMMENTS.filter(c => c.taskId !== t.id);
  });
  TASKS = TASKS.filter(t => t.pid !== projectId);
  PROJECTS.splice(idx, 1);
  saveData();
  showToast('项目已删除', 'warning');
}

// ===================== CRUD: 评论 =====================

function addComment(taskId, author, text) {
  if (!text.trim()) { showToast('请输入评论内容', 'warning'); return null; }
  const id = getNextId('c', COMMENTS);
  const now = new Date();
  const timeStr = (now.getMonth()+1).toString().padStart(2,'0') + '-' +
                  now.getDate().toString().padStart(2,'0') + ' ' +
                  now.getHours().toString().padStart(2,'0') + ':' +
                  now.getMinutes().toString().padStart(2,'0');
  const newComment = { id, taskId, author, time: timeStr, text: text.trim() };
  COMMENTS.push(newComment);
  saveData();
  showToast('评论已添加');
  return newComment;
}

function deleteComment(commentId) {
  const idx = COMMENTS.findIndex(c => c.id === commentId);
  if (idx === -1) return;
  COMMENTS.splice(idx, 1);
  saveData();
  showToast('评论已删除', 'warning');
}

// ===================== 项目任务计数 & 进度 =====================

function recalcProjectTaskCounts(projectId) {
  const projectTasks = TASKS.filter(t => t.pid === projectId);
  const todo = projectTasks.filter(t => t.status === 'todo').length;
  const in_progress = projectTasks.filter(t => t.status === 'in_progress').length;
  const done = projectTasks.filter(t => t.status === 'done').length;
  const total = todo + in_progress + done;
  const proj = PROJECTS.find(p => p.id === projectId);
  if (proj) {
    proj.tasks = { todo, in_progress, done };
    proj.progress = total > 0 ? Math.round((done / total) * 100) : 0;
  }
}

function recalcAllProjects() {
  PROJECTS.forEach(p => recalcProjectTaskCounts(p.id));
  saveData();
}

// ===================== 搜索 & 过滤 =====================

function filterTasks(options) {
  let results = [...TASKS];
  const { pid, status, priority, assignee, keyword, dueBefore } = options || {};

  if (pid) results = results.filter(t => t.pid === pid);
  if (status) results = results.filter(t => t.status === status);
  if (priority) results = results.filter(t => t.priority === priority);
  if (assignee) results = results.filter(t => t.assignee === assignee);
  if (keyword) {
    const kw = keyword.toLowerCase();
    results = results.filter(t =>
      t.title.toLowerCase().includes(kw) ||
      (t.desc && t.desc.toLowerCase().includes(kw))
    );
  }
  if (dueBefore) {
    results = results.filter(t => t.due && t.due <= dueBefore);
  }
  return results;
}

function searchProjects(keyword) {
  if (!keyword) return [...PROJECTS];
  const kw = keyword.toLowerCase();
  return PROJECTS.filter(p =>
    p.name.toLowerCase().includes(kw) ||
    p.desc.toLowerCase().includes(kw)
  );
}

// ===================== 登录 =====================

function requireLogin() {
  if (!localStorage.getItem('qingtian_user')) {
    window.location.href = 'login.html';
    return null;
  }
  return JSON.parse(localStorage.getItem('qingtian_user'));
}

function logout() {
  localStorage.removeItem('qingtian_user');
  window.location.href = 'login.html';
}

// ===================== 工具函数 =====================

function getTodayStr() {
  const now = new Date();
  return now.getFullYear() + ' 年 ' + (now.getMonth()+1) + ' 月 ' + now.getDate() + ' 日';
}

function priorityLabel(p) {
  return p === 'high' ? '高' : p === 'medium' ? '中' : '低';
}

function statusLabel(s) {
  const map = { todo: '📋 待办', in_progress: '🔄 进行中', done: '✅ 已完成' };
  return map[s] || s;
}
