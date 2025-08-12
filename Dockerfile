FROM python:3.9-slim

WORKDIR /app

COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

COPY . .

EXPOSE 8000

CMD ["python", "MASTER_LAUNCHER.bat"]