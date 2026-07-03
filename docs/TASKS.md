# TourHub Tasks

Version: 1.0

Status: Active

Last Updated: 2026-07-03

---

# Правила

- Каждая задача должна быть законченной.
- Один Commit = одна задача.
- После выполнения задача отмечается как выполненная.
- Cursor не имеет права переходить к следующей задаче без явного разрешения.
- После выполнения каждой задачи Cursor обязан предоставить отчёт:
  - что сделано;
  - какие файлы изменены;
  - какие решения приняты;
  - как проверить результат.

---

# Milestone 1 — Foundation

## Epic 1. Infrastructure

- [ ] T1. Создать Backend Skeleton
- [ ] T2. Настроить Docker для Backend
- [ ] T3. Подключить PostgreSQL
- [ ] T4. Настроить Alembic
- [ ] T5. Настроить конфигурацию приложения (Pydantic Settings)
- [ ] T6. Настроить логирование
- [ ] T7. Настроить middleware
- [ ] T8. Настроить обработку ошибок
- [ ] T9. Healthcheck `/health`
- [ ] T10. Базовые тесты Backend

## Epic 2. Authentication

- [ ] T11. Модуль auth
- [ ] T12. JWT
- [ ] T13. RBAC (Guest / Instructor / Verified Instructor / Admin)

## Epic 3. Organizations

- [ ] T14. Organization
- [ ] T15. Membership пользователя в организации

## Epic 4. Projects

- [ ] T16. Создание проекта
- [ ] T17. Dashboard проекта
- [ ] T18. Жизненный цикл проекта

---

# Milestone 2 — Food Domain

## Epic 5. Products

- [ ] T19. Product
- [ ] T20. Package
- [ ] T21. Purchase Option

## Epic 6. Recipes

- [ ] T22. Dish
- [ ] T23. Recipe
- [ ] T24. Versioning рецептов
- [ ] T25. Ingredient
- [ ] T26. Calculation Strategy

## Epic 7. Meal Planner

- [ ] T27. Planner Wizard
- [ ] T28. Любимые блюда
- [ ] T29. Исключённые блюда
- [ ] T30. Генерация меню

---

# Milestone 3 — Engines

## Epic 8. Engines

- [ ] T31. Planner Engine
- [ ] T32. Calculation Engine
- [ ] T33. Package Engine
- [ ] T34. Equipment Engine

## Epic 9. Processes

- [ ] T35. Prepare Project Process
- [ ] T36. Shopping Process
- [ ] T37. Export Process

---

# Milestone 4 — Documents

## Epic 10. Documents

- [ ] T38. PDF
- [ ] T39. Excel
- [ ] T40. Print View

---

# Milestone 5 — Warehouse

## Epic 11. Equipment

- [ ] T41. Equipment
- [ ] T42. Warehouse
- [ ] T43. Equipment Reservation

---

# Milestone 6 — Knowledge

## Epic 12. Knowledge Base

- [ ] T44. Comments
- [ ] T45. Notes
- [ ] T46. Attachments
- [ ] T47. Object History

---

# Milestone 7 — ERP

## Epic 13. Routes

- [ ] T48. Route Cards
- [ ] T49. Contractors
- [ ] T50. GPX

## Epic 14. Analytics

- [ ] T51. Reports
- [ ] T52. Statistics
- [ ] T53. Budget