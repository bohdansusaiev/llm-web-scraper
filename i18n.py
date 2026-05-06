UA = {
    "app_title": "Адаптивний збір веб-інформації з використанням LLM",
    "subtitle": "Введіть URL новини, і LLM витягне структуровану інформацію",
    "url_label": "URL новини",
    "url_placeholder": "https://example.com/article",
    "scrape_btn": "Почати адаптивний скрапінг",
    "spinner": "LLM аналізує сторінку... Зачекайте.",
    "no_title": "Заголовок не знайдено",
    "author": "Автор",
    "date": "Дата",
    "summary": "Опис",
    "no_summary": "Опис відсутній",
    "no_image": "Зображення недоступне",
    "error_url": "Будь ласка, введіть коректний URL.",
    "error_connect": "Не вдалося підключитися до бекенду. Переконайтеся, що сервер працює на порту 8000.",
    "error_generic": "Помилка запиту: {}",
    "footer": "Створено з Crawl4AI + DeepSeek + FastAPI + Streamlit",
    "login_title": "Вхід",
    "login_page_title": "Вхід в систему",
    "register_title": "Реєстрація",
    "register_page_title": "Створити акаунт",
    "username": "Ім'я користувача",
    "password": "Пароль",
    "login_btn": "Увійти",
    "register_btn": "Зареєструватися",
    "logout_btn": "Вийти",
    "no_account": "Ще немає акаунту?",
    "has_account": "Вже маєте акаунт?",
    "register_link": "Зареєструватися",
    "login_link": "Увійти",
    "history_title": "Історія",
    "history_empty": "Історія порожня",
    "export_json": "Експортувати JSON",
    "export_csv": "Експортувати CSV",
    "nav_scraper": "Скрапер",
    "nav_history": "Історія",
    "language": "Мова",
    "welcome": "Ласкаво просимо, {}",
    "register_success": "Реєстрація успішна! Увійдіть.",
    "login_failed": "Невірне ім'я користувача або пароль",
    "register_failed": "Користувач з таким іменем вже існує",
    "scrape_again": "Скрапити знову",
    "saved_at": "Збережено",
    "result_title": "Результат скрапінгу",
    "article_type": "Тип статті",
    "key_points": "Ключові моменти",
    "interview": "Інтерв'ю",
    "news": "Новина",
    "opinion": "Думка",
    "other": "Інше",
    "login_required": "Увійдіть або зареєструйтесь, щоб використовувати скрапер.",
    "show_details": "Переглянути результат",
    "translated": "Перекладено",
    "nav_about": "Про програму",
    "about_title": "Про програму",
    "about_adaptivity_title": "У чому полягає адаптивність?",
    "about_adaptivity": (
        "Звичайні веб-скрапери — це програми, які збирають дані з сайтів за вказівками "
        "на кшталт \"візьми текст із заголовка всередині елемента з класом .news-title\". "
        "Такі вказівки називаються CSS-селекторами або XPath-виразами — це мови, якими "
        "програміст описує, де саме на сторінці лежить потрібна інформація. Проблема в тому, "
        "що варто сайту трохи змінити дизайн — і всі вказівки перестають працювати, "
        "доводиться все переналаштовувати вручну.\n\n"
        "Ця програма працює інакше. Замість жорстких інструкцій вона використовує великі "
        "мовні моделі (LLM) для семантичного, тобто смислового, розуміння вмісту сторінки. "
        "Програма не шукає \"текст у класі .news-title\" — вона читає сторінку як людина "
         "і розуміє: \"ось заголовок, ось автор, ось дата\", що забезпечує:\n\n"
        "**1. Стійкість до змін верстки.** LLM аналізує зміст, а не HTML-структуру. "
        "Якщо сайт змінить CSS-класи або порядок елементів, скрапер не зламається.\n\n"
        "**2. Універсальність до джерел.** Одна й та сама програма працює на будь-якому "
        "новинному сайті — від BBC до Української правди — без доналаштування.\n\n"
        "**3. Контекстне розуміння.** LLM розуміє, що \"Ілон Маск\", \"засновник Tesla\" "
        "і \"власник Twitter\" — це одна й та сама людина, навіть якщо в тексті "
        "використані різні формулювання.\n\n"
        "**4. Інтелектуальне визначення типу.** Система автоматично визначає, чи є стаття "
        "новиною, інтерв'ю або думкою, і відповідно адаптує витягування даних."
    ),
    "about_tech": "Технології та їх роль",
    "about_tech_python": "Мова програмування. Забезпечує основну логіку застосунку, асинхронність та інтеграцію всіх компонентів.",
    "about_tech_fastapi": "Веб-фреймворк. Реалізує REST API для прийому запитів від фронтенду та виклику логіки скрапінгу.",
    "about_tech_crawl4ai": "Бібліотека веб-скрапінгу. Керує браузером Chromium для завантаження сторінок і забезпечує LLM-стратегію витягування даних.",
    "about_tech_deepseek": "Велика мовна модель. Відповідає за семантичний аналіз, витягування полів, визначення типу статті, переклад та узагальнення контенту.",
    "about_tech_streamlit": "Фреймворк для фронтенду. Забезпечує інтерактивний веб-інтерфейс з авторизацією, історією та експортом.",
    "about_tech_sqlite": "Легковажна база даних. Зберігає облікові записи користувачів та історію скрапінгу.",
    "about_features_heading": "Можливості",
    "about_feature1": "Адаптивне витягування даних за допомогою LLM (Crawl4AI + DeepSeek) — програма самостійно визначає структуру сторінки та витягує потрібні поля без ручного налаштування селекторів",
    "about_feature2": "Автоматичне визначення типу статті (новина, інтерв'ю, думка) — для інтерв'ю додатково витягуються ключові цитати та факти",
    "about_feature3": "Переклад вмісту на обрану мову з візуальною індикацією — якщо стаття іншою мовою, LLM перекладає всі поля, а інтерфейс позначає це тегом \"Перекладено\"",
    "about_feature4": "Авторизація користувачів (реєстрація/вхід) та персональна історія скрапінгу з можливістю перегляду збережених результатів",
    "about_feature5": "Експорт результатів у JSON та CSV для подальшого аналізу та інтеграції з іншими інструментами обробки даних",
    "about_purpose_title": "Про дипломний проєкт",
    "about_purpose": "Дослідження можливостей використання великих мовних моделей (LLM) для автоматизованого збору та обробки веб-даних із відкритих джерел. Фокус на легкій, малоресурсній інтеграції LLM для виявлення та структурування релевантної інформації, фільтрації шуму та адаптивного парсингу.",
    "about_relevance": "Актуальність: Зі зростанням обсягів відкритих даних зростає потреба у швидкому, гнучкому та \"розумному\" зборі інформації з інтернету. Великі мовні моделі дають змогу не лише отримувати дані, а й одразу їх фільтрувати, структурувати та узгоджувати за змістом, що особливо важливо для досліджень і моніторингу в умовах інформаційного перевантаження.",
    "about_author_title": "Виконавець",
    "about_author_name": "Сусаєв Богдан Вадимович",
    "about_author_group": "ТВ-21",
    "about_author_institute": "Навчально-науковий інститут атомної та теплової енергетики",
    "about_author_specialty": "Інженерія програмного забезпечення",
}

