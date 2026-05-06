FROM mcr.microsoft.com/playwright/python:jammy

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt
RUN python3 -m playwright install chromium 2>&1

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
