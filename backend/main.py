"""晴天项目看板 — FastAPI 主入口"""

import asyncio
import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func

from database import init_db, enable_wal_mode, SessionLocal
from models import User, Project, Task

# ── 日志配置 ──
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("qingtian")

app = FastAPI(
    title="晴天项目看板 API",
    description="Hermes 6 Agent 协作看板系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS 中间件（允许前端 MPA 跨域请求） ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 每日日报检查 ──

async def _send_daily_report_if_needed():
    """检查是否需要发送今日日报，首次启动时触发"""
    try:
        from feishu import send_daily_report, FEISHU_WEBHOOK_URL

        if not FEISHU_WEBHOOK_URL:
            logger.info("飞书 Webhook 未配置，跳过每日日报")
            return

        db = SessionLocal()
        try:
            total_projects = db.query(func.count(Project.id)).scalar() or 0
            active_projects = db.query(func.count(Project.id)).filter(Project.is_active == 1).scalar() or 0
            total_tasks = db.query(func.count(Task.id)).scalar() or 0
            todo_tasks = db.query(func.count(Task.id)).filter(Task.status == "todo").scalar() or 0
            in_progress_tasks = db.query(func.count(Task.id)).filter(Task.status == "in_progress").scalar() or 0
            done_tasks = db.query(func.count(Task.id)).filter(Task.status == "done").scalar() or 0
            total_users = db.query(func.count(User.id)).filter(User.is_active == 1).scalar() or 0

            stats = {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "total_tasks": total_tasks,
                "todo_tasks": todo_tasks,
                "in_progress_tasks": in_progress_tasks,
                "done_tasks": done_tasks,
                "total_users": total_users,
            }
        finally:
            db.close()

        await send_daily_report(stats)
        logger.info("每日日报已发送")
    except Exception as e:
        logger.warning("每日日报发送失败（首次运行忽略）: %s", e)


async def _daily_report_loop():
    """后台定时任务：每小时检查一次，在每天 09:00 发送日报"""
    while True:
        now = datetime.now()
        # 每天 9:00 发送日报
        if now.hour == 9 and now.minute == 0:
            logger.info("定时日报触发")
            await _send_daily_report_if_needed()
            # 等一分钟，避免同一小时重复触发
            await asyncio.sleep(120)
        else:
            await asyncio.sleep(60)


# ── 应用生命周期 ──

@app.on_event("startup")
async def on_startup():
    """启动时初始化数据库并启动日报定时任务"""
    logger.info("晴天看板后端启动中...")
    enable_wal_mode()
    init_db()

    # 启动时发送一次日报（异步，不阻塞启动）
    asyncio.create_task(_send_daily_report_if_needed())

    # 启动定时日报循环
    asyncio.create_task(_daily_report_loop())

    logger.info("晴天看板后端启动完成")


# ── 健康检查 ──
@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


# ── 注册路由 ──
from routes.auth import router as auth_router
from routes.projects import router as projects_router
from routes.tasks import router as tasks_router
from routes.comments import router as comments_router
from routes.stats import router as stats_router

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(stats_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
