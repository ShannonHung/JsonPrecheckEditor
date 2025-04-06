# 使用輕量級的 Python 基礎鏡像
FROM python:3.11-slim

# 設定工作目錄為 /app
WORKDIR /app

# 複製當前資料夾（除了 .dockerignore 排除的檔案）到容器中的 /app 資料夾
COPY . .

# 設定環境變數，避免在容器內部有提示（例如 pip 安裝時）
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安裝 requirements.txt 中列出的所有依賴
RUN pip install --no-cache-dir -r requirements.txt

# 開放容器的 4000 端口
EXPOSE 4000

# 設定容器啟動時執行的指令
CMD ["python", "app.py"]
