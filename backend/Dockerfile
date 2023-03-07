FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN sudo apt-get update && \
    sudo apt install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0:8000" ]
