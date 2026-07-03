# TourHub Tasks

Version: 1.0

Status: Sprint 1

Last Updated: 2026-07-03

---

# Назначение

Этот документ содержит только задачи текущего спринта.

Roadmap проекта хранится отдельно в docs/ROADMAP.md.

После завершения задачи Cursor обязан остановиться и дождаться следующего задания.

Cursor никогда самостоятельно не выбирает следующую задачу.

---

# Правила

- Один Commit = одна задача.
- Один Pull Request = одна законченная задача.
- Каждая задача должна быть полностью завершена.
- Не допускается переход к следующей задаче без подтверждения Product Owner.
- После выполнения задачи Cursor предоставляет полный отчёт.

---

# Sprint 1 — Backend Foundation

## TH-0001 — Backend Skeleton

Статус:

🟡 Ready

---

### Цель

Создать минимальный полностью работоспособный Backend проекта TourHub.

---

### Что необходимо реализовать

- структура backend согласно ARCHITECTURE.md;
- FastAPI приложение;
- app/main.py;
- централизованная регистрация Router;
- lifespan;
- config.py;
- logging.py;
- middleware.py;
- exceptions.py;
- dependencies.py;
- router.py;
- health endpoint;
- Dockerfile;
- .dockerignore;
- pyproject.toml;
- requirements;
- requirements-dev;
- базовая структура tests.

---

### Что НЕ реализовывать

Не создавать:

- пользователей;
- авторизацию;
- JWT;
- SQLAlchemy модели;
- Alembic миграции;
- бизнес-логику;
- Engine;
- Process;
- Contracts;
- Repository;
- Service;
- DTO.

Это будет реализовано отдельными задачами.

---

### Definition of Done

Backend запускается.

GET /

↓

{
    "status": "ok",
    "project": "TourHub"
}

GET /health

↓

{
    "status": "healthy"
}

Swagger доступен.

/redoc доступен.

Docker собирается.

Тест проходит.

---

### После выполнения

Cursor обязан остановиться.

Не выполнять TH-0002.

Ждать следующего задания Product Owner.