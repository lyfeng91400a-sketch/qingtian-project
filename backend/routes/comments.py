"""评论 CRUD 路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Task, Comment
from schemas import CommentCreate, CommentOut
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["评论"])


@router.get("/tasks/{task_id}/comments", response_model=list[CommentOut])
def list_comments(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务评论列表"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    comments = db.query(Comment).filter(
        Comment.task_id == task_id
    ).order_by(Comment.created_at.asc()).all()

    result = []
    for c in comments:
        out = CommentOut.model_validate(c)
        if c.author:
            from schemas import UserBrief
            out.author = UserBrief.model_validate(c.author)
        result.append(out)
    return result


@router.post("/tasks/{task_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: str,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加评论"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    comment = Comment(
        task_id=task_id,
        author_id=current_user.id,
        text=data.text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    out = CommentOut.model_validate(comment)
    from schemas import UserBrief
    out.author = UserBrief.model_validate(current_user)
    return out


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除评论"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 只能删除自己的评论
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的评论",
        )

    db.delete(comment)
    db.commit()
    return {"message": "评论已删除"}
