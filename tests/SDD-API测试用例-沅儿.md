# 晴天项目看板后端 — API 测试用例

> **作者**: 沅儿  
> **版本**: v1.0  
> **日期**: 2026-07-01  
> **基础路径**: `http://localhost:8000`  
> **认证方式**: Bearer Token（JWT，有效期 7 天）

---

## 目录

1. [认证模块](#1-认证模块-api-auth)
2. [项目模块](#2-项目模块-api-projects)
3. [任务模块](#3-任务模块-api-tasks)
4. [评论模块](#4-评论模块-api-comments)
5. [统计模块](#5-统计模块-api-dashboard)
6. [健康检查](#6-健康检查-api-health)

---

## 1. 认证模块 (`/api/auth`)

### 1.1. POST `/api/auth/register` — 注册

#### TC-AUTH-REG-001 ✅ 正常注册
| 字段 | 值 |
|---|---|
| email | `test@example.com` |
| name | `测试用户` |
| password | `123456` |

**预期结果**:  
- 状态码: `201`
- 返回 `access_token` (JWT)、`token_type: "bearer"`、`user` 对象
- `user` 包含: `id`, `email`, `name="测试用户"`, `role="member"`, `avatar="测"`, `is_active=1`, `created_at`
- 数据库 `users` 表中新增一条记录
- 密码被 bcrypt 哈希存储

**校验点**:
```json
{
  "access_token": "<jwt_string>",
  "token_type": "bearer",
  "user": {
    "id": "<16_char_id>",
    "email": "test@example.com",
    "name": "测试用户",
    "role": "member",
    "avatar": "测",
    "is_active": 1,
    "created_at": "<datetime>"
  }
}
```

---

#### TC-AUTH-REG-002 ❌ 重复注册
| 步骤 | 操作 |
|---|---|
| 1 | 用 `test@example.com` 注册成功 |
| 2 | 再次用相同 email 注册 |

**预期结果**:
- 状态码: `400`
- 响应体: `{"detail": "该邮箱已被注册"}`
- 数据库不产生新记录

---

#### TC-AUTH-REG-003 ❌ 密码长度不足
| 字段 | 值 |
|---|---|
| email | `shortpw@test.com` |
| name | `短密码` |
| password | `12345` (5 位) |

**预期结果**:
- 状态码: `422` (Pydantic 校验失败)
- 响应体包含 `password` 字段的验证错误，提示至少 6 位

---

#### TC-AUTH-REG-004 ❌ 邮箱超长
| 字段 | 值 |
|---|---|
| email | `a` × 256 + `@test.com` |
| name | `超长邮箱` |
| password | `123456` |

**预期结果**:
- 状态码: `422`
- Pydantic 校验拒绝超过 255 字符的 `email`

---

#### TC-AUTH-REG-005 ❌ 空字段
| 场景 | 操作 |
|---|---|
| 缺少 email | 不传 email 字段 |
| email 为空字符串 | `email: ""` |
| name 为空 | `name: ""` |

**预期结果**: 状态码 `422`，Pydantic 校验失败

---

### 1.2. POST `/api/auth/login` — 登录

#### TC-AUTH-LOGIN-001 ✅ 正常登录
**前提**: 用户 `test@example.com` 已注册，密码 `123456`

**请求**: `POST /api/auth/login` 携带 `{"email": "test@example.com", "password": "123456"}`

**预期结果**:
- 状态码: `200`
- 返回 `access_token` + `user` 对象
- `user.email === "test@example.com"`
- `user.name === "测试用户"`

---

#### TC-AUTH-LOGIN-002 ❌ 密码错误
**前提**: 用户 `test@example.com` 已注册

**请求**: `{"email": "test@example.com", "password": "wrongpass"}`

**预期结果**:
- 状态码: `401`
- 响应体: `{"detail": "邮箱或密码错误"}`

---

#### TC-AUTH-LOGIN-003 ❌ 未注册邮箱
**请求**: `{"email": "nobody@example.com", "password": "123456"}`

**预期结果**:
- 状态码: `401`
- 响应体: `{"detail": "邮箱或密码错误"}`
- ⚠️ 与密码错误返回相同消息，不泄漏邮箱是否存在

---

#### TC-AUTH-LOGIN-004 ❌ 空密码
**请求**: `{"email": "test@example.com", "password": ""}`

**预期结果**:
- 状态码: `422` (未触发 min_length 校验) 或 `401` (服务端验证)
- 至少不返回 token

---

### 1.3. GET `/api/auth/me` — 获取当前用户

#### TC-AUTH-ME-001 ✅ 有效 Token 获取用户信息
**请求头**: `Authorization: Bearer <valid_token>`

**预期结果**:
- 状态码: `200`
- 返回 `UserOut` 对象，字段与注册响应一致

---

#### TC-AUTH-ME-002 ❌ 无 Token
**请求**: 不传 `Authorization` 头

**预期结果**:
- 状态码: `403` (HTTPBearer auto-error)

---

#### TC-AUTH-ME-003 ❌ 无效 Token
**请求头**: `Authorization: Bearer invalid.jwt.token`

**预期结果**:
- 状态码: `401`
- 响应体: `{"detail": "无效的认证凭证"}`

---

#### TC-AUTH-ME-004 ❌ 过期 Token
| 操作 |
|---|
| 用过期 Token 请求 `/api/auth/me` |

**预期结果**:
- 状态码: `401`
- 响应体: `{"detail": "无效的认证凭证"}`

---

#### TC-AUTH-ME-005 ❌ 已禁用用户
**前提**: 用户被设置 `is_active=0`

**请求头**: `Authorization: Bearer <该用户的token>`

**预期结果**:
- 状态码: `401`
- 响应体: `{"detail": "用户不存在或已禁用"}`

---

## 2. 项目模块 (`/api/projects`)

### 2.1. GET `/api/projects` — 项目列表

#### TC-PROJ-LIST-001 ✅ 获取全部活跃项目
**前提**: 数据库中有 3 个 `is_active=1` 的项目

**预期结果**:
- 状态码: `200`
- 返回数组，长度 ≥ 3
- 每个元素包含 `id`, `name`, `description`, `color`, `progress`, `creator_id`, `is_active`, `created_at`, `updated_at`, `creator`, `task_count`, `member_count`
- 按 `updated_at` 降序排列

---

#### TC-PROJ-LIST-002 ✅ 关键字搜索
**请求**: `GET /api/projects?keyword=晴天`

**预期结果**:
- 状态码: `200`
- 仅返回名称包含 "晴天" 的项目
- 空结果时返回空数组 `[]`

---

#### TC-PROJ-LIST-003 ✅ 空结果搜索
**请求**: `GET /api/projects?keyword=ZZZZNOTEXIST`

**预期结果**:
- 状态码: `200`
- 返回 `[]`

---

#### TC-PROJ-LIST-004 ❌ 未认证
**请求**: 不传 Token

**预期结果**: 状态码 `403`

---

### 2.2. POST `/api/projects` — 创建项目

#### TC-PROJ-CREATE-001 ✅ 正常创建
**请求**:
```json
{
  "name": "晴天项目",
  "description": "Hermes 6 Agent 协作看板系统",
  "color": "#4F46E5"
}
```

**预期结果**:
- 状态码: `201`
- 返回 `ProjectOut` 对象
- `name === "晴天项目"`, `color === "#4F46E5"`
- `creator_id === 当前用户.id`
- `is_active === 1`, `progress === 0`
- `task_count === 0`, `member_count === 1`
- 数据库中 `projects` 表新增记录
- 数据库中 `project_members` 表新增一条 `role="owner"` 的记录

---

#### TC-PROJ-CREATE-002 ✅ 只传必填字段
**请求**: `{"name": "最小项目"}`

**预期结果**:
- 状态码: `201`
- `description` 默认空字符串 ""
- `color` 默认为 `"#4F46E5"`

---

#### TC-PROJ-CREATE-003 ❌ 名称超长
**请求**: `{"name": "a" × 201}`

**预期结果**:
- 状态码: `422`
- Pydantic 校验拒绝

---

#### TC-PROJ-CREATE-004 ❌ 名称为空
**请求**: `{"name": ""}`

**预期结果**:
- 状态码: `422` (string 类型需要至少含内容 - Pydantic 校验)

---

### 2.3. GET `/api/projects/{project_id}` — 项目详情

#### TC-PROJ-GET-001 ✅ 获取已存在项目
**前提**: 项目 ID 存在

**预期结果**:
- 状态码: `200`
- 返回 `ProjectOut`，`id` 匹配路径参数
- `creator` 对象包含 `id`, `name`, `avatar`, `role`

---

#### TC-PROJ-GET-002 ❌ 项目不存在
**请求**: `GET /api/projects/nonexistent123`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "项目不存在"}`

---

#### TC-PROJ-GET-003 ❌ 已软删除项目
**前提**: 项目 `is_active=0`

**请求**: `GET /api/projects/{deleted_project_id}`

**预期结果**:
- 状态码: `404`（按 ID 查不到 filter 中被排除，但当前实现用直接查询，所以仍能找到）
- ⚠️ **注意**: 当前实现未按 `is_active` 过滤 GET 详情，能查到已软删除项目。这是一个**潜在问题**，建议修复。

---

### 2.4. PUT `/api/projects/{project_id}` — 更新项目

#### TC-PROJ-UPDATE-001 ✅ 更新名称和描述
**请求**: `{"name": "新名称", "description": "新描述"}`

**预期结果**:
- 状态码: `200`
- `name` 变为 "新名称"，`description` 变为 "新描述"
- `updated_at` 更新

---

#### TC-PROJ-UPDATE-002 ✅ 部分更新颜色
**请求**: `{"color": "#FF0000"}`

**预期结果**:
- 状态码: `200`
- 仅 `color` 改变，其它字段不变

---

#### TC-PROJ-UPDATE-003 ✅ 软删除项目
**请求**: `{"is_active": 0}`

**预期结果**:
- 状态码: `200`
- `is_active` 变为 0
- 项目不再出现在 GET 列表结果中

---

#### TC-PROJ-UPDATE-004 ❌ 项目不存在
**请求**: `PUT /api/projects/nonexistent123`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "项目不存在"}`

---

### 2.5. DELETE `/api/projects/{project_id}` — 删除项目

#### TC-PROJ-DEL-001 ✅ 正常删除（级联）
**前提**: 项目下有 3 个任务，每个任务有若干评论

**预期结果**:
- 状态码: `200`
- 响应体: `{"message": "项目已删除"}`
- 数据库中项目记录被删除
- 关联的任务、评论、成员记录被级联删除（CASCADE）

---

#### TC-PROJ-DEL-002 ❌ 项目不存在
**请求**: `DELETE /api/projects/nonexistent123`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "项目不存在"}`

---

## 3. 任务模块 (`/api/tasks`, `/api/projects/{pid}/tasks`)

### 3.1. GET `/api/tasks/my` — 我的任务

#### TC-TASK-MY-001 ✅ 获取当前用户待办任务
**前提**: 当前用户被分配了任务，状态为 `todo`、`in_progress`、`done`

**预期结果**:
- 状态码: `200`
- 返回任务数组，仅 `assignee_id === 当前用户.id`
- 默认最多 50 条
- 按 `updated_at` 降序

---

#### TC-TASK-MY-002 ✅ 按状态过滤（未完成）
**请求**: `GET /api/tasks/my?status=todo`

**预期结果**:
- 返回 `status = "todo"` 或 `"in_progress"` 的任务（todo 过滤器的约定）

---

#### TC-TASK-MY-003 ✅ 按状态过滤（已完成）
**请求**: `GET /api/tasks/my?status=done`

**预期结果**:
- 仅返回 `status = "done"` 的任务

---

#### TC-TASK-MY-004 ✅ 限制条数
**请求**: `GET /api/tasks/my?limit=2`

**预期结果**:
- 最多返回 2 条结果

---

#### TC-TASK-MY-005 ✅ 无任务时
**前提**: 当前用户没有分配任何任务

**预期结果**:
- 状态码: `200`
- 返回 `[]`

---

### 3.2. GET `/api/projects/{pid}/tasks` — 按项目列出任务

#### TC-TASK-LIST-001 ✅ 获取项目下所有任务
**前提**: 项目有 5 个任务

**预期结果**:
- 状态码: `200`
- 返回数组，长度 = 5
- 按 `created_at` 降序

---

#### TC-TASK-LIST-002 ✅ 按状态过滤
**请求**: `GET /api/projects/{pid}/tasks?status=todo`

**预期结果**:
- 仅返回 `status === "todo"` 的任务

---

#### TC-TASK-LIST-003 ✅ 按优先级过滤
**请求**: `GET /api/projects/{pid}/tasks?priority=high`

**预期结果**:
- 仅返回 `priority === "high"` 的任务

---

#### TC-TASK-LIST-004 ✅ 按负责人过滤
**请求**: `GET /api/projects/{pid}/tasks?assignee_id={user_id}`

**预期结果**:
- 仅返回 `assignee_id` 匹配的任务

---

#### TC-TASK-LIST-005 ✅ 复合过滤
**请求**: `GET /api/projects/{pid}/tasks?status=in_progress&priority=high`

**预期结果**:
- 同时满足两个条件的任务

---

#### TC-TASK-LIST-006 ❌ 项目不存在
**请求**: `GET /api/projects/nonexistent/tasks`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "项目不存在"}`

---

### 3.3. POST `/api/projects/{pid}/tasks` — 创建任务

#### TC-TASK-CREATE-001 ✅ 正常创建（仅必填）
**请求**:
```json
{
  "title": "实现登录功能"
}
```

**预期结果**:
- 状态码: `201`
- 返回 `TaskOut`，包含 `id`, `pid`, `title`, `status="todo"`, `priority="medium"`, `assignee_id=null`, `due_date=""`, `description=""`, `feishu_msg_id=""`, `source="manual"`, `created_at`, `updated_at`
- 项目进度自动更新

---

#### TC-TASK-CREATE-002 ✅ 创建任务（全字段）
**请求**:
```json
{
  "title": "实现登录功能",
  "status": "in_progress",
  "priority": "high",
  "assignee_id": "<existing_user_id>",
  "due_date": "07-15",
  "description": "用户邮箱密码登录",
  "source": "manual"
}
```

**预期结果**:
- 状态码: `201`
- 所有字段按请求设置

---

#### TC-TASK-CREATE-003 ❌ 负责人不存在
**请求**: `{"title": "任务", "assignee_id": "nonexistent_user"}`

**预期结果**:
- 状态码: `400`
- 响应体: `{"detail": "负责人不存在"}`

---

#### TC-TASK-CREATE-004 ❌ 项目不存在
**请求**: `POST /api/projects/nonexistent/tasks`

**预期结果**:
- 状态码: `404`

---

#### TC-TASK-CREATE-005 ❌ 标题超长
**请求**: `{"title": "x" × 501}`

**预期结果**:
- 状态码: `422`

---

#### TC-TASK-CREATE-006 ❌ 状态值无效
**请求**: `{"title": "任务", "status": "cancelled"}`

**预期结果**:
- 状态码: `422`（Pydantic / DB CheckConstraint）

---

### 3.4. GET `/api/tasks/{task_id}` — 任务详情

#### TC-TASK-GET-001 ✅ 获取已存在任务
**前提**: 任务已创建

**预期结果**:
- 状态码: `200`
- 返回 `TaskOut`，`assignee` 字段非空时有嵌套 `UserBrief`

---

#### TC-TASK-GET-002 ❌ 任务不存在
**请求**: `GET /api/tasks/nonexistent`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "任务不存在"}`

---

### 3.5. PUT `/api/tasks/{task_id}` — 更新任务

#### TC-TASK-UPDATE-001 ✅ 更新标题和描述
**请求**: `{"title": "新标题", "description": "新的描述内容"}`

**预期结果**:
- 状态码: `200`
- `title`, `description` 被更新，其它字段不变
- 项目进度重新计算

---

#### TC-TASK-UPDATE-002 ✅ 重新分配负责人
**请求**: `{"assignee_id": "<another_user_id>"}`

**预期结果**:
- `assignee_id` 更新为新的用户 ID
- `assignee` 嵌套对象更新为新用户信息

---

#### TC-TASK-UPDATE-003 ✅ 清除负责人
**请求**: `{"assignee_id": ""}`

**预期结果**:
- `assignee_id` 变为 `""`（当前实现会将空字符串设进去）
- ⚠️ 注意: 当前代码 `if data.assignee_id:` 是 `""` 为 False 时走 else 分支 `task.assignee_id = data.assignee_id`。代码逻辑: `if data.assignee_id:` 为 False 时，`task.assignee_id = ""`。但实际上因为 `if data.assignee_id is not None:` 在外部，所以 `""` 被当作非 None 传入，内部 `if data.assignee_id:` 为 False → 走 `else` 分支 `task.assignee_id = data.assignee_id` → 设为 `""`。这是正确的清除行为。

---

#### TC-TASK-UPDATE-004 ❌ 负责人不存在
**请求**: `{"assignee_id": "ghost_user"}`

**预期结果**:
- 状态码: `400`
- 响应体: `{"detail": "负责人不存在"}`

---

#### TC-TASK-UPDATE-005 ❌ 任务不存在
**请求**: `PUT /api/tasks/nonexistent`

**预期结果**:
- 状态码: `404`

---

### 3.6. DELETE `/api/tasks/{task_id}` — 删除任务

#### TC-TASK-DEL-001 ✅ 正常删除（级联评论）
**前提**: 任务下有 2 条评论

**预期结果**:
- 状态码: `200`
- 响应体: `{"message": "任务已删除"}`
- 任务被删除
- 关联评论被级联删除
- 项目进度重新计算

---

#### TC-TASK-DEL-002 ❌ 任务不存在
**请求**: `DELETE /api/tasks/nonexistent`

**预期结果**:
- 状态码: `404`

---

### 3.7. PATCH `/api/tasks/{task_id}/status` — 切换状态

#### TC-TASK-STATUS-001 ✅ todo → in_progress
**前提**: 任务当前状态 `todo`

**请求**: `{"status": "in_progress"}`

**预期结果**:
- 状态码: `200`
- `status` 变为 `"in_progress"`
- 项目进度重新计算

---

#### TC-TASK-STATUS-002 ✅ in_progress → done
**前提**: 任务当前状态 `in_progress`

**请求**: `{"status": "done"}`

**预期结果**:
- `status` 变为 `"done"`
- 项目进度增加

---

#### TC-TASK-STATUS-003 ✅ done → todo（回退）
**请求**: `{"status": "todo"}`

**预期结果**:
- `status` 变为 `"todo"`
- 项目进度减少

---

#### TC-TASK-STATUS-004 ❌ 无效状态值
**请求**: `{"status": "cancelled"}`

**预期结果**:
- 状态码: `422`（Pydantic regex 拒绝）

---

#### TC-TASK-STATUS-005 ❌ 任务不存在
**请求**: `PATCH /api/tasks/nonexistent/status`

**预期结果**:
- 状态码: `404`

---

## 4. 评论模块 (`/api/comments`, `/api/tasks/{task_id}/comments`)

### 4.1. GET `/api/tasks/{task_id}/comments` — 评论列表

#### TC-COMM-LIST-001 ✅ 获取任务评论
**前提**: 任务下有 3 条评论

**预期结果**:
- 状态码: `200`
- 返回数组，长度 = 3
- 每条评论包含 `id`, `task_id`, `author_id`, `text`, `created_at`, `author`
- 按 `created_at` 升序排列

---

#### TC-COMM-LIST-002 ✅ 无评论的任务
**前提**: 任务无评论

**预期结果**:
- 状态码: `200`
- 返回 `[]`

---

#### TC-COMM-LIST-003 ❌ 任务不存在
**请求**: `GET /api/tasks/nonexistent/comments`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "任务不存在"}`

---

### 4.2. POST `/api/tasks/{task_id}/comments` — 添加评论

#### TC-COMM-CREATE-001 ✅ 正常添加
**请求**: `{"text": "这是一个评论"}`

**预期结果**:
- 状态码: `201`
- 返回 `CommentOut`，包含 `id`, `task_id`, `author_id`, `text="这是一个评论"`, `created_at`
- `author` 为当前用户的 `UserBrief`

---

#### TC-COMM-CREATE-002 ❌ 空内容
**请求**: `{"text": ""}`

**预期结果**:
- 状态码: `422`（Pydantic min_length=1）

---

#### TC-COMM-CREATE-003 ❌ 任务不存在
**请求**: `POST /api/tasks/nonexistent/comments`

**预期结果**:
- 状态码: `404`

---

### 4.3. DELETE `/api/comments/{comment_id}` — 删除评论

#### TC-COMM-DEL-001 ✅ 删除自己的评论
**前提**: 当前用户是评论的作者

**预期结果**:
- 状态码: `200`
- 响应体: `{"message": "评论已删除"}`
- 数据库中评论记录被删除

---

#### TC-COMM-DEL-002 ❌ 删除他人的评论
**前提**: 当前用户不是评论的作者

**预期结果**:
- 状态码: `403`
- 响应体: `{"detail": "只能删除自己的评论"}`

---

#### TC-COMM-DEL-003 ❌ 评论不存在
**请求**: `DELETE /api/comments/nonexistent`

**预期结果**:
- 状态码: `404`
- 响应体: `{"detail": "评论不存在"}`

---

## 5. 统计模块 (`/api/dashboard`)

### 5.1. GET `/api/dashboard/stats` — 仪表盘统计

#### TC-STATS-001 ✅ 数据正确性
**前提**: 已知数据库状态：
- 活跃项目: 5 个
- 总任务: 20 个（todo: 10, in_progress: 5, done: 5）
- 活跃用户: 8 个

**预期结果**:
```json
{
  "total_projects": 5,
  "active_projects": 5,
  "total_tasks": 20,
  "todo_tasks": 10,
  "in_progress_tasks": 5,
  "done_tasks": 5,
  "total_users": 8
}
```

---

#### TC-STATS-002 ✅ 空数据库
**前提**: 数据库无数据

**预期结果**:
- 所有字段返回 0
- 不会报错

---

#### TC-STATS-003 📊 数据一致性校验
**校验点**: `total_projects === active_projects`（当前实现 `active_projects` 等于 `total_projects`，即等同于活跃项目数。**注意**: 这个字段命名与实现有歧义——`active_projects` 实际统计的是 `is_active=1` 的项目，但实现中复用了 `total_projects` 的值，未单独按 `is_active` 过滤。如果数据库中有 `is_active=0` 的项目，`active_projects` 将显示错误。）

**校验点**: `total_tasks === todo_tasks + in_progress_tasks + done_tasks`

---

### 5.2. GET `/api/dashboard/my-tasks` — 我的待办

#### TC-DB-MYTASKS-001 ✅ 返回当前用户的待办任务
**前提**: 当前用户有 3 个 `todo`/`in_progress` 状态的任务

**预期结果**:
- 状态码: `200`
- 返回数组，每条包含 `id`, `pid`, `title`, `status`, `priority`, `due_date`, `project_name`, `project_color`
- 按 `updated_at` 降序
- 默认最多 5 条

---

#### TC-DB-MYTASKS-002 ✅ 限制条数
**请求**: `GET /api/dashboard/my-tasks?limit=3`

**预期结果**:
- 最多返回 3 条

---

#### TC-DB-MYTASKS-003 ✅ limit 超上限
**请求**: `GET /api/dashboard/my-tasks?limit=100`

**预期结果**:
- 状态码: `422`（Pydantic `le=50` 校验失败）

---

#### TC-DB-MYTASKS-004 ✅ 无待办任务
**前提**: 当前用户没有分配 `todo`/`in_progress` 状态的任务

**预期结果**:
- 状态码: `200`
- 返回 `[]`

---

#### TC-DB-MYTASKS-005 ✅ 项目名和颜色正确
**校验**: `project_name`, `project_color` 与 tasks 表关联的 projects 表一致

---

### 5.3. GET `/api/dashboard/recent-projects` — 最近项目

#### TC-DB-RECENT-001 ✅ 返回最近的活跃项目
**前提**: 数据库有 5 个活跃项目

**预期结果**:
- 状态码: `200`
- 返回数组，默认 3 条
- 按 `updated_at` 降序
- 每条包含 `id`, `name`, `color`, `progress`, `task_count`

---

#### TC-DB-RECENT-002 ✅ 限制条数
**请求**: `GET /api/dashboard/recent-projects?limit=5`

**预期结果**:
- 最多返回 5 条

---

#### TC-DB-RECENT-003 ✅ limit 超上限
**请求**: `GET /api/dashboard/recent-projects?limit=20`

**预期结果**:
- 状态码: `422`（Pydantic `le=10` 校验失败）

---

#### TC-DB-RECENT-004 ✅ 无活跃项目
**前提**: 所有项目 `is_active=0` 或无项目

**预期结果**:
- 状态码: `200`
- 返回 `[]`

---

#### TC-DB-RECENT-005 ✅ progress 和 task_count 正确性
**校验**: `progress` 与 projects 表一致；`task_count` 等于该项目的实际任务数

---

## 6. 健康检查 (`/api/health`)

#### TC-HEALTH-001 ✅ 无需认证
**请求**: `GET /api/health`（无 Token）

**预期结果**:
- 状态码: `200`
- 响应体: `{"status": "ok", "version": "1.0.0"}`

---

## 附录 A：API 端点速查表

| 序号 | 方法 | 路径 | 认证 | 角色 |
|---|------|------|------|------|
| 1 | POST | `/api/auth/register` | ❌ | - |
| 2 | POST | `/api/auth/login` | ❌ | - |
| 3 | GET | `/api/auth/me` | ✅ | - |
| 4 | GET | `/api/projects` | ✅ | - |
| 5 | POST | `/api/projects` | ✅ | - |
| 6 | GET | `/api/projects/{id}` | ✅ | - |
| 7 | PUT | `/api/projects/{id}` | ✅ | - |
| 8 | DELETE | `/api/projects/{id}` | ✅ | - |
| 9 | GET | `/api/tasks/my` | ✅ | - |
| 10 | GET | `/api/projects/{pid}/tasks` | ✅ | - |
| 11 | POST | `/api/projects/{pid}/tasks` | ✅ | - |
| 12 | GET | `/api/tasks/{id}` | ✅ | - |
| 13 | PUT | `/api/tasks/{id}` | ✅ | - |
| 14 | DELETE | `/api/tasks/{id}` | ✅ | - |
| 15 | PATCH | `/api/tasks/{id}/status` | ✅ | - |
| 16 | GET | `/api/tasks/{id}/comments` | ✅ | - |
| 17 | POST | `/api/tasks/{id}/comments` | ✅ | - |
| 18 | DELETE | `/api/comments/{id}` | ✅ | - |
| 19 | GET | `/api/dashboard/stats` | ✅ | - |
| 20 | GET | `/api/dashboard/my-tasks` | ✅ | - |
| 21 | GET | `/api/dashboard/recent-projects` | ✅ | - |
| 22 | GET | `/api/health` | ❌ | - |

> **共 22 个端点，85 个测试用例** (认证 14 + 项目 17 + 任务 31 + 评论 9 + 统计 13 + 健康 1)

## 附录 B：测试发现的问题

1. **`GET /api/projects/{id}` 未过滤已软删除项目**  
   列表接口过滤了 `is_active=1`，但详情接口直接通过 ID 查询，能查到已软删除的项目，行为不一致。建议详情接口也加入 `filter(Project.is_active == 1)` 校验，或返回 404。

2. **`active_projects` 统计字段名歧义**  
   `/api/dashboard/stats` 中 `active_projects` 实际复用了 `total_projects` 的值，应单独统计 `is_active=1` 的项目。当前若存在软删除项目 (`is_active=0`)，`active_projects` 将显示错误数据。

3. **评论删除权限仅检查"是否自己"**  
   当前删除评论只校验作者身份，没有给管理员或项目 owner 额外的删除权限。建议后续增加角色级别权限。
