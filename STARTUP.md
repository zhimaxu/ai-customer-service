# 启动指南

## 方式一：开发模式（推荐）

### 1. 启动后端

> **注意**：虚拟环境在 `backend/.venv` 中，需在 `backend/` 目录下用 `py` 命令创建和激活。

```bash
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端运行在 `http://localhost:8000`
API 文档在 `http://localhost:8000/api/docs`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`

Vite 已配置代理，所有 `/api` 请求自动转发到 `http://localhost:8000`

### 3. 访问

打开 `http://localhost:5173` → 登录页 → 点击登录

---

## 方式二：Docker 一键启动

```bash
docker compose up --build
```

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:80 |
| 后端 | http://localhost:8000 |
| MySQL | localhost:3306 |
| Qdrant | localhost:6333 |
| Redis | localhost:6379 |

---

## 前提条件

启动前需要：

- **MySQL** 已运行（Docker 或本地），默认连接 `localhost:3306`，用户名 `root`，密码 `root`
- **Qdrant** 已运行（Docker 或本地），默认连接 `localhost:6333`
- Agnes AI API Key 已配置（默认值在 `backend/app/core/config.py`）

### 启动 MySQL（Docker）

```bash
docker run -d --name ai-cs-mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.4.10
```

### 启动 Qdrant（Docker）

```bash
docker run -d --name ai-cs-qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 仅启动基础设施

如果只用后端 + 前端开发调试，可单独启动基础设施：

```bash
docker compose up mysql qdrant redis
```

然后在两个新终端分别启动后端和前端（方式一）。
