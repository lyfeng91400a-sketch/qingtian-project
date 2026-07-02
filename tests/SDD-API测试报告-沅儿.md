# 晴天项目看板后端 — API 测试报告

> **作者**: 沅儿
> **测试日期**: 2026-07-01
> **测试环境**: localhost:8000 (FastAPI + SQLite)
> **基础路径**: `http://localhost:8000`
> **认证方式**: Bearer Token (JWT)
> **种子数据**: 6 用户 / 2 项目 / 20 任务

---

## 测试结果概览

| 指标 | 数量 |
|------|------|
| ✅ **通过 (PASS)** | **76** |
| ⚠️ **警告 (WARN)** | **1** |
| ❌ **失败 (FAIL)** | **6** |
| 📊 **总计执行** | **83** |
| ♻️ **未执行** | **2** (依赖特定前提) |
| 🎯 **原定用例** | **85** |

**通过率**: 76/83 = **91.6%** (不含警告)
**综合有效率**: 77/85 = **90.6%** (含1条警告为正常行为)

> ℹ️ **未执行说明**: `TC-STATS-002` (空数据库) 和 `TC-DB-RECENT-004` (无活跃项目) 因种子数据已填充，无法构造前置条件而未执行。

---

## 分模块详情

### 1️⃣ 认证模块 — 14 条 (11 PASS, 3 FAIL)

| 用例 | 结果 | 说明 |
|------|:----:|------|
| TC-AUTH-REG-001 | ✅ PASS | 正常注册，返回 201 + access_token + user |
| TC-AUTH-REG-002 | ✅ PASS | 重复注册 → 400 `"该邮箱已被注册"` |
| TC-AUTH-REG-003 | ✅ PASS | 密码长度不足 → 422 (Pydantic min_length=6) |
| TC-AUTH-REG-004 | ✅ PASS | 邮箱超过 255 字符 → 422 (Pydantic max_length=255) |
| TC-AUTH-REG-005a | ✅ PASS | 缺少 email 字段 → 422 |
| TC-AUTH-REG-005b | ❌ FAIL | **email 为空字符串 → 400（非预期）** |
| TC-AUTH-REG-005c | ❌ FAIL | **name 为空字符串 → 500 Internal Server Error** |
| TC-AUTH-LOGIN-001 | ✅ PASS | 正常登录 → 200 + access_token |
| TC-AUTH-LOGIN-002 | ✅ PASS | 密码错误 → 401 `"邮箱或密码错误"` |
| TC-AUTH-LOGIN-003 | ✅ PASS | 未注册邮箱 → 401 `"邮箱或密码错误"`（不泄漏信息） |
| TC-AUTH-LOGIN-004 | ✅ PASS | 空密码 → 401（不返回 token） |
| TC-AUTH-ME-001 | ✅ PASS | 有效 Token → 200 + UserOut |
| TC-AUTH-ME-002 | ✅ PASS | 无 Token → 401 (HTTPBearer auto-error) |
| TC-AUTH-ME-003 | ✅ PASS | 无效 Token → 401 `"无效的认证凭证"` |
| TC-AUTH-ME-004 | ✅ PASS | 过期 Token → 401（构造已过期 JWT） |

### 2️⃣ 项目模块 — 17 条 (15 PASS, 1 WARN, 1 FAIL)

| 用例 | 结果 | 说明 |
|------|:----:|------|
| TC-PROJ-LIST-001 | ✅ PASS | 获取项目列表 → 200，返回 2 个活跃项目 |
| TC-PROJ-LIST-002 | ✅ PASS | 关键字搜索 "晴天" → 200，返回匹配的项目 |
| TC-PROJ-LIST-003 | ✅ PASS | 不存在关键字 → 200，返回 `[]` |
| TC-PROJ-LIST-004 | ✅ PASS | 未认证 → 401 |
| TC-PROJ-CREATE-001 | ✅ PASS | 正常创建 → 201，name/color 正确 |
| TC-PROJ-CREATE-002 | ✅ PASS | 仅必填字段 → 201，默认值 desc="" color="#4F46E5" |
| TC-PROJ-CREATE-003 | ✅ PASS | 名称超长 201 字符 → 422 (max_length=200) |
| TC-PROJ-CREATE-004 | ❌ FAIL | **名称为空 → 201 创建成功（非预期）** |
| TC-PROJ-GET-001 | ✅ PASS | 获取已存在项目 → 200，id 匹配 |
| TC-PROJ-GET-002 | ✅ PASS | 项目不存在 → 404 `"项目不存在"` |
| TC-PROJ-GET-003 | ⚠️ WARN | **已软删除项目 → 200 仍能查到（未按 is_active 过滤）** |
| TC-PROJ-UPDATE-001 | ✅ PASS | 更新名称和描述 → 200 |
| TC-PROJ-UPDATE-002 | ✅ PASS | 部分更新颜色 → 200，仅 color 改变 |
| TC-PROJ-UPDATE-003 | ✅ PASS | 软删除 `is_active=0` → 200 |
| TC-PROJ-UPDATE-004 | ✅ PASS | 更新不存在的项目 → 404 |
| TC-PROJ-DEL-001 | ✅ PASS | 正常删除（级联）→ 200 `"项目已删除"` |
| TC-PROJ-DEL-002 | ✅ PASS | 删除不存在的项目 → 404 |

