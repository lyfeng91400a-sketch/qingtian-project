"""Pydantic Schemas — 请求/响应模型"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ── 认证 ──

class UserRegister(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


# ── 用户 ──

class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    avatar: str
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    """用户简要信息（用于关联展示）"""
    id: str
    name: str
    avatar: str
    role: str

    class Config:
        from_attributes = True


# ── 项目 ──

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    color: str = "#4F46E5"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[int] = None

class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    color: str
    progress: int
    creator_id: str
    is_active: int
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserBrief] = None
    task_count: int = 0
    member_count: int = 0

    class Config:
        from_attributes = True


# ── 项目成员 ──

class ProjectMemberOut(BaseModel):
    project_id: str
    user_id: str
    role: str
    joined_at: datetime
    user: Optional[UserBrief] = None

    class Config:
        from_attributes = True


# ── 任务 ──

class TaskCreate(BaseModel):
    title: str = Field(..., max_length=500)
    status: str = Field("todo", pattern="^(todo|in_progress|done)$")
    priority: str = Field("medium", pattern="^(high|medium|low)$")
    assignee_id: Optional[str] = None
    due_date: str = ""
    description: str = ""
    source: str = Field("manual", pattern="^(manual|hermes_agent|feishu_sync)$")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    description: Optional[str] = None

class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done)$")

class TaskOut(BaseModel):
    id: str
    pid: str
    title: str
    status: str
    priority: str
    assignee_id: Optional[str] = None
    due_date: str
    description: str
    feishu_msg_id: str
    source: str
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserBrief] = None

    class Config:
        from_attributes = True


# ── 评论 ──

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1)

class CommentOut(BaseModel):
    id: str
    task_id: str
    author_id: str
    text: str
    created_at: datetime
    author: Optional[UserBrief] = None

    class Config:
        from_attributes = True


# ── 仪表盘 ──

class DashboardStats(BaseModel):
    total_projects: int = 0
    active_projects: int = 0
    total_tasks: int = 0
    todo_tasks: int = 0
    in_progress_tasks: int = 0
    done_tasks: int = 0
    total_users: int = 0


class MyTaskItem(BaseModel):
    id: str
    pid: str
    title: str
    status: str
    priority: str
    due_date: str
    project_name: str = ""
    project_color: str = ""

    class Config:
        from_attributes = True


class RecentProjectItem(BaseModel):
    id: str
    name: str
    color: str
    progress: int
    task_count: int = 0

    class Config:
        from_attributes = True


# ── 通用 ──

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
