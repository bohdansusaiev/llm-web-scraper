# LLM-Scraper

Система адаптивного збору наукових даних на основі великих мовних моделей (LLM).

## Опис

Веб-застосунок для автоматизованого пошуку, фільтрації та структурованого вилучення інформації з наукових публікацій. Підтримує три режими роботи:

- **Дослідницький** — паралельний пошук статей у п'яти відкритих академічних базах (OpenAlex, Semantic Scholar, arXiv, CORE, Crossref), оцінка релевантності через LLM, глибоке вилучення методології, висновків та ключових слів
- **Універсальний збирач** — вилучення структурованих даних з довільної веб-сторінки за описаною користувачем схемою
- **Бенчмарк** — порівняння LLM-підходу з класичними методами (trafilatura + BeautifulSoup)

## Системні вимоги

| Компонент | Вимога |
|-----------|--------|
| ОС | Linux / macOS / Windows 10+ |
| Python | 3.11 або новіший |
| Node.js | 18 або новіший |
| База даних | SQLite (вбудована у Python, не потребує окремої установки) |

**API-ключі** (безкоштовна реєстрація):
- `DEEPSEEK_API_KEY` — [api-docs.deepseek.com](https://api-docs.deepseek.com/)
- `CORE_API_KEY` *(опціонально)* — [core.ac.uk/services/api](https://core.ac.uk/services/api)

## Встановлення та запуск

```bash
# 1. Клонувати репозиторій
git clone https://github.com/bohdansusaiev/llm-web-scraper.git
cd llm-web-scraper

# 2. Встановити залежності бекенду
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Налаштувати змінні середовища
cp .env.example .env
# Відкрити .env і вказати DEEPSEEK_API_KEY (і за потреби CORE_API_KEY)

# 4. Встановити залежності фронтенду
cd frontend && npm install && cd ..

# 5. Запустити бекенд (термінал 1)
uvicorn app.main:app --reload --port 8000

# 6. Запустити фронтенд (термінал 2)
cd frontend && npm run dev
```

Відкрити у браузері: **http://localhost:5173** → зареєструвати акаунт → розпочати дослідження.

## Бібліотеки та технологічний стек

| Рівень | Технологія |
|--------|-----------|
| Бекенд | Python 3.11, FastAPI, asyncio, Pydantic v2 |
| LLM | DeepSeek API (OpenAI-сумісний інтерфейс) |
| Веб-сканування | Crawl4AI (headless Chromium через Playwright) |
| База даних | SQLite (вбудована) |
| Фронтенд | SvelteKit, TypeScript |
| Класичний baseline | trafilatura, BeautifulSoup4 |
| Наукові API | OpenAlex, Semantic Scholar, arXiv, CORE, Crossref |

## Структура проекту

```
app/
  core/           LLM-рушій: crawler.py, llm_extractor.py, prompts.py
  services/
    discovery/    Клієнти наукових API (openalex, crossref, semantic_scholar, ...)
    extraction/   Оцінка релевантності та глибоке вилучення
    pipeline.py   Головний конвеєр обробки
  routers/        HTTP-ендпоінти FastAPI
  db/             SQLite-шар (schema, catalogs, jobs, cache)
  models/         Pydantic-схеми
frontend/         SvelteKit-застосунок (Research / Scrape / Benchmark / Catalogs)
```
