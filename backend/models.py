"""SQLAlchemy 数据模型 — 7张表

1. users         — 用户表（6 个 Hermes Agent 映射）
2. projects      — 项目表
3. project_members — 项目成员关联表
4. tasks         — 任务表
5. comments      — 评论表
6. feishu_sync_log — 飞书同步日志表
7. activity_log  — 活动日志表
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index, text
)
from sqlalchemy.orm import relationship

from database import Base


def gen_id():
    """生成短 UUID 作为主键（去掉连字符，取前16位）"""
    return uuid.uuid4().hex[:16]


def now():
    return datetime.utcnow()


# ──────────────────────────────────────────────
# 1. users — 用户表
# ──────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(String(16), primary_key=True, default=gen_id)
    email         = Column(String(255), nullable=False, unique=True, index=True)
    name          = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20), nullable=False, default="member")
    avatar        = Column(String(500), default="")
    is_active     = Column(Integer, nullable=False, default=1)
    created_at    = Column(DateTime, nullable=False, default=now)
    updated_at    = Column(DateTime, nullable=False, default=now, onupdate=now)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="ck_user_role"),
    )

    # 关系
    created_projects = relationship("Project", back_populates="creator", lazy="select")
    assigned_tasks   = relationship("Task", back_populates="assignee", lazy="select",
                                     foreign_keys="Task.assignee_id")
    comments         = relationship("Comment", back_populates="author", lazy="select")


# ──────────────────────────────────────────────
# 2. projects — 项目表
# ──────────────────────────────────────────────
class Project(Base):
    __tablename__ = "projects"

    id          = Column(String(16), primary_key=True, default=gen_id)
    name        = Column(String(200), nullable=False)
    description = Column(Text, default="")
    color       = Column(String(20), nullable=False, default="#4F46E5")
    progress    = Column(Integer, nullable=False, default=0)  # 0-100
    creator_id  = Column(String(16), ForeignKey("users.id"), nullable=False)
    is_active   = Column(Integer, nullable=False, default=1)
    created_at  = Column(DateTime, nullable=False, default=now)
    updated_at  = Column(DateTime, nullable=False, default=now, onupdate=now)

    __table_args__ = (
        Index("idx_projects_creator", "creator_id"),
    )

    # 关系
    creator      = relationship("User", back_populates="created_projects", lazy="select")
    tasks        = relationship("Task", back_populates="project", lazy="select",
                                 cascade="all, delete-orphan")
    members      = relationship("ProjectMember", back_populates="project", lazy="select",
                                 cascade="all, delete-orphan")


# ──────────────────────────────────────────────
# 3. project_members — 项目成员表
# ──────────────────────────────────────────────
class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(String(16), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id    = Column(String(16), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role       = Column(String(20), nullable=False, default="member")
    joined_at  = Column(DateTime, nullable=False, default=now)

    __table_args__ = (
        CheckConstraint("role IN ('owner', 'member')", name="ck_member_role"),
    )

    # 关系
    project = relationship("Project", back_populates="members")
    user    = relationship("User")


# ──────────────────────────────────────────────
# 4. tasks — 任务表
# ──────────────────────────────────────────────
class Task(Base):
    __tablename__ = "tasks"

    id            = Column(String(16), primary_key=True, default=gen_id)
    pid           = Column(String(16), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title         = Column(String(500), nullable=False)
    status        = Column(String(20), nullable=False, default="todo")
    priority      = Column(String(20), nullable=False, default="medium")
    assignee_id   = Column(String(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date      = Column(String(20), default="")  # 'MM-DD' 或 ISO date
    description   = Column(Text, default="")
    feishu_msg_id = Column(String(100), default="")
    source        = Column(String(20), nullable=False, default="manual")
    created_at    = Column(DateTime, nullable=False, default=now)
    updated_at    = Column(DateTime, nullable=False, default=now, onupdate=now)

    __table_args__ = (
        CheckConstraint("status IN ('todo', 'in_progress', 'done')", name="ck_task_status"),
        CheckConstraint("priority IN ('high', 'medium', 'low')", name="ck_task_priority"),
        CheckConstraint("source IN ('manual', 'hermes_agent', 'feishu_sync')", name="ck_task_source"),
        Index("idx_tasks_project", "pid"),
        Index("idx_tasks_assignee", "assignee_id"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_project_status", "pid", "status"),
    )

    # 关系
    project  = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks",
                             foreign_keys=[assignee_id], lazy="select")
    comments = relationship("Comment", back_populates="task", lazy="select",
                             cascade="all, delete-orphan",
                             order_by="Comment.created_at")


# ──────────────────────────────────────────────
# 5. comments — 评论表
# ──────────────────────────────────────────────
class Comment(Base):
    __tablename__ = "comments"

    id         = Column(String(16), primary_key=True, default=gen_id)
    task_id    = Column(String(16), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    author_id  = Column(String(16), ForeignKey("users.id"), nullable=False)
    text       = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=now)

    __table_args__ = (
        Index("idx_comments_task", "task_id"),
    )

    # 关系
    task   = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")


# ──────────────────────────────────────────────
# 6. feishu_sync_log — 飞书同步日志表
# ──────────────────────────────────────────────
class FeishuSyncLog(Base):
    __tablename__ = "feishu_sync_log"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    event_type    = Column(String(50), nullable=False)  # 'task_created', 'task_updated', 'status_changed'
    task_id       = Column(String(16), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    feishu_msg_id = Column(String(100), default="")
    direction     = Column(String(20), nullable=False)  # 'to_feishu', 'from_feishu'
    status        = Column(String(20), nullable=False, default="success")
    error_msg     = Column(Text, default="")
    created_at    = Column(DateTime, nullable=False, default=now)

    __table_args__ = (
        CheckConstraint("direction IN ('to_feishu', 'from_feishu')", name="ck_sync_direction"),
        CheckConstraint("status IN ('success', 'failed')", name="ck_sync_status"),
    )


# ──────────────────────────────────────────────
# 7. activity_log — 活动日志表
# ──────────────────────────────────────────────
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    entity_type  = Column(String(30), nullable=False)  # 'task', 'project', 'comment'
    entity_id    = Column(String(16), nullable=False)
    action       = Column(String(50), nullable=False)  # 'created', 'updated', 'status_changed'
    actor_id     = Column(String(16), ForeignKey("users.id"), nullable=True)
    old_value    = Column(Text, default="")
    new_value    = Column(Text, default="")
    created_at   = Column(DateTime, nullable=False, default=now)

    __table_args__ = (
        Index("idx_activity_entity", "entity_type", "entity_id"),
        Index("idx_activity_actor", "actor_id"),
    )
