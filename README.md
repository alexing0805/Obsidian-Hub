# Obsidian Hub

一个面向平板的家庭中控面板。

后端使用 FastAPI，对接 Home Assistant 和 Music Assistant；前端使用 Vue 3 + Vite，提供灯光、空调、窗帘、天气、低电量、离线设备和音乐播放的统一控制界面。

## 当前功能

- Home Assistant
  - 获取实体列表：`GET /api/ha/entities`
  - 获取汇总信息：`GET /api/ha/summary`
  - 调用服务：`POST /api/ha/service`
- Music Assistant
  - 获取当前状态：`GET /api/ma/state`
  - 发送命令：`POST /api/ma/cmd`
  - 切换当前播放器：`POST /api/ma/switch_player`
- 前端界面
  - 户型图布局与拖拽定位
  - 灯光、空调、窗帘快捷控制
  - 天气、温湿度、低电量、离线设备卡片
  - Music Assistant 播放控制
  - WebSocket 实时同步：`WS /api/ws`
- 设置持久化
  - 配置保存在 `backend/settings.json`
  - 支持天气实体、温湿度实体、侧边栏显示项、户型图背景和实体布局

## 项目结构

```text
aura-grid-docker/
├─ backend/
│  ├─ main.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  ├─ style.css
│  │  └─ components/
│  ├─ package.json
│  └─ vite.config.js
├─ Dockerfile
├─ docker-compose.yml
├─ .env.example
└─ README.md
```

## 环境变量

参考 `.env.example`。

关键变量：

- `HA_URL`
- `HA_TOKEN`
- `MA_URL`
- `MA_TOKEN`
- `HOST`
- `PORT`
- `MA_COMMAND_TIMEOUT`
- `CORS_ALLOW_ORIGINS`

说明：

- `CORS_ALLOW_ORIGINS` 使用逗号分隔，例如 `http://localhost:8000,http://localhost:5173`
- `HA_REFRESH_INTERVAL` 和 `MA_REFRESH_INTERVAL` 已经迁移为运行时设置，优先从 `backend/settings.json` 读取，不再建议依赖环境变量

## 本地开发

后端：

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

开发模式下：

- 前端默认运行在 `http://localhost:5173`
- Vite 已经把 `/api` 和 WebSocket 代理到 `http://localhost:8000`

## Docker 运行

准备配置：

```bash
cp .env.example .env
```

启动：

```bash
docker compose up -d --build
```

访问：

- `http://localhost:8000`

说明：

- `backend/settings.json` 会通过 volume 持久化
- `docker-compose.yml` 默认使用本地 `Dockerfile` 构建，而不是直接拉远程镜像

## API 概览

- `GET /api/status`
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/ha/entities`
- `GET /api/ha/summary`
- `POST /api/ha/service`
- `GET /api/ma/state`
- `POST /api/ma/cmd`
- `POST /api/ma/switch_player`
- `WS /api/ws`

## 已知实现说明

- Music Assistant 的状态同步采用“长连接 + 定时刷新 + WebSocket 广播”组合，而不是只依赖服务端事件推送
- 浏览器侧不会再收到明文 HA/MA token；设置接口仅返回掩码值
