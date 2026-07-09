FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# copy only backend project files
COPY pyproject.toml /app/
COPY app /app/app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatch

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
