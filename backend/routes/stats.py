"""仪表盘统计路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Project, Task
from schemas import DashboardStats, MyTaskItem, RecentProjectItem
from auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """统计卡片数据"""
    total_projects = db.query(func.count(Project.id)).filter(Project.is_active == 1).scalar()
    total_tasks = db.query(func.count(Task.id)).scalar()
    todo_tasks = db.query(func.count(Task.id)).filter(Task.status == "todo").scalar()
    in_progress_tasks = db.query(func.count(Task.id)).filter(Task.status == "in_progress").scalar()
    done_tasks = db.query(func.count(Task.id)).filter(Task.status == "done").scalar()
    total_users = db.query(func.count(User.id)).filter(User.is_active == 1).scalar()

    return DashboardStats(
        total_projects=total_projects or 0,
        active_projects=total_projects or 0,
        total_tasks=total_tasks or 0,
        todo_tasks=todo_tasks or 0,
        in_progress_tasks=in_progress_tasks or 0,
        done_tasks=done_tasks or 0,
        total_users=total_users or 0,
    )


@router.get("/my-tasks", response_model=list[MyTaskItem])
def get_my_tasks(
    limit: int = Query(5, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的待办（<=5条）"""
    tasks = (
        db.query(Task)
        .filter(Task.assignee_id == current_user.id, Task.status.in_(["todo", "in_progress"]))
        .order_by(Task.updated_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for t in tasks:
        project = db.query(Project).filter(Project.id == t.pid).first()
        item = MyTaskItem(
            id=t.id,
            pid=t.pid,
            title=t.title,
            status=t.status,
            priority=t.priority,
            due_date=t.due_date,
            project_name=project.name if project else "",
            project_color=project.color if project else "",
        )
        result.append(item)
    return result


@router.get("/recent-projects", response_model=list[RecentProjectItem])
def get_recent_projects(
    limit: int = Query(3, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """最近项目（<=3条）"""
    projects = (
        db.query(Project)
        .filter(Project.is_active == 1)
        .order_by(Project.updated_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for p in projects:
        task_count = db.query(func.count(Task.id)).filter(Task.pid == p.id).scalar()
        result.append(RecentProjectItem(
            id=p.id,
            name=p.name,
            color=p.color,
            progress=p.progress,
            task_count=task_count or 0,
        ))
    return result
