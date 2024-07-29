# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim
# 设置工作目录
WORKDIR /app
# 将当前目录内容复制到容器的 /app 中
COPY ./vecmul.py /app
COPY ./vecmul_service.py /app
COPY ./requirements.txt /app
# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt
# 让端口 8001 可供此容器外的环境使用
EXPOSE 8002
# 运行 app.py
CMD ["uvicorn", "vecmul_service:app", "--host", "0.0.0.0", "--port", "8002"]