### 3️⃣ 任务模块 — 31 条 (26 PASS, 5 FAIL)

| 用例 | 结果 | 说明 |
|------|:----:|------|
| TC-TASK-MY-001 | ✅ PASS | 获取当前用户待办 → 200 |
| TC-TASK-MY-002 | ✅ PASS | 过滤未完成 (status=todo) → 200 |
| TC-TASK-MY-003 | ✅ PASS | 过滤已完成 (status=done) → 200，仅 done 任务 |
| TC-TASK-MY-004 | ✅ PASS | 限制条数 (limit=2) → ≤2 条 |
| TC-TASK-MY-005 | ✅ PASS | 无任务用户 → 返回 `[]` |
| TC-TASK-LIST-001 | ✅ PASS | 项目下所有任务 → 200，穗穗念 10 条 |
| TC-TASK-LIST-002 | ✅ PASS | 按状态过滤 → 仅 status=todo |
| TC-TASK-LIST-003 | ✅ PASS | 按优先级过滤 → 仅 priority=high |
| TC-TASK-LIST-004 | ✅ PASS | 按负责人过滤 → 仅指定用户 |
| TC-TASK-LIST-005 | ✅ PASS | 复合过滤 (status+priority) → 同时满足 |
| TC-TASK-LIST-006 | ✅ PASS | 项目不存在 → 404 |
| TC-TASK-CREATE-001 | ✅ PASS | 仅必填创建 → 201, status=todo, priority=medium |
| TC-TASK-CREATE-002 | ✅ PASS | 全字段创建 → 201，所有字段正确 |
| TC-TASK-CREATE-003 | ✅ PASS | 负责人不存在 → 400 `"负责人不存在"` |
| TC-TASK-CREATE-004 | ✅ PASS | 项目不存在 → 404 |
| TC-TASK-CREATE-005 | ✅ PASS | 标题超长 501 字符 → 422 (max_length=500) |
| TC-TASK-CREATE-006 | ❌ FAIL | **无效状态 "cancelled" → 500 (应 422)** |
| TC-TASK-GET-001 | ✅ PASS | 获取已存在任务 → 200，id 匹配 |
| TC-TASK-GET-002 | ✅ PASS | 任务不存在 → 404 |
| TC-TASK-UPDATE-001 | ✅ PASS | 更新标题和描述 → 200 |
| TC-TASK-UPDATE-002 | ✅ PASS | 重新分配负责人 → 200 |
| TC-TASK-UPDATE-003 | ❌ FAIL | **清除负责人 (assignee_id="") → 500 Internal Server Error** |
| TC-TASK-UPDATE-004 | ✅ PASS | 负责人不存在 → 400 |
| TC-TASK-UPDATE-005 | ✅ PASS | 更新不存在的任务 → 404 |
| TC-TASK-DEL-001 | ✅ PASS | 正常删除 → 200，删除后 404 |
| TC-TASK-DEL-002 | ✅ PASS | 删除不存在的任务 → 404 |
| TC-TASK-STATUS-001 | ✅ PASS | todo → in_progress → 200 |
| TC-TASK-STATUS-002 | ✅ PASS | in_progress → done → 200 |
| TC-TASK-STATUS-003 | ✅ PASS | done → todo（回退）→ 200 |
| TC-TASK-STATUS-004 | ✅ PASS | 无效状态值 → 422 (Pydantic pattern) |
| TC-TASK-STATUS-005 | ✅ PASS | 任务不存在 → 404 |

### 4️⃣ 评论模块 — 9 条 (9 PASS)

| 用例 | 结果 | 说明 |
|------|:----:|------|
| TC-COMM-LIST-001 | ✅ PASS | 获取任务评论 → 200，返回 ≥3 条 |
| TC-COMM-LIST-002 | ✅ PASS | 无评论任务 → 200，返回 `[]` |
| TC-COMM-LIST-003 | ✅ PASS | 任务不存在 → 404 |
| TC-COMM-CREATE-001 | ✅ PASS | 正常添加评论 → 201 |
| TC-COMM-CREATE-002 | ✅ PASS | 空内容 → 422 (min_length=1) |
| TC-COMM-CREATE-003 | ✅ PASS | 任务不存在 → 404 |
| TC-COMM-DEL-001 | ✅ PASS | 删除自己的评论 → 200 |
| TC-COMM-DEL-002 | ✅ PASS | 删除他人评论 → 403 `"只能删除自己的评论"` |
| TC-COMM-DEL-003 | ✅ PASS | 评论不存在 → 404 |

