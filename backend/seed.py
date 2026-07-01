"""种子数据脚本

填充：
- 6 个 Hermes Agent 用户
- 2 个示例项目（穗穗念、小红书）
- 穗穗念 10 条 seed 任务
- 小红书 10 条 seed 任务
- 项目成员关联
"""

from datetime import datetime

from database import SessionLocal, init_db, enable_wal_mode
from models import User, Project, ProjectMember, Task
from auth import hash_password


def seed():
    enable_wal_mode()
    init_db()
    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(User).count() > 0:
            print("⚠️  数据库已有数据，跳过 seed。如需重新填充，请先删除 qingtian.db")
            return

        # ── 1. 创建 6 个 Agent 用户 ──
        agents = [
            {"email": "liu@qingtian.com",  "name": "刘风翼", "role": "admin"},
            {"email": "zhao@qingtian.com", "name": "赵工",   "role": "admin"},
            {"email": "wang@qingtian.com", "name": "王工",   "role": "member"},
            {"email": "qiqi@qingtian.com", "name": "童七七", "role": "member"},
            {"email": "yuan@qingtian.com", "name": "沅儿",   "role": "member"},
            {"email": "gong@qingtian.com", "name": "工",     "role": "member"},
        ]

        users = {}
        for a in agents:
            user = User(
                email=a["email"],
                name=a["name"],
                password_hash=hash_password("123456"),
                role=a["role"],
                avatar=a["name"][0].upper(),
            )
            db.add(user)
            db.flush()
            users[a["email"]] = user

        print(f"✅ 创建了 {len(agents)} 个用户")

        # ── 2. 创建 2 个项目 ──
        projects_data = [
            {
                "name": "穗穗念",
                "description": "穗穗念项目 — 内容创作与发布平台。包括文章撰写、排版、发布、数据分析等全流程管理。",
                "color": "#F59E0B",
                "creator_email": "qiqi@qingtian.com",
            },
            {
                "name": "小红书运营",
                "description": "小红书账号运营 — 笔记创作、话题策划、粉丝互动、数据复盘。",
                "color": "#EC4899",
                "creator_email": "qiqi@qingtian.com",
            },
        ]

        projects = {}
        for pd in projects_data:
            project = Project(
                name=pd["name"],
                description=pd["description"],
                color=pd["color"],
                creator_id=users[pd["creator_email"]].id,
            )
            db.add(project)
            db.flush()
            projects[pd["name"]] = project

            # 创建者自动成为 owner
            db.add(ProjectMember(
                project_id=project.id,
                user_id=users[pd["creator_email"]].id,
                role="owner",
            ))

            # 其他用户作为 member
            for u in users.values():
                if u.id != users[pd["creator_email"]].id:
                    db.add(ProjectMember(
                        project_id=project.id,
                        user_id=u.id,
                        role="member",
                    ))

        print(f"✅ 创建了 {len(projects_data)} 个项目 + 项目成员")

        # ── 3. 穗穗念 10 条 seed 任务 ──
        suisuinian_tasks = [
            {
                "title": "完成本周星座运势稿件",
                "status": "in_progress",
                "priority": "high",
                "assignee_email": "qiqi@qingtian.com",
                "due_date": "07-05",
                "description": "撰写7月第一周12星座运势，含爱情、事业、财运三个维度。字数要求：2000字以上。",
            },
            {
                "title": "文章排版模板优化",
                "status": "todo",
                "priority": "medium",
                "assignee_email": "wang@qingtian.com",
                "due_date": "07-08",
                "description": "优化公众号文章排版模板，适配移动端阅读体验。增加卡片式排版、引用样式优化。",
            },
            {
                "title": "数据分析看板上线",
                "status": "in_progress",
                "priority": "high",
                "assignee_email": "zhao@qingtian.com",
                "due_date": "07-06",
                "description": "完成穗穗念数据分析看板开发，包括阅读量趋势、用户增长、内容表现等模块。",
            },
            {
                "title": "新栏目选题策划",
                "status": "todo",
                "priority": "medium",
                "assignee_email": "liu@qingtian.com",
                "due_date": "07-10",
                "description": "策划一个面向25-35岁职场人群的新栏目《周三下午茶》，内容方向包括职场故事、效率工具、副业经验。",
            },
            {
                "title": "评论区互动功能测试",
                "status": "done",
                "priority": "low",
                "assignee_email": "yuan@qingtian.com",
                "due_date": "06-30",
                "description": "对评论区新功能进行全量回归测试，包括发送、回复、删除、表情等功能。",
            },
            {
                "title": "自动化发布流程文档",
                "status": "todo",
                "priority": "low",
                "assignee_email": "gong@qingtian.com",
                "due_date": "07-12",
                "description": "编写自动化发布流程的使用文档，包括 CI/CD 配置、发布检查清单、回滚流程。",
            },
            {
                "title": "用户反馈收集与整理",
                "status": "in_progress",
                "priority": "medium",
                "assignee_email": "qiqi@qingtian.com",
                "due_date": "07-04",
                "description": "整理6月份所有用户反馈，按功能模块分类，输出改进优先级列表。",
            },
            {
                "title": "SEO 关键词优化方案",
                "status": "todo",
                "priority": "high",
                "assignee_email": "liu@qingtian.com",
                "due_date": "07-07",
                "description": "对穗穗念现有文章进行 SEO 分析，制定关键词优化方案，提升搜索引擎收录率。",
            },
            {
                "title": "后端接口性能优化",
                "status": "done",
                "priority": "high",
                "assignee_email": "zhao@qingtian.com",
                "due_date": "06-28",
                "description": "对穗穗念 API 进行性能分析，优化慢查询，引入缓存机制。已完成首页接口从 800ms 优化到 120ms。",
            },
            {
                "title": "Weekly 数据报告模板",
                "status": "done",
                "priority": "medium",
                "assignee_email": "yuan@qingtian.com",
                "due_date": "06-29",
                "description": "设计 Weekly 数据报告模板，包含阅读量、新增关注、转发数等核心指标的可视化展示。",
            },
        ]

        for td in suisuinian_tasks:
            task = Task(
                pid=projects["穗穗念"].id,
                title=td["title"],
                status=td["status"],
                priority=td["priority"],
                assignee_id=users[td["assignee_email"]].id,
                due_date=td["due_date"],
                description=td["description"],
            )
            db.add(task)

        # 更新穗穗念项目进度
        db.flush()
        suisuinian_done = sum(1 for t in suisuinian_tasks if t["status"] == "done")
        projects["穗穗念"].progress = int(suisuinian_done / len(suisuinian_tasks) * 100)

        print(f"✅ 穗穗念：创建了 {len(suisuinian_tasks)} 条任务")

        # ── 4. 小红书运营 10 条 seed 任务 ──
        xiaohongshu_tasks = [
            {
                "title": "7月内容日历排期",
                "status": "in_progress",
                "priority": "high",
                "assignee_email": "qiqi@qingtian.com",
                "due_date": "07-03",
                "description": "制定7月份小红书笔记发布日历，每周 3-4 篇，覆盖美妆、生活、职场等话题。",
            },
            {
                "title": "爆款笔记模板设计",
                "status": "todo",
                "priority": "high",
                "assignee_email": "wang@qingtian.com",
                "due_date": "07-08",
                "description": "设计 5 套爆款笔记模板，含封面图、标题格式、正文结构、标签组合的标准化方案。",
            },
            {
                "title": "竞品账号分析报告",
                "status": "in_progress",
                "priority": "medium",
                "assignee_email": "yuan@qingtian.com",
                "due_date": "07-06",
                "description": "分析 10 个同类账号的运营策略，包括发文频率、内容风格、互动率、涨粉速度。",
            },
            {
                "title": "粉丝互动活动策划",
                "status": "todo",
                "priority": "medium",
                "assignee_email": "liu@qingtian.com",
                "due_date": "07-15",
                "description": "策划 7 月粉丝互动活动，建议形式：抽奖、话题讨论、UGC 征集。预算控制在 500 元以内。",
            },
            {
                "title": "笔记数据复盘（6月）",
                "status": "done",
                "priority": "medium",
                "assignee_email": "qiqi@qingtian.com",
                "due_date": "07-01",
                "description": "对6月份发布的 15 篇笔记进行数据复盘，分析曝光量、点击率、互动率的 TOP3 共性。",
            },
            {
                "title": "话题标签数据库建设",
                "status": "todo",
                "priority": "low",
                "assignee_email": "gong@qingtian.com",
                "due_date": "07-20",
                "description": "建立小红书话题标签数据库，按垂直领域分类，记录每个标签的搜索量和竞争度。",
            },
            {
                "title": "视频笔记拍摄计划",
                "status": "todo",
                "priority": "high",
                "assignee_email": "qiqi@qingtian.com",
                "due_date": "07-10",
                "description": "制定 7 月视频笔记拍摄计划，每周 1 条短视频，内容方向：好物分享、Vlog、教程类。",
            },
            {
                "title": "品牌合作洽谈跟进",
                "status": "in_progress",
                "priority": "high",
                "assignee_email": "liu@qingtian.com",
                "due_date": "07-05",
                "description": "跟进 3 个潜在品牌合作方的洽谈进度，准备合作提案 PPT。",
            },
            {
                "title": "封面图 A/B 测试",
                "status": "done",
                "priority": "medium",
                "assignee_email": "wang@qingtian.com",
                "due_date": "06-27",
                "description": "对 3 篇笔记进行封面图 A/B 测试，结论：人物出镜+文字叠加的封面点击率高出 35%。",
            },
            {
                "title": "评论区话术库建设",
                "status": "done",
                "priority": "low",
                "assignee_email": "yuan@qingtian.com",
                "due_date": "06-30",
                "description": "整理常用评论区回复话术，按场景分类（好评回复、差评处理、常见问题解答），共 50 条。",
            },
        ]

        for td in xiaohongshu_tasks:
            task = Task(
                pid=projects["小红书运营"].id,
                title=td["title"],
                status=td["status"],
                priority=td["priority"],
                assignee_id=users[td["assignee_email"]].id,
                due_date=td["due_date"],
                description=td["description"],
            )
            db.add(task)

        # 更新小红书项目进度
        db.flush()
        xhs_done = sum(1 for t in xiaohongshu_tasks if t["status"] == "done")
        projects["小红书运营"].progress = int(xhs_done / len(xiaohongshu_tasks) * 100)

        print(f"✅ 小红书运营：创建了 {len(xiaohongshu_tasks)} 条任务")

        db.commit()
        print("\n🎉 Seed 数据填充完成！")
        print(f"   - 用户: {len(agents)} 个")
        print(f"   - 项目: {len(projects_data)} 个")
        print(f"   - 任务: {len(suisuinian_tasks) + len(xiaohongshu_tasks)} 条")
        print(f"   - 默认密码: 123456")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed 失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
