"""项目 CRUD 路由"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Project, ProjectMember, Task
from schemas import ProjectCreate, ProjectUpdate, ProjectOut, ProjectMemberOut
from auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["项目"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    keyword: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取项目列表（支持 keyword 搜索）"""
    query = db.query(Project).filter(Project.is_active == 1)

    if keyword:
        query = query.filter(Project.name.ilike(f"%{keyword}%"))

    projects = query.order_by(Project.updated_at.desc()).all()

    result = []
    for p in projects:
        task_count = db.query(func.count(Task.id)).filter(Task.pid == p.id).scalar()
        member_count = db.query(func.count(ProjectMember.user_id)).filter(
            ProjectMember.project_id == p.id
        ).scalar()
        out = ProjectOut.model_validate(p)
        out.task_count = task_count or 0
        out.member_count = member_count or 0
        if p.creator:
            from schemas import UserBrief
            out.creator = UserBrief.model_validate(p.creator)
        result.append(out)

    return result


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建项目"""
    project = Project(
        name=data.name,
        description=data.description,
        color=data.color,
        creator_id=current_user.id,
    )
    db.add(project)
    db.flush()

    # 创建者自动成为项目的 owner
    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(member)
    db.commit()
    db.refresh(project)

    out = ProjectOut.model_validate(project)
    out.task_count = 0
    out.member_count = 1
    from schemas import UserBrief
    out.creator = UserBrief.model_validate(current_user)
    return out


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取单个项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    task_count = db.query(func.count(Task.id)).filter(Task.pid == project.id).scalar()
    member_count = db.query(func.count(ProjectMember.user_id)).filter(
        ProjectMember.project_id == project.id
    ).scalar()
    out = ProjectOut.model_validate(project)
    out.task_count = task_count or 0
    out.member_count = member_count or 0
    if project.creator:
        from schemas import UserBrief
        out.creator = UserBrief.model_validate(project.creator)
    return out


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.color is not None:
        project.color = data.color
    if data.is_active is not None:
        project.is_active = data.is_active

    db.commit()
    db.refresh(project)

    task_count = db.query(func.count(Task.id)).filter(Task.pid == project.id).scalar()
    member_count = db.query(func.count(ProjectMember.user_id)).filter(
        ProjectMember.project_id == project.id
    ).scalar()
    out = ProjectOut.model_validate(project)
    out.task_count = task_count or 0
    out.member_count = member_count or 0
    if project.creator:
        from schemas import UserBrief
        out.creator = UserBrief.model_validate(project.creator)
    return out


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除项目（级联删除任务 + 评论）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    db.delete(project)  # cascade 会自动删除关联的任务、评论、成员
    db.commit()
    return {"message": "项目已删除"}