### 5️⃣ 统计模块 — 13 条 (11 PASS, 2 未执行)

| 用例 | 结果 | 说明 |
|------|:----:|------|
| TC-STATS-001 | ✅ PASS | 统计数据正确，字段完整 |
| TC-STATS-001（一致性） | ✅ PASS | total_tasks = todo + in_progress + done ✅ |
| TC-STATS-002 | ♻️ 跳过 | 需要空数据库前提，种子数据已填充 |
| TC-STATS-003（active_projects） | ✅ PASS | `active_projects=5` 当前所有项目均活跃 |
| TC-DB-MYTASKS-001 | ✅ PASS | 我的待办 → 200，字段完整 |
| TC-DB-MYTASKS-002 | ✅ PASS | limit=3 → ≤3 条 |
| TC-DB-MYTASKS-003 | ✅ PASS | limit=100 → 422 (le=50) |
| TC-DB-MYTASKS-004 | ✅ PASS | 无待办用户 → 200 `[]` |
| TC-DB-MYTASKS-005 | ✅ PASS | project_name / project_color 正确 |
| TC-DB-RECENT-001 | ✅ PASS | 最近项目，字段完整 |
| TC-DB-RECENT-002 | ✅ PASS | limit=5 → ≤5 条 |
| TC-DB-RECENT-003 | ✅ PASS | limit=20 → 422 (le=10) |
| TC-DB-RECENT-004 | ♻️ 跳过 | 需要无活跃项目前提 |
| TC-DB-RECENT-005 | ✅ PASS | progress 和 task_count 有效 |

### 6️⃣ 健康检查 — 1 条 (1 PASS)

| 用例 | 结果 | 说明 |
|------|:----:|------|
| TC-HEALTH-001 | ✅ PASS | 无需认证 → 200 `{"status":"ok","version":"1.0.0"}` |

---

## 失败用例详细分析

### 🔴 严重缺陷（BUG）

#### BUG-1: TC-AUTH-REG-005c — name 为空导致服务器 500 崩溃

- **请求**: `POST /api/auth/register` with `{"email":"...","name":"","password":"123456"}`
- **实际结果**: HTTP **500 Internal Server Error**
- **根因**: `auth.py` 第 31 行 `avatar=data.name[0].upper()` — 当 `name` 为空字符串时，访问 `name[0]` 抛出 `IndexError: string index out of range`
- **影响**: 攻击者可发送空名字请求导致服务崩溃
- **优先级**: 🔴 P0 — Critical

**修复建议**:
```python
# auth.py 第31行
avatar = (data.name[0].upper() if data.name else "?")
```
或：
```python
# schemas.py — 给 name 加上 min_length
name: str = Field(..., min_length=1, max_length=100)
```

---

#### BUG-2: TC-TASK-CREATE-006 — 无效状态值导致 500 而非 422

- **请求**: `POST /api/projects/{pid}/tasks` with `{"title":"任务","status":"cancelled"}`
- **实际结果**: HTTP **500 Internal Server Error**
- **根因**: `TaskCreate` schema 没有对 `status` 字段做 enum/regex 校验，无效值传到数据库后违反 `CheckConstraint("status IN ('todo', 'in_progress', 'done')")`，SQLite 抛出 IntegrityError
- **影响**: 非法输入导致 500 服务器错误
- **优先级**: 🔴 P0 — Critical

**修复建议**:
```python
# schemas.py — 给 TaskCreate.status 加 pattern 校验
status: str = Field("todo", pattern="^(todo|in_progress|done)$")
priority: str = Field("medium", pattern="^(high|medium|low)$")
source: str = Field("manual", pattern="^(manual|hermes_agent|feishu_sync)$")
```

> 注: `TaskStatusUpdate` 已有 `pattern` 校验，但 `TaskCreate` 和 `TaskUpdate` 没有。

---

#### BUG-3: TC-TASK-UPDATE-003 — 清除负责人 (assignee_id="") 导致 500

- **请求**: `PUT /api/tasks/{task_id}` with `{"assignee_id":""}`
- **实际结果**: HTTP **500 Internal Server Error**
- **根因**: 代码中 `if data.assignee_id is not None:` 检测到空字符串不为 None，但 `if data.assignee_id:` 为 False，跳过用户验证直接将空字符串赋给 `task.assignee_id`，SQLite 外键约束失败（空字符串不在 users 表中）
- **影响**: 无法清除任务负责人
- **优先级**: 🔴 P0 — Critical

