"""任务 CRUD 路由"""

import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Task, Project, Comment
from schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskOut, CommentOut
from auth import get_current_user
from feishu import notify_task_created, notify_task_updated, notify_task_status_changed

router = APIRouter(prefix="/api", tags=["任务"])


@router.get("/tasks/my", response_model=list[TaskOut])
def get_my_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的待办任务"""
    query = db.query(Task).filter(Task.assignee_id == current_user.id)

    if status_filter:
        if status_filter == "todo":
            query = query.filter(Task.status.in_(["todo", "in_progress"]))
        else:
            query = query.filter(Task.status == status_filter)

    tasks = query.order_by(Task.updated_at.desc()).limit(limit).all()

    result = []
    for t in tasks:
        out = TaskOut.model_validate(t)
        if t.assignee:
            from schemas import UserBrief
            out.assignee = UserBrief.model_validate(t.assignee)
        result.append(out)
    return result


@router.get("/projects/{pid}/tasks", response_model=list[TaskOut])
def list_tasks(
    pid: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取项目下的任务列表（支持过滤）"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    query = db.query(Task).filter(Task.pid == pid)

    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    tasks = query.order_by(Task.created_at.desc()).all()

    result = []
    for t in tasks:
        out = TaskOut.model_validate(t)
        if t.assignee:
            from schemas import UserBrief
            out.assignee = UserBrief.model_validate(t.assignee)
        result.append(out)
    return result


@router.post("/projects/{pid}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    pid: str,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建任务"""
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    # 验证 assignee 存在
    if data.assignee_id:
        assignee = db.query(User).filter(User.id == data.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="负责人不存在")

    task = Task(
        pid=pid,
        title=data.title,
        status=data.status,
        priority=data.priority,
        assignee_id=data.assignee_id,
        due_date=data.due_date,
        description=data.description,
        source=data.source,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 更新项目进度
    _update_project_progress(pid, db)

    out = TaskOut.model_validate(task)
    if task.assignee:
        from schemas import UserBrief
        out.assignee = UserBrief.model_validate(task.assignee)
        task_assignee_name = out.assignee.name
    else:
        task_assignee_name = "未分配"

    # 飞书通知：任务创建（fire-and-forget）
    task_dict = {
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "assignee": {"name": task_assignee_name},
    }
    asyncio.create_task(notify_task_created(task_dict, current_user.name))

    return out


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取单个任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    out = TaskOut.model_validate(task)
    if task.assignee:
        from schemas import UserBrief
        out.assignee = UserBrief.model_validate(task.assignee)
    return out


@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    # 记录变更前状态
    changes = {}

    if data.title is not None and data.title != task.title:
        changes["标题"] = {"old": task.title, "new": data.title}
        task.title = data.title
    if data.status is not None and data.status != task.status:
        changes["状态"] = {"old": task.status, "new": data.status}
        task.status = data.status
    if data.priority is not None and data.priority != task.priority:
        changes["优先级"] = {"old": task.priority, "new": data.priority}
        task.priority = data.priority
    if data.assignee_id is not None:
        old_assignee = task.assignee_id
        if data.assignee_id:
            assignee = db.query(User).filter(User.id == data.assignee_id).first()
            if not assignee:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="负责人不存在")
            task.assignee_id = data.assignee_id
        else:
            task.assignee_id = None  # 空字符串视为清除负责人
        if task.assignee_id != old_assignee:
            changes["负责人"] = {"old": old_assignee or "无", "new": task.assignee_id or "无"}
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.description is not None:
        task.description = data.description

    db.commit()
    db.refresh(task)

    # 更新项目进度
    _update_project_progress(task.pid, db)

    out = TaskOut.model_validate(task)
    if task.assignee:
        from schemas import UserBrief
        out.assignee = UserBrief.model_validate(task.assignee)

    # 飞书通知：任务更新（fire-and-forget）
    if changes:
        task_dict = {
            "title": task.title,
            "status": task.status,
            "assignee": {"name": out.assignee.name if task.assignee else "未分配"},
        }
        asyncio.create_task(notify_task_updated(task_dict, current_user.name, changes))

    return out


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除任务（级联删除评论）"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    pid = task.pid
    db.delete(task)  # cascade 会自动删除关联的评论
    db.commit()

    # 更新项目进度
    _update_project_progress(pid, db)
    return {"message": "任务已删除"}


@router.patch("/tasks/{task_id}/status", response_model=TaskOut)
async def update_task_status(
    task_id: str,
    data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """切换任务状态（todo ↔ in_progress ↔ done）"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    old_status = task.status
    task.status = data.status
    db.commit()
    db.refresh(task)

    # 更新项目进度
    _update_project_progress(task.pid, db)

    out = TaskOut.model_validate(task)
    if task.assignee:
        from schemas import UserBrief
        out.assignee = UserBrief.model_validate(task.assignee)

    # 飞书通知：状态变更（fire-and-forget）
    task_dict = {
        "title": task.title,
        "status": task.status,
        "assignee": {"name": out.assignee.name if task.assignee else "未分配"},
    }
    asyncio.create_task(notify_task_status_changed(task_dict, current_user.name, old_status, data.status))

    return out


def _update_project_progress(pid: str, db: Session):
    """自动计算项目进度（done 任务数 / 总任务数）"""
    total = db.query(func.count(Task.id)).filter(Task.pid == pid).scalar()
    if total == 0:
        progress = 0
    else:
        done = db.query(func.count(Task.id)).filter(
            Task.pid == pid, Task.status == "done"
        ).scalar()
        progress = int(done / total * 100)

    db.query(Project).filter(Project.id == pid).update({"progress": progress})
    db.commit()
