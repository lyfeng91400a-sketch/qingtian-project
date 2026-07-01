"""飞书消息推送模块

通过群机器人 Webhook 发送通知到飞书群。

配置方式（环境变量）:
    FEISHU_WEBHOOK_URL: 飞书群机器人 Webhook 地址
    FEISHU_DRY_RUN: 设为 "1" 时仅打印不发送（开发调试用）

使用方式:
    from feishu import notify_task_created, notify_task_status_changed
    
    await notify_task_created(task_data, operator_name)
    await notify_task_status_changed(task_data, operator_name)
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── 配置 ──

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
DRY_RUN = os.environ.get("FEISHU_DRY_RUN", "0") == "1"

# ── 状态映射 ──

STATUS_LABELS = {
    "todo": "📋 待办",
    "in_progress": "🔄 进行中",
    "done": "✅ 已完成",
}

STATUS_TEMPLATES = {
    "todo": "blue",
    "in_progress": "orange",
    "done": "green",
}

PRIORITY_LABELS = {
    "high": "🔴 高",
    "medium": "🟡 中",
    "low": "🟢 低",
}


def _is_configured() -> bool:
    """检查飞书 Webhook 是否已配置"""
    return bool(FEISHU_WEBHOOK_URL)


def _build_card(title: str, template: str, elements: list[dict[str, Any]]) -> dict[str, Any]:
    """构建飞书消息卡片"""
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": elements,
        },
    }


async def _send(payload: dict) -> bool:
    """发送消息到飞书（DRY_RUN 时只打印不发送）"""
    if not _is_configured():
        logger.warning("FEISHU_WEBHOOK_URL 未配置，跳过飞书通知")
        return False

    if DRY_RUN:
        logger.info("[FEISHU DRY_RUN] 模拟发送:\n%s", json.dumps(payload, ensure_ascii=False, indent=2))
        return True

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(FEISHU_WEBHOOK_URL, json=payload)
            if resp.status_code != 200:
                logger.error("飞书通知失败: HTTP %s, %s", resp.status_code, resp.text)
                return False
            logger.info("飞书通知成功: %s", resp.json().get("data", {}))
            return True
    except Exception as e:
        logger.error("飞书通知异常: %s", e)
        return False


# ── 公开 API ──

async def notify_task_created(task: dict, operator: str) -> bool:
    """任务创建通知"""
    title = task.get("title", "")
    status = task.get("status", "todo")
    priority = task.get("priority", "medium")
    assignee = task.get("assignee", {}).get("name", "未分配")
    due = task.get("due_date", "") or "未设置"

    elements = [
        {"tag": "markdown", "content": f"**📌 {title}**"},
        {"tag": "markdown", "content": f"状态: {STATUS_LABELS.get(status, '📝 未知')}"},
        {"tag": "markdown", "content": f"优先级: {PRIORITY_LABELS.get(priority, '中')}"},
        {"tag": "markdown", "content": f"负责人: {assignee}"},
        {"tag": "markdown", "content": f"截止日期: {due}"},
        {"tag": "markdown", "content": f"创建人: {operator}"},
        {"tag": "hr"},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}]},
    ]

    payload = _build_card("🎯 新任务创建", "blue", elements)
    return await _send(payload)


async def notify_task_updated(task: dict, operator: str, changes: Optional[dict] = None) -> bool:
    """任务更新通知

    Args:
        task: 更新后的任务数据
        operator: 操作人
        changes: 变更字段字典，如 {"status": {"old": "todo", "new": "in_progress"}}
    """
    title = task.get("title", "")
    status = task.get("status", "todo")
    assignee = task.get("assignee", {}).get("name", "未分配")

    elements = [
        {"tag": "markdown", "content": f"**✏️ {title}**"},
        {"tag": "markdown", "content": f"当前状态: {STATUS_LABELS.get(status, '📝 未知')}"},
        {"tag": "markdown", "content": f"负责人: {assignee}"},
    ]

    if changes:
        change_text = "\n".join(
            f"• **{k}**: {v.get('old', '')} → {v.get('new', '')}"
            for k, v in changes.items()
        )
        if change_text:
            elements.insert(1, {"tag": "markdown", "content": f"**变更内容:**\n{change_text}"})

    elements.append({"tag": "markdown", "content": f"操作人: {operator}"})
    elements.append({"tag": "hr"})
    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}],
    })

    payload = _build_card("🔄 任务已更新", "indigo", elements)
    return await _send(payload)


async def notify_task_status_changed(task: dict, operator: str, old_status: str, new_status: str) -> bool:
    """任务状态变更通知（独立接口，用于 status patch）"""
    title = task.get("title", "")
    assignee = task.get("assignee", {}).get("name", "未分配")

    old_label = STATUS_LABELS.get(old_status, old_status)
    new_label = STATUS_LABELS.get(new_status, new_status)
    template = STATUS_TEMPLATES.get(new_status, "blue")

    elements = [
        {"tag": "markdown", "content": f"**{title}**"},
        {"tag": "markdown", "content": f"{old_label} → {new_label}"},
        {"tag": "markdown", "content": f"负责人: {assignee}"},
        {"tag": "markdown", "content": f"操作人: {operator}"},
        {"tag": "hr"},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}]},
    ]

    emoji = "✅" if new_status == "done" else "🔄"
    payload = _build_card(f"{emoji} 任务状态变更", template, elements)
    return await _send(payload)


async def send_daily_report(stats: dict) -> bool:
    """发送每日日报到飞书群

    Args:
        stats: 统计数据，包含:
            - total_projects, active_projects
            - total_tasks, todo_tasks, in_progress_tasks, done_tasks
            - total_users
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # 计算完成率
    total = stats.get("total_tasks", 0)
    done = stats.get("done_tasks", 0)
    completion_rate = f"{int(done / total * 100)}%" if total > 0 else "0%"

    elements = [
        {"tag": "markdown", "content": f"📅 **{today} 项目日报**"},
        {"tag": "hr"},
        {"tag": "markdown", "content": f"**项目概览**"},
        {"tag": "markdown", "content": f"• 活跃项目: {stats.get('active_projects', 0)} / {stats.get('total_projects', 0)}"},
        {"tag": "markdown", "content": f"• 总用户数: {stats.get('total_users', 0)}"},
        {"tag": "hr"},
        {"tag": "markdown", "content": f"**任务进度**"},
        {"tag": "markdown", "content": f"• 总任务: {total}"},
        {"tag": "markdown", "content": f"• 📋 待办: {stats.get('todo_tasks', 0)}"},
        {"tag": "markdown", "content": f"• 🔄 进行中: {stats.get('in_progress_tasks', 0)}"},
        {"tag": "markdown", "content": f"• ✅ 已完成: {done}"},
        {"tag": "markdown", "content": f"• 📊 完成率: **{completion_rate}**"},
    ]

    payload = _build_card(f"📊 晴天看板日报 - {today}", "blue", elements)
    return await _send(payload)
