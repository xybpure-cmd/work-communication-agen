# 职场沟通 Copilot MVP

这是一个基于 **FastAPI + SQLite + SQLAlchemy + OpenAI API** 的最小可用版本（MVP）。

## 功能

- 表单输入：
  - 收到的消息
  - 联系人（Person）
  - 事项上下文（Matter）
  - 沟通目标
- 一键生成三种中文回复：
  1. 审慎版（prudent）
  2. 简洁版（concise）
  3. 推进版（push-forward）
- 风格调节选项：
  - more formal
  - shorter
  - more tactful
  - more assertive
- 基于联系人 + 事项的简单记忆检索（最近历史回复）
- 保存最终选中的回复到 `reply_history`
- 支持 Markdown 种子数据导入（`data/seeds/`）

## 目录结构

```text
.
├── app/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── schemas.py
│   ├── services.py
│   ├── seed_loader.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── data/
│   └── seeds/
│       ├── people.md
│       └── matters.md
├── .env.example
├── requirements.txt
└── README.md
```

## 快速开始

1. 安装依赖：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
```

3. 初始化种子数据：

```bash
python -m app.seed_loader
```

4. 启动服务：

```bash
uvicorn app.main:app --reload
```

5. 打开浏览器访问：

- http://127.0.0.1:8000

## API

### `POST /generate_reply`

请求体示例：

```json
{
  "person_id": 1,
  "matter_id": 1,
  "incoming_message": "这个需求我们这周能不能上线？",
  "communication_goal": "先稳住预期并给出可执行时间点",
  "modifiers": ["more formal", "more tactful"]
}
```

返回示例：

```json
{
  "prudent": "...",
  "concise": "...",
  "push_forward": "...",
  "memory_context": "..."
}
```

### `POST /save_reply`

保存最终选定的回复至 `reply_history`。

## 说明

- 当前记忆检索策略为：按 `person_id + matter_id` 查询最近 3 条历史。
- 如果没有历史记录，会返回“暂无历史回复记录”。
- 数据库默认文件：`app.db`（项目根目录）。
