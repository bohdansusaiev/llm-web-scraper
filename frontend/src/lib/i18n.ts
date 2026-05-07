import { get } from 'svelte/store';
import { language } from './stores/language';

export function t(key: string): string {
    const lang = get(language);
    const dict = lang === 'ua' ? UA : EN;
    return dict[key] || key;
}

export function lang(): 'en' | 'ua' {
    return get(language);
}

export const UA: Record<string, string> = {
    app_title: "Адаптивний збір веб-інформації",
    app_subtitle: "Будь-який новинний сайт. Структуровані дані. Без налаштувань.",
    try_without_login: "Спробуйте без входу",
    scrape_btn: "Скрапити",
    scrape_btn_loading: "Аналізую...",
    url_label: "URL статті",
    url_placeholder: "https://example.com/article",
    no_title: "Заголовок не знайдено",
    author: "Автор",
    date: "Дата",
    summary: "Короткий зміст",
    no_summary: "Короткий зміст відсутній",
    article_type: "Тип статті",
    key_points: "Ключові моменти",
    translated: "Перекладено",
    error_url: "Введіть коректний URL.",
    error_connect: "Не вдалося підключитися до сервера.",
    error_generic: "Помилка: {}",

    login_title: "Вхід",
    register_title: "Реєстрація",
    username: "Ім'я користувача",
    password: "Пароль",
    login_btn: "Увійти",
    register_btn: "Зареєструватися",
    logout_btn: "Вийти",
    no_account: "Ще немає акаунту?",
    has_account: "Вже маєте акаунт?",
    register_link: "Зареєструватися",
    login_link: "Увійти",
    register_success: "Реєстрація успішна! Увійдіть.",
    login_failed: "Невірне ім'я користувача або пароль",
    register_failed: "Користувач з таким іменем вже існує",

    nav_dashboard: "Огляд",
    nav_scraper: "Скрапер",
    nav_collections: "Колекції",
    nav_history: "Історія",
    nav_about: "Про проект",
    welcome: "Ласкаво просимо, {}",

    dashboard_title: "Огляд",
    dashboard_total_articles: "Всього статей",
    dashboard_total_collections: "Колекцій",
    dashboard_total_sources: "Джерел",
    dashboard_recent: "Нещодавні статті",
    dashboard_empty: "Ще немає статей. Додайте джерела або скрапте вручну.",
    dashboard_by_type: "Статті за типом",

    scraper_title: "Скрапер",
    scraper_desc: "Вставте URL новинної статті та отримайте структуровані дані, витягнуті ШІ.",
    scraper_quick: "Швидкий скрапінг",
    scraper_to_collection: "Скрапити до колекції",
    scraper_again: "Скрапити знову",
    scraper_result: "Результат",

    collections_title: "Колекції",
    collections_new: "Нова колекція",
    collections_name: "Назва колекції",
    collections_create: "Створити",
    collections_empty: "Немає колекцій. Створіть першу.",
    collections_delete: "Видалити",
    collections_sources: "джерел",
    collections_articles: "статей",

    sources_title: "Джерела",
    sources_add: "Додати джерело",
    sources_url: "URL джерела",
    sources_name: "Назва (необов'язково)",
    sources_interval: "Інтервал",
    sources_manual: "Вручну",
    sources_hourly: "Щогодини",
    sources_daily: "Щодня",
    sources_weekly: "Щотижня",
    sources_add_btn: "Додати",
    sources_empty: "Немає джерел у цій колекції.",
    sources_scrape_now: "Скрапити",
    sources_scrape_all: "Скрапити всі",
    sources_status_ok: "OK",
    sources_status_error: "Помилка",
    sources_status_pending: "Очікує",
    sources_batch_progress: "Скрапінг {} з {}...",
    sources_batch_done: "Готово. {} успішно, {} з помилками.",
    sources_articles: "Статті джерела",

    history_title: "Історія",
    history_empty: "Історія порожня",
    history_filter_type: "Тип",
    history_filter_all: "Всі типи",
    history_search: "Пошук...",
    history_results: "Результатів: {}",
    history_no_results: "Нічого не знайдено",

    export_json: "JSON",
    export_csv: "CSV",
    saved_at: "Збережено",
    show_details: "Деталі",
    delete: "Видалити",
    back: "Назад",
    cancel: "Скасувати",
    confirm: "Підтвердити",
    collection_select: "Оберіть колекцію",
    type_all: "Всі типи",
    no_collection: "Без колекції",
    saved: "Збережено!",
    collapse: "згорнути",

    about_title: "Принцип роботи",
    about_hero: "Будь-який новинний сайт. Структуровані дані. Нуль налаштувань.",
    about_value_prop: "Традиційні парсери ламаються при зміні дизайну сайту. NewsScraper використовує ШІ для смислового розуміння сторінки — без CSS-селекторів, без ручного налаштування.",
    about_how_title: "Як це працює",
    about_how_1_title: "Ви вставляєте URL",
    about_how_1_desc: "Посилання на будь-яку новинну статтю — BBC, Reuters, Українська правда, The Guardian.",
    about_how_2_title: "ШІ читає сторінку",
    about_how_2_desc: "Crawl4AI завантажує контент, DeepSeek аналізує його семантично — як людина.",
    about_how_3_title: "Отримуєте структуровані дані",
    about_how_3_desc: "Заголовок, автор, дата, короткий зміст, ключові факти, тип статті — готовий JSON.",
    about_compare_title: "Традиційний підхід проти адаптивного",
    about_compare_old: "CSS-селектори ламаються, коли сайт змінює верстку. Кожен сайт потребує окремого налаштування.",
    about_compare_new: "LLM читає контент семантично. Працює на будь-якому сайті без змін. Стійкий до редизайну.",
    about_features_title: "Можливості",
    about_feature_1: "Адаптивне витягування даних через LLM (Crawl4AI + DeepSeek V4)",
    about_feature_2: "Автоматичне визначення типу статті (новина, аналіз, думка, інтерв'ю, репортаж)",
    about_feature_3: "Переклад вмісту на українську або англійську мову",
    about_feature_4: "Колекції для групування джерел за темами",
    about_feature_5: "Запланований періодичний скрапінг джерел",
    about_feature_6: "Пошук та фільтрація за типом, датою, колекцією",
    about_feature_7: "Пакетний скрапінг кількох URL одночасно",
    about_feature_8: "Експорт результатів у JSON та CSV",
    about_tech_title: "Технології",
    about_tech_python: "Python + FastAPI — REST API сервер, асинхронна обробка запитів",
    about_tech_crawl4ai: "Crawl4AI + Chromium — завантаження та рендеринг сторінок",
    about_tech_deepseek: "DeepSeek V4 — семантичний аналіз та витягування даних",
    about_tech_svelte: "SvelteKit — швидкий реактивний фронтенд з темною/світлою темою",
    about_tech_sqlite: "SQLite — легковажна база даних без зовнішніх залежностей",
    about_author_title: "Дипломний проект",
    about_author_name: "Сусаєв Богдан Вадимович",
    about_author_group: "ТВ-21",
    about_author_institute: "Навчально-науковий інститут атомної та теплової енергетики",
    about_author_specialty: "Інженерія програмного забезпечення",
    about_purpose: "Дослідження використання великих мовних моделей для адаптивного збору та обробки веб-даних.",
    about_relevance: "Зі зростанням обсягів відкритих даних потрібен гнучкий інструмент збору інформації, який не залежить від структури сайту.",

    about_adaptivity_title: "У чому полягає адаптивність?",
    about_adaptivity_text: ""
        + "Звичайні веб-скрапери збирають дані за жорсткими вказівками — CSS-селекторами "
        + "на кшталт «візьми текст із елемента з класом .news-title». Варто сайту змінити "
        + "дизайн — і всі вказівки перестають працювати.\n\n"

        + "Ця програма замість жорстких інструкцій використовує великі мовні моделі для "
        + "смислового розуміння сторінки. Вона не шукає «текст у класі .news-title» — "
        + "вона читає сторінку як людина й розуміє: «ось заголовок, ось автор, ось дата». "
        + "Це забезпечує:\n\n"

        + "1. Стійкість до змін верстки. LLM аналізує зміст, а не HTML-структуру. "
        + "Якщо сайт змінить CSS-класи, скрапер не зламається.\n\n"

        + "2. Універсальність джерел. Одна програма працює на будь-якому новинному сайті — "
        + "від BBC до Української правди — без доналаштування.\n\n"

        + "3. Контекстне розуміння. LLM розуміє, що «Ілон Маск», «засновник Tesla» і "
        + "«власник Twitter» — одна людина, навіть якщо вжито різні формулювання.\n\n"

        + "4. Інтелектуальне визначення типу. Система автоматично визначає, чи є стаття "
        + "новиною, аналізом, думкою або інтерв'ю, і адаптує витягування даних.",

    about_tech_detail_python: "Python + FastAPI. Мова програмування та веб-фреймворк. Забезпечує основну логіку застосунку, асинхронність, реалізує REST API для прийому запитів від фронтенду та виклику логіки скрапінгу.",
    about_tech_detail_crawl4ai: "Crawl4AI. Бібліотека веб-скрапінгу. Керує браузером Chromium для завантаження та рендерингу сторінок і забезпечує LLM-стратегію витягування даних.",
    about_tech_detail_deepseek: "DeepSeek V4. Велика мовна модель. Відповідає за семантичний аналіз, витягування полів, визначення типу статті, переклад та узагальнення контенту.",
    about_tech_detail_svelte: "SvelteKit. Фреймворк для фронтенду. Забезпечує швидкий реактивний інтерфейс з темною/світлою темою та підтримкою двох мов.",
    about_tech_detail_sqlite: "SQLite. Легковажна база даних. Зберігає облікові записи користувачів, колекції, джерела та історію скрапінгу без зовнішніх залежностей.",

    interview: "Інтерв'ю",
    news: "Новина",
    opinion: "Думка",
    analysis: "Аналіз",
    report: "Репортаж",
    other: "Інше",
};

