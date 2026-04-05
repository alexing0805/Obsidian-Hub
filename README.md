# Obsidian Hub

面向平板的智能家居控制面板，后端对接 Home Assistant（HA）与 Music Assistant（MA），前端提供 Obsidian Hub 风格控制界面。

## 当前已实现

- HA 集成
- 获取全部实体（`/api/ha/entities`）
- 获取摘要信息（温湿度、天气、设备统计）（`/api/ha/summary`）
- 调用 HA 服务（`/api/ha/service`）

- MA 集成
- 后端维持 MA WebSocket 长连接并认证
- 拉取队列和播放器状态（`/api/ma/state`）
- 发送 MA 命令（`/api/ma/cmd`）
- 采用稳定轮询刷新（默认 5 秒）+ 前端 WS 推送

- 前端
- 动态读取真实灯光实体，不再硬编码
- 灯光点位可点击控制
- 天气、温湿度、设备统计卡片
- Music Assistant 播放控制、进度拖拽、音量控制、随机/循环
- 与后端 `/api/ws` 实时同步状态

## 项目结构

```text
obsidian-hub/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── style.css
│   │   └── components/
│   │       └── MusicAssistantPlayer.vue
│   ├── package.json
│   └── vite.config.js
├── Dockerfile
├── docker-compose.yml
├── .env
└── .env.example
```

## 环境变量

示例见 `.env.example`。

关键项：

- `HA_URL`：例如 `http://192.168.100.50:8123`
- `HA_TOKEN`：HA Long-Lived Access Token
- `MA_URL`：例如 `ws://192.168.100.50:8095/ws`
- `MA_TOKEN`：MA 长期令牌
- `HA_REFRESH_INTERVAL`：HA 轮询秒数（默认 15）
- `MA_REFRESH_INTERVAL`：MA 轮询秒数（默认 5）

## 运行方式

### Docker

```bash
docker-compose up -d --build
```

访问：`http://localhost:8000`

### 本地开发

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

前端开发服务器默认 `http://localhost:5173`，已配置 `/api` 和 WebSocket 代理到 `http://localhost:8000`。

## API 简要

- `GET /api/status`：后端连接状态
- `GET /api/ha/entities?domain=light`：实体列表（可按 domain 过滤）
- `GET /api/ha/summary`：摘要统计
- `POST /api/ha/service`：调用 HA 服务
- `GET /api/ma/state`：MA 当前状态
- `POST /api/ma/cmd`：发送 MA 命令
- `WS /api/ws`：推送 `init / ha_state / ma_state / ma_event`

## 说明

部分 MA 实例在当前版本下不会稳定推送全量状态事件，因此后端采用“长连接 + 定时刷新 + WS 广播”的方式保证前端状态可靠更新。