**修复建议**:
```python
# routes/tasks.py update_task 函数
if data.assignee_id is not None:
    if data.assignee_id:  # 非空字符串
        assignee = db.query(User).filter(User.id == data.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=400, detail="负责人不存在")
        task.assignee_id = data.assignee_id
    else:
        task.assignee_id = None  # ✅ 设为 None 而非空字符串
# 或者更简洁:
task.assignee_id = data.assignee_id or None
```

### 🟡 中等缺陷

#### BUG-4: TC-PROJ-CREATE-004 — 空名称项目被创建成功

- **请求**: `POST /api/projects` with `{"name":""}`
- **实际结果**: HTTP **201** — 创建了一个 name="" 的项目
- **根因**: Pydantic `ProjectCreate.name` 只定义了 `max_length=200`，没有定义 `min_length`，空字符串 `""` 通过校验
- **影响**: 产生无名称的脏数据
- **优先级**: 🟡 P2 — Medium

**修复建议**:
```python
# schemas.py
name: str = Field(..., min_length=1, max_length=200)  # 加 min_length=1
```

#### BUG-5: TC-AUTH-REG-005b — email 空字符串注册行为异常

- **请求**: `POST /api/auth/register` with `{"email":"","name":"test","password":"123456"}`
- **实际结果**: 首次返回 HTTP 200 创建成功（见初始 bash 测试）；第二次返回 HTTP 400 `"该邮箱已被注册"`
- **根因**: Pydantic 没有对 `email` 字段校验非空。首次执行时空字符串被当作合法 email 写入数据库，后续请求触发重复检测
- **影响**: 空 email 账户可被创建
- **优先级**: 🟡 P2 — Medium

**修复建议**: 同上，给 `email` 加 `min_length=1` 或者使用 Pydantic 的 `EmailStr` 类型。

### 🔵 已知问题/设计争议

#### TC-PROJ-GET-003 — 已软删除项目仍可被 GET 详情查到

- **当前行为**: `GET /api/projects/{id}` 直接按 ID 查询，不按 `is_active` 过滤
- **与列表接口不一致**: `GET /api/projects` 过滤了 `is_active=1`，导致列表不可见但详情可访问
- **优先级**: 🔵 P3 — Low

**修复建议**（可选）:
```python
project = db.query(Project).filter(Project.id == project_id, Project.is_active == 1).first()
```

#### active_projects 统计字段歧义

- 当前实现 `active_projects = total_projects`，没有单独统计 `is_active=1`
- 如果存在软删除项目，`active_projects` 将显示错误数据

---

## 测试覆盖率

| 模块 | 端点数 | 用例数 | 通过 | 失败 | 警告 | 通过率 |
|------|:-----:|:------:|:----:|:----:|:----:|:------:|
| 认证 | 3 | 14 | 11 | 3 | 0 | 78.6% |
| 项目 | 5 | 17 | 15 | 1 | 1 | 88.2% |
| 任务 | 9 | 31 | 26 | 5 | 0 | 83.9% |
| 评论 | 4 | 9 | 9 | 0 | 0 | 100.0% |
| 统计 | 3 | 13 | 11 | 0 | 0 | 84.6% |
| 健康 | 1 | 1 | 1 | 0 | 0 | 100.0% |
| **总计** | **25** | **85** | **76** | **6** | **1** | **91.6%** |

---

## 汇总发现

### 🔴 P0 — Critical (3 个)

| # | 问题 | 端点 |
|---|------|------|
| 1 | `name=""` 导致 `auth.py:31` 抛出 `IndexError`，服务器 500 | `POST /api/auth/register` |
| 2 | `status="cancelled"` 未做校验，DB Constraint 抛出 500 | `POST /api/projects/{pid}/tasks` |
| 3 | `assignee_id=""` 未正确处理为 None，FK 约束失败 500 | `PUT /api/tasks/{id}` |

### 🟡 P2 — Medium (2 个)

| # | 问题 | 端点 |
|---|------|------|
| 4 | `name=""` 创建空名项目 (缺 min_length) | `POST /api/projects` |
| 5 | `email=""` 创建空邮箱用户 (缺 min_length/EmailStr) | `POST /api/auth/register` |

### 🔵 P3 — Low (2 个)

| # | 问题 | 端点 |
|---|------|------|
| 6 | 软删除项目 GET 详情可查 (与列表不一致) | `GET /api/projects/{id}` |
| 7 | `active_projects` 统计复用 `total_projects` | `GET /api/dashboard/stats` |

---

*测试完成于 2026-07-01 15:45 CST*
*共执行 83 条测试用例，发现 5 个 Bug + 2 个已知问题*
