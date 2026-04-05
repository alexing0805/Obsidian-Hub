# 多阶段构建：先构建前端
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# 后端镜像
FROM python:3.11-slim
WORKDIR /app

# 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 环境变量默认值
ENV HA_URL=http://homeassistant.local:8123
ENV HA_TOKEN=
ENV MA_URL=ws://192.168.100.50:8095/ws
ENV MA_TOKEN=
ENV HOST=0.0.0.0
ENV PORT=8000

# 暴露端口
EXPOSE 8000

# 启动后端
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