export const EN: Record<string, string> = {
    app_title: "Adaptive Web Information Collection",
    app_subtitle: "Any news website. Structured data. Zero configuration.",
    try_without_login: "Try without login",
    scrape_btn: "Scrape",
    scrape_btn_loading: "Analyzing...",
    url_label: "Article URL",
    url_placeholder: "https://example.com/article",
    no_title: "No Title Found",
    author: "Author",
    date: "Date",
    summary: "Summary",
    no_summary: "No summary available.",
    article_type: "Article Type",
    key_points: "Key Points",
    translated: "Translated",
    error_url: "Please enter a valid URL.",
    error_connect: "Cannot connect to server.",
    error_generic: "Error: {}",

    login_title: "Login",
    register_title: "Register",
    username: "Username",
    password: "Password",
    login_btn: "Login",
    register_btn: "Register",
    logout_btn: "Logout",
    no_account: "Don't have an account?",
    has_account: "Already have an account?",
    register_link: "Register",
    login_link: "Login",
    register_success: "Registration successful! Please log in.",
    login_failed: "Invalid username or password",
    register_failed: "Username already exists",

    nav_dashboard: "Dashboard",
    nav_scraper: "Scraper",
    nav_collections: "Collections",
    nav_history: "History",
    nav_about: "About",
    welcome: "Welcome, {}",

    dashboard_title: "Dashboard",
    dashboard_total_articles: "Total Articles",
    dashboard_total_collections: "Collections",
    dashboard_total_sources: "Sources",
    dashboard_recent: "Recent Articles",
    dashboard_empty: "No articles yet. Add sources or scrape manually.",
    dashboard_by_type: "Articles by Type",

    scraper_title: "Scraper",
    scraper_desc: "Paste a news article URL and get structured data extracted by AI.",
    scraper_quick: "Quick Scrape",
    scraper_to_collection: "Scrape to Collection",
    scraper_again: "Scrape Again",
    scraper_result: "Result",

    collections_title: "Collections",
    collections_new: "New Collection",
    collections_name: "Collection Name",
    collections_create: "Create",
    collections_empty: "No collections yet. Create your first one.",
    collections_delete: "Delete",
    collections_sources: "sources",
    collections_articles: "articles",

    sources_title: "Sources",
    sources_add: "Add Source",
    sources_url: "Source URL",
    sources_name: "Name (optional)",
    sources_interval: "Interval",
    sources_manual: "Manual",
    sources_hourly: "Hourly",
    sources_daily: "Daily",
    sources_weekly: "Weekly",
    sources_add_btn: "Add",
    sources_empty: "No sources in this collection.",
    sources_scrape_now: "Scrape Now",
    sources_scrape_all: "Scrape All",
    sources_status_ok: "OK",
    sources_status_error: "Error",
    sources_status_pending: "Pending",
    sources_batch_progress: "Scraping {} of {}...",
    sources_batch_done: "Done. {} succeeded, {} failed.",
    sources_articles: "Source Articles",

    history_title: "History",
    history_empty: "History is empty",
    history_filter_type: "Type",
    history_filter_all: "All types",
    history_search: "Search...",
    history_results: "Results: {}",
    history_no_results: "Nothing found",

    export_json: "JSON",
    export_csv: "CSV",
    saved_at: "Saved at",
    show_details: "Details",
    delete: "Delete",
    back: "Back",
    cancel: "Cancel",
    confirm: "Confirm",
    collection_select: "Select Collection",
    type_all: "All types",
    no_collection: "No Collection",
    saved: "Saved!",
    collapse: "collapse",

    about_title: "How it works",
    about_hero: "Any news website. Structured data. Zero configuration.",
    about_value_prop: "Traditional scrapers break when a site changes its design. NewsScraper uses AI for semantic understanding of page content — no CSS selectors, no manual setup.",
    about_how_title: "How it works",
    about_how_1_title: "You paste a URL",
    about_how_1_desc: "Link to any news article — BBC, Reuters, The Guardian, or any other source.",
    about_how_2_title: "AI reads the page",
    about_how_2_desc: "Crawl4AI loads the content, DeepSeek analyzes it semantically — like a human would.",
    about_how_3_title: "You get structured data",
    about_how_3_desc: "Title, author, date, summary, key facts, article type — ready-to-use JSON.",
    about_compare_title: "Traditional vs Adaptive",
    about_compare_old: "CSS selectors break when the site changes layout. Each site needs separate configuration.",
    about_compare_new: "LLM reads content semantically. Works on any site without changes. Layout-change resilient.",
    about_features_title: "Features",
    about_feature_1: "Adaptive data extraction via LLM (Crawl4AI + DeepSeek V4)",
    about_feature_2: "Automatic article type detection (news, analysis, opinion, interview, report)",
    about_feature_3: "Content translation to Ukrainian or English",
    about_feature_4: "Collections for grouping sources by topic",
    about_feature_5: "Scheduled recurring scraping of sources",
    about_feature_6: "Search and filter by type, date, and collection",
    about_feature_7: "Batch scraping of multiple URLs at once",
    about_feature_8: "Export results to JSON and CSV",
    about_tech_title: "Technology Stack",
    about_tech_python: "Python + FastAPI — REST API server, async request handling",
    about_tech_crawl4ai: "Crawl4AI + Chromium — page loading and rendering",
    about_tech_deepseek: "DeepSeek V4 — semantic analysis and data extraction",
    about_tech_svelte: "SvelteKit — fast reactive frontend with dark/light theme",
    about_tech_sqlite: "SQLite — lightweight database with zero external dependencies",
    about_author_title: "Diploma Project",
    about_author_name: "Bohdan Susaiev",
    about_author_group: "TV-21",
    about_author_institute: "Institute of Atomic and Thermal Energy",
    about_author_specialty: "Software Engineering",
    about_purpose: "Research on using Large Language Models for adaptive web data collection and processing.",
    about_relevance: "As open data volumes grow, a flexible information collection tool independent of site structure is needed.",

    about_adaptivity_title: "What Makes It Adaptive?",
    about_adaptivity_text: ""
        + "Traditional web scrapers collect data using rigid CSS selectors — instructions "
        + "like \"get the text from the element with class .news-title\". If the website "
        + "changes its design, all these instructions break.\n\n"

        + "This application uses Large Language Models instead of rigid instructions for "
        + "semantic understanding of page content. It doesn't look for \"text in class "
        + ".news-title\" — it reads the page like a human and understands: \"this is the "
        + "headline, this is the author, this is the date\". This provides:\n\n"

        + "1. Resilience to layout changes. The LLM analyzes content, not HTML structure. "
        + "If a website changes its CSS classes or element order, the scraper does not break.\n\n"

        + "2. Source universality. The same program works on any news website — from BBC "
        + "to The Guardian — without per-site configuration.\n\n"

        + "3. Contextual understanding. The LLM understands that \"Elon Musk\", "
        + "\"Tesla founder\", and \"Twitter owner\" refer to the same person, even when "
        + "different phrasings are used in the text.\n\n"

        + "4. Intelligent type detection. The system automatically determines whether an "
        + "article is news, analysis, opinion, or interview, and adapts data extraction accordingly.",

    about_tech_detail_python: "Python + FastAPI. Programming language and web framework. Provides core application logic, async support, and implements the REST API to receive frontend requests and invoke scraping logic.",
    about_tech_detail_crawl4ai: "Crawl4AI. Web scraping library. Manages the Chromium browser for page rendering and provides the LLM extraction strategy.",
    about_tech_detail_deepseek: "DeepSeek V4. Large Language Model. Handles semantic analysis, field extraction, article type detection, translation, and content summarization.",
    about_tech_detail_svelte: "SvelteKit. Frontend framework. Provides a fast, reactive interface with dark/light theme and bilingual support.",
    about_tech_detail_sqlite: "SQLite. Lightweight database. Stores user accounts, collections, sources, and scraping history with zero external dependencies.",

    interview: "Interview",
    news: "News",
    opinion: "Opinion",
    analysis: "Analysis",
    report: "Report",
    other: "Other",
};