EN = {
    "app_title": "Adaptive Web Information Collection using LLMs",
    "subtitle": "Enter a news article URL and let the LLM extract structured information",
    "url_label": "News Article URL",
    "url_placeholder": "https://example.com/article",
    "scrape_btn": "Start Adaptive Scraping",
    "spinner": "LLM is analyzing the page... Please wait.",
    "no_title": "No Title Found",
    "author": "Author",
    "date": "Date",
    "summary": "Summary",
    "no_summary": "No summary available.",
    "no_image": "No image available",
    "error_url": "Please enter a valid URL.",
    "error_connect": "Cannot connect to backend. Make sure the FastAPI server is running on port 8000.",
    "error_generic": "Request failed: {}",
    "footer": "Built with Crawl4AI + DeepSeek + FastAPI + Streamlit",
    "login_title": "Login",
    "login_page_title": "Sign In",
    "register_title": "Register",
    "register_page_title": "Create Account",
    "username": "Username",
    "password": "Password",
    "login_btn": "Login",
    "register_btn": "Register",
    "logout_btn": "Logout",
    "no_account": "Don't have an account?",
    "has_account": "Already have an account?",
    "register_link": "Register",
    "login_link": "Login",
    "history_title": "History",
    "history_empty": "History is empty",
    "export_json": "Export JSON",
    "export_csv": "Export CSV",
    "nav_scraper": "Scraper",
    "nav_history": "History",
    "language": "Language",
    "welcome": "Welcome, {}",
    "register_success": "Registration successful! Please log in.",
    "login_failed": "Invalid username or password",
    "register_failed": "Username already exists",
    "scrape_again": "Scrape Again",
    "saved_at": "Saved at",
    "result_title": "Scraping Result",
    "article_type": "Article Type",
    "key_points": "Key Points",
    "interview": "Interview",
    "news": "News",
    "opinion": "Opinion",
    "other": "Other",
    "login_required": "Please log in or register to use the scraper.",
    "show_details": "View Result",
    "translated": "Translated",
    "nav_about": "About",
    "about_title": "About",
    "about_adaptivity_title": "What Makes It Adaptive?",
    "about_adaptivity": (
        "Traditional web scrapers work by following rigid instructions like "
        "\"get the text from the element with class .news-title\". These instructions are called "
        "CSS selectors or XPath expressions — languages that describe where exactly on a page "
        "the needed information is located. The problem is that if the website changes its design, "
        "all these instructions break and must be manually updated.\n\n"
        "This application works differently. Instead of rigid instructions, it uses Large Language "
        "Models (LLMs) for semantic (meaning-based) understanding of page content. The program "
        "doesn't look for \"text in class .news-title\" — it reads the page like a human and "
         "understands: \"this is the headline, this is the author, this is the date\", which provides:\n\n"
        "**1. Resilience to layout changes.** The LLM analyzes content, not HTML structure. "
        "If a website changes its CSS classes or element order, the scraper does not break.\n\n"
        "**2. Source universality.** The same program works on any news website — from BBC "
        "to The Guardian — without per-site configuration.\n\n"
        "**3. Contextual understanding.** The LLM understands that \"Elon Musk\", "
        "\"Tesla founder\", and \"Twitter owner\" refer to the same person, even when "
        "different phrasings are used in the text.\n\n"
        "**4. Intelligent type detection.** The system automatically determines whether an "
        "article is news, an interview, or an opinion piece, and adapts data extraction accordingly."
    ),
    "about_tech": "Technologies and Their Role",
    "about_tech_python": "Programming language. Provides core application logic, async support, and integration of all components.",
    "about_tech_fastapi": "Web framework. Implements the REST API to receive frontend requests and invoke scraping logic.",
    "about_tech_crawl4ai": "Web scraping library. Manages the Chromium browser for page rendering and provides the LLM extraction strategy.",
    "about_tech_deepseek": "Large Language Model. Handles semantic analysis, field extraction, article type detection, translation, and content summarization.",
    "about_tech_streamlit": "Frontend framework. Provides an interactive web interface with authentication, history, and export features.",
    "about_tech_sqlite": "Lightweight database. Stores user accounts and scraping history persistently.",
    "about_features_heading": "Features",
    "about_feature1": "Adaptive data extraction via LLM (Crawl4AI + DeepSeek) — the application autonomously determines page structure and extracts required fields without manual selector configuration",
    "about_feature2": "Automatic article type detection (news, interview, opinion) — for interviews, key quotes and facts are additionally extracted",
    "about_feature3": "Content translation to the selected language with visual indicator — if the article is in another language, the LLM translates all fields and the UI shows a \"Translated\" badge",
    "about_feature4": "User authentication (register/login) and personal scraping history with the ability to review saved results",
    "about_feature5": "Export results to JSON and CSV for further analysis and integration with other data processing tools",
    "about_purpose_title": "About the Diploma Project",
    "about_purpose": "Research on the capabilities of using Large Language Models (LLMs) for automated collection and processing of web data from open sources. Focus on lightweight, low-resource LLM integration for detecting and structuring relevant information, noise filtering, and adaptive parsing.",
    "about_relevance": "Relevance: With the growth of open data volumes, there is an increasing need for fast, flexible, and \"intelligent\" information collection from the web. LLMs enable not only data retrieval but also immediate filtering, structuring, and semantic alignment, which is especially important for research and monitoring under information overload.",
    "about_author_title": "Author",
    "about_author_name": "Bohdan Susaiev",
    "about_author_group": "TV-21",
    "about_author_institute": "Institute of Atomic and Thermal Energy",
    "about_author_specialty": "Software Engineering",
}
