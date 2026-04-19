# 运行指南（中文，零技术版）

你只需要按下面 4 步做，就可以跑起来。

## 1) 先填 API Key（最重要）

你需要编辑这个文件：

- `.env.example`

把下面这行里的 `your_openai_api_key` 改成你自己的 Key：

- `OPENAI_API_KEY=your_openai_api_key`

然后把 `.env.example` 复制成 `.env`（文件名必须是 `.env`）。

> 简单理解：程序会从 `.env` 读取你的 Key。

---

## 2) 启动前先装依赖

在项目根目录运行：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3) 导入示例数据并启动

先导入数据：

```bash
python -m app.seed_loader
```

再启动：

```bash
uvicorn app.main:app --reload
```

---

## 4) 浏览器打开哪个页面

打开：

- `http://127.0.0.1:8000`

就是首页表单页面。

---

## 5) 怎么做一次最简单测试

在页面里：

1. 联系人：选 `李敏`（或你自己填的联系人）
2. 事项：选 `客户 A 项目上线准备`（或你自己填的事项）
3. 收到的消息：填「这个需求这周能上线吗？」
4. 沟通目标：填「先稳住预期，再给明确时间点」
5. 点「生成三版回复」

你会看到 3 个结果：
- 审慎版
- 简洁版
- 推进版

如果能看到这 3 个文本框里有内容，说明跑通了。
