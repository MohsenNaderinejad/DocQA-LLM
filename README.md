# DocQA-LLM — Document Question Answering System (Django + LangChain + OpenRouter)

A backend web application that lets you **upload `.docx` documents**, automatically **extract and store full text**, **split documents into chunks**, **generate embeddings**, and then **answer user questions** using an LLM **strictly based on the uploaded documents**.

This project is designed to meet an internship-style “LLM + Document Q&A” assignment and focuses on:
- a **clean, extensible backend**
- a **usable REST API**
- a **Django Admin UI** (no separate frontend)
- **Docker** support for easy setup and reproducibility

---

## Table of Contents (English)

- [Key Features (Requirement Checklist)](#key-features-requirement-checklist)
- [Tech Stack](#tech-stack)
- [High-Level Architecture / Flow](#high-level-architecture--flow)
- [Project Structure](#project-structure)
- [Setup (Recommended): Run with Docker (PostgreSQL + pgvector)](#setup-recommended-run-with-docker-postgresql--pgvector)
- [Setup (Alternative): Run Locally without Docker (PostgreSQL + pgvector)](#setup-alternative-run-locally-without-docker-postgresql--pgvector)
- [.env Configuration](#env-configuration)
- [Database & Migrations](#database--migrations)
- [Create Admin User (Django Admin)](#create-admin-user-django-admin)
- [Using the Admin Panel](#using-the-admin-panel)
- [API Overview (Quick Examples)](#api-overview-quick-examples)
- [More Detailed API Docs](#more-detailed-api-docs)
- [Sample Data](#sample-data)
- [Troubleshooting](#troubleshooting)
- [Notes / Limitations](#notes--limitations)
- [License](#license)

---

## Key Features (Requirement Checklist)

This system includes the minimum expected capabilities:

- **Django is used** (project is a Django backend).
- **Docker support** (`Dockerfile` + `docker-compose.yml`) for reproducible execution.
- **LangChain is used** to connect to an LLM (via OpenRouter).
- **Django Admin UI** is the management interface (no separate frontend required).
- A **usable REST API** (via Django REST Framework) that supports:
  - Add / list documents
  - Retrieve / delete documents
  - Ask a question
  - Retrieve question/answer history
- **DOCX support**: upload `.docx` files.
- **Full text storage**: extracted text is saved in the database.
- **Advanced retrieval**:
  - documents are split into chunks
  - embeddings are generated for chunks
  - similarity search is performed using **pgvector**
- **Answer generation from documents**:
  - relevant chunks are retrieved
  - LLM answers based only on the retrieved context
- **History storage**: question/answer and sources are persisted.

---

## Tech Stack

- **Backend**: Django, Django REST Framework
- **LLM Orchestration**: LangChain
- **LLM Provider**: OpenRouter (free model collection supported)
  - default model in code: `nvidia/nemotron-3-super-120b-a12b:free`
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim vectors)
- **Vector Database**: PostgreSQL + **pgvector** (via `pgvector` Python package)
- **Document Parsing**: `python-docx`
- **Containerization**: Docker, Docker Compose

---

## High-Level Architecture / Flow

1. **Upload a `.docx`** document via API or Django Admin.
2. A Django **signal** triggers processing after creation:
   - extract text from `.docx`
   - save `extracted_text` (full text)
   - split text into overlapping chunks
   - store chunks in `DocumentChunk`
3. Each chunk gets an **embedding** vector and is stored in PostgreSQL (pgvector).
4. When a user asks a question:
   - the question is embedded
   - similar chunks are retrieved by vector similarity (cosine distance)
   - a context prompt is built from the top chunks
   - the LLM generates an answer **using only the provided context**
5. The system saves the result into `QAHistory` and links the source documents.

---

## Project Structure

- `core/`  
  Django project settings and root URLs.
- `documents/`  
  Document upload model + text extraction + chunking + embedding generation.
- `qa/`  
  Question answering pipeline (retrieval + LLM call) and history storage.
- `API_DOCUMENTATION.md`  
  Detailed REST API documentation and examples.
- `docker-compose.yml`, `Dockerfile`  
  Containerized setup for web + database.

---

## Setup (Recommended): Run with Docker (PostgreSQL + pgvector)

### Prerequisites
- Docker + Docker Compose installed
- An OpenRouter API key (see: https://openrouter.ai)

### 1) Create `.env`
Create a file named `.env` in the project root (same folder as `docker-compose.yml`).

You can use the template in the section: [.env Configuration](#env-configuration)

### 2) Build and run containers
From the project root:

```bash
docker compose up --build
```

What happens:
- The `db` container starts (PostgreSQL with pgvector enabled).
- The `web` container starts and automatically runs:
  - `python manage.py migrate`
  - `python manage.py runserver 0.0.0.0:8000`

### 3) Open the app
- API base: `http://localhost:8000/api/`
- Admin panel: `http://localhost:8000/admin/`

---

## Setup (Alternative): Run Locally without Docker (PostgreSQL + pgvector)

This setup is useful if you want to learn Django/Python tooling and run everything on your OS directly.

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- pgvector extension installed/enabled in PostgreSQL
- `pip` and `venv`

### 1) Create and activate virtual environment

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install requirements
```bash
pip install -r requirements.txt
```

### 3) Create `.env`
Create `.env` in the project root. See: [.env Configuration](#env-configuration)

### 4) Run migrations and start server
```bash
python manage.py migrate
python manage.py runserver
```

Then open:
- API base: `http://127.0.0.1:8000/api/`
- Admin panel: `http://127.0.0.1:8000/admin/`

---

## .env Configuration

Create a file named `.env` in the project root.

Minimum required variables:

```env
# Django
SECRET_KEY=replace-this-with-a-strong-secret-key

# Database (PostgreSQL)
# Docker Compose will expose the DB at host "db" inside the docker network.
# If running locally without Docker, you will typically use "localhost".
DATABASE_URL=postgresql://docqa_user:docqa_password@db:5432/docqa

# OpenRouter (LLM)
OPENROUTER_API_KEY=replace-with-your-openrouter-api-key
# Optional: override the default model from code
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

Notes:
- `OPENROUTER_MODEL` can be omitted; the code uses a default.
- If you run **without Docker**, change `@db:5432` to `@localhost:5432` (or your DB host).

---

## Database & Migrations

### What migrations do
Django migrations are version-controlled “database schema changes”.  
They create tables like:
- `documents_document`
- `documents_documentchunk` (includes the pgvector embedding column)
- `qa_qahistory` (stores questions/answers and sources)

### Apply migrations
Docker mode: migrations run automatically on container startup, but you can run them manually:

```bash
docker compose exec web python manage.py migrate
```

Local mode:

```bash
python manage.py migrate
```

---

## Create Admin User (Django Admin)

Create a superuser to access the admin panel:

**Docker:**
```bash
docker compose exec web python manage.py createsuperuser
```

**Local:**
```bash
python manage.py createsuperuser
```

Then login at:
- `http://localhost:8000/admin/`

---

## Using the Admin Panel

In Django Admin you can:
- Add / edit / delete **Documents**
- Inspect **DocumentChunk** objects (inline under each document; read-only)
- View **QA History** (read-only history of questions and answers)

Typical workflow:
1. Login to `/admin/`
2. Add a new Document (upload `.docx`)
3. Wait briefly for processing (text extraction + chunking + embeddings)
4. Use API endpoint `/api/ask/` to query the documents
5. View Q&A history in admin

---

## API Overview (Quick Examples)

Base URL: `http://localhost:8000/api`

### 1) Upload a document (`.docx`)
```bash
curl -X POST http://localhost:8000/api/documents/ \
  -F "title=My Document" \
  -F "file=@/path/to/file.docx"
```

### 2) Ask a question
```bash
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this document about?"}'
```

### 3) Fetch question history (last 20)
```bash
curl http://localhost:8000/api/history/
```

---

## More Detailed API Docs

See the full API reference here:
- `API_DOCUMENTATION.md`

It includes:
- full endpoint list
- request/response bodies
- status codes and error formats
- more examples

---

## Sample Data

The repository includes a ready-to-use `sample_data/` folder with **10 `.docx` files**:

- `sample_data/en_01_employee_handbook.docx`
- `sample_data/en_02_rental_agreement.docx`
- `sample_data/en_03_product_manual.docx`
- `sample_data/en_04_university_regulations.docx`
- `sample_data/en_05_project_requirements_docqa.docx`
- `sample_data/en_06_customer_support_faq.docx`
- `sample_data/fa_01_راهنمای_کارمند.docx`
- `sample_data/fa_02_قرارداد_اجاره.docx`
- `sample_data/fa_03_راهنمای_محصول.docx`
- `sample_data/fa_04_سوالات_متداول.docx`

Each sample document is intentionally long (at least 6000+ characters) for chunking/retrieval demonstrations.

### Upload commands (run from repository root)

```bash
curl -X POST http://localhost:8000/api/documents/ -F "title=Employee Handbook" -F "file=@sample_data/en_01_employee_handbook.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=Rental Agreement" -F "file=@sample_data/en_02_rental_agreement.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=Product Manual" -F "file=@sample_data/en_03_product_manual.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=University Regulations" -F "file=@sample_data/en_04_university_regulations.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=DocQA Project Requirements" -F "file=@sample_data/en_05_project_requirements_docqa.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=Customer Support FAQ" -F "file=@sample_data/en_06_customer_support_faq.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=راهنمای کارمند" -F "file=@sample_data/fa_01_راهنمای_کارمند.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=قرارداد اجاره" -F "file=@sample_data/fa_02_قرارداد_اجاره.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=راهنمای محصول" -F "file=@sample_data/fa_03_راهنمای_محصول.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=سوالات متداول" -F "file=@sample_data/fa_04_سوالات_متداول.docx"
```

### Processing note

After each upload, wait for background processing (text extraction, chunking, and embedding generation) to complete before asking questions.  
If needed, monitor logs:

```bash
docker compose logs -f web
```

### Optional quick test questions

- “What is the monthly payroll date in the employee handbook?”
- “How much is the security deposit in the rental agreement?”
- “What is the first response SLA for priority support tickets?”
- «ساعت کاری عادی در راهنمای کارمند چیست؟»
- «در قرارداد اجاره، مبلغ ودیعه چقدر است؟»
- «در سوالات متداول، زمان پاسخ اولیه برای تیکت فوری چقدر است؟»

---

## Troubleshooting

### 1) “Invalid API key” / OpenRouter errors
- Ensure `.env` contains `OPENROUTER_API_KEY`
- Restart containers after editing `.env`:
  ```bash
  docker compose down
  docker compose up --build
  ```

### 2) pgvector extension / embedding errors
This project expects PostgreSQL with `vector` extension enabled. In Docker, the image is already `pgvector/pgvector`.

### 3) Migrations fail on first run
Try running migrations manually:

```bash
docker compose exec web python manage.py migrate
```

### 4) Document text is empty after upload
Text extraction happens after document creation (signal-based processing). Check logs:

```bash
docker compose logs -f web
```

---

## Notes / Limitations

- Only `.docx` files are supported in the current implementation.
- Very large documents may take longer to embed and may increase memory usage.
- The system is designed to **avoid hallucination** by instructing the LLM to answer only from retrieved context, but quality still depends on:
  - document clarity
  - chunking strategy
  - retrieval quality
  - LLM behavior

---

## License

MIT License (see `LICENSE`)

---

---

# داکیومنت‌کیو-اِل‌اِل‌اِم — سامانه پرسش‌وپاسخ از اسناد (Django + LangChain + OpenRouter)

یک اپلیکیشن بک‌اند تحت وب که به شما اجازه می‌دهد **اسناد `.docx` را آپلود کنید**، متن کامل آن‌ها را **به‌صورت خودکار استخراج و ذخیره کنید**، سند را به **چانک‌های کوچک‌تر** تقسیم کنید، برای هر چانک **امبدینگ** بسازید، و سپس به سوالات کاربران با استفاده از یک **مدل زبانی (LLM)** پاسخ دهید؛ به‌طوری‌که پاسخ **صرفاً بر اساس محتوای اسناد آپلود شده** تولید شود.

این پروژه برای انجام یک تمرین/پروژه‌ی کارآموزی در حوزه‌ی “LLM + Document Q&A” طراحی شده و تمرکز آن روی موارد زیر است:
- یک بک‌اند **تمیز، قابل توسعه و قابل استفاده**
- یک **REST API** کاربردی
- رابط مدیریتی **Django Admin** (بدون نیاز به فرانت‌اند جداگانه)
- پشتیبانی از **Docker** برای اجرای ساده و تکرارپذیر

---

## فهرست مطالب (فارسی)

- [قابلیت‌های کلیدی (چک‌لیست نیازمندی‌ها)](#قابلیتهای-کلیدی-چکلیست-نیازمندیها)
- [پشته فناوری (Tech Stack)](#پشته-فناوری-tech-stack)
- [معماری و جریان کلی سیستم](#معماری-و-جریان-کلی-سیستم)
- [ساختار پروژه](#ساختار-پروژه)
- [راه‌اندازی (پیشنهادی): اجرا با Docker (PostgreSQL + pgvector)](#راهاندازی-پیشنهادی-اجرا-با-docker-postgresql--pgvector)
- [راه‌اندازی (جایگزین): اجرای محلی بدون Docker (PostgreSQL + pgvector)](#راهاندازی-جایگزین-اجرای-محلی-بدون-docker-postgresql--pgvector)
- [پیکربندی فایل .env](#پیکربندی-فایل-env)
- [پایگاه داده و Migrationها](#پایگاه-داده-و-migrationها)
- [ساخت کاربر ادمین (Django Admin)](#ساخت-کاربر-ادمین-django-admin)
- [استفاده از پنل ادمین](#استفاده-از-پنل-ادمین)
- [نمای کلی API (چند مثال کوتاه)](#نمای-کلی-api-چند-مثال-کوتاه)
- [مستندات کامل‌تر API](#مستندات-کاملتر-api)
- [داده نمونه](#داده-نمونه)
- [رفع اشکال (Troubleshooting)](#رفع-اشکال-troubleshooting)
- [نکات / محدودیت‌ها](#نکات--محدودیتها)
- [لایسنس](#لایسنس)

---

## قابلیت‌های کلیدی (چک‌لیست نیازمندی‌ها)

این سامانه حداقل قابلیت‌های مورد انتظار را پیاده‌سازی می‌کند:

- استفاده از **Django** (پروژه یک بک‌اند Django است).
- پشتیبانی از **Docker** (`Dockerfile` + `docker-compose.yml`) برای اجرای تکرارپذیر.
- استفاده از **LangChain** برای ارتباط با مدل زبانی (از طریق OpenRouter).
- رابط مدیریتی **Django Admin** به‌عنوان UI اصلی (بدون نیاز به فرانت‌اند جداگانه).
- ارائه یک **REST API** قابل استفاده (با Django REST Framework) که شامل:
  - افزودن / لیست کردن اسناد
  - دریافت / حذف یک سند
  - پرسیدن سوال
  - دریافت تاریخچه پرسش و پاسخ
- پشتیبانی از فایل‌های **DOCX**: آپلود فایل‌های `.docx`.
- ذخیره‌سازی **متن کامل**: متن استخراج‌شده در دیتابیس ذخیره می‌شود.
- **بازیابی پیشرفته**:
  - سند به چانک‌های کوچک تقسیم می‌شود
  - برای چانک‌ها امبدینگ تولید می‌شود
  - جستجوی شباهت با استفاده از **pgvector** انجام می‌شود
- تولید پاسخ بر اساس اسناد:
  - چانک‌های مرتبط بازیابی می‌شوند
  - LLM فقط بر اساس همان کانتکست پاسخ می‌دهد
- ذخیره تاریخچه:
  - سوال/پاسخ و منابع مورد استفاده ذخیره و قابل مشاهده هستند

---

## پشته فناوری (Tech Stack)

- **Backend**: Django, Django REST Framework
- **هماهنگ‌سازی با LLM**: LangChain
- **سرویس LLM**: OpenRouter (پشتیبانی از مدل‌های رایگان)
  - مدل پیش‌فرض در کد: `nvidia/nemotron-3-super-120b-a12b:free`
- **Embeddings**: `sentence-transformers` (مدل `all-MiniLM-L6-v2` با بردار ۳۸۴ بعدی)
- **Vector Database**: PostgreSQL + **pgvector** (با پکیج `pgvector`)
- **استخراج متن DOCX**: `python-docx`
- **کانتینرسازی**: Docker, Docker Compose

---

## معماری و جریان کلی سیستم

1. یک سند `.docx` را از طریق API یا Django Admin آپلود می‌کنید.
2. یک **signal** در Django بعد از ساخت سند، پردازش را انجام می‌دهد:
   - استخراج متن از `.docx`
   - ذخیره `extracted_text` (متن کامل)
   - تقسیم متن به چانک‌های همپوشان
   - ذخیره چانک‌ها در مدل `DocumentChunk`
3. برای هر چانک یک بردار **embedding** ساخته و در PostgreSQL (با pgvector) ذخیره می‌شود.
4. هنگام پرسیدن سوال:
   - سوال embedding می‌شود
   - چانک‌های مشابه با جستجوی برداری (cosine distance) پیدا می‌شوند
   - از چانک‌های برتر یک کانتکست ساخته می‌شود
   - LLM پاسخ را **صرفاً با استفاده از کانتکست** تولید می‌کند
5. نتیجه در `QAHistory` ذخیره می‌شود و اسناد منبع به آن لینک می‌شوند.

---

## ساختار پروژه

- `core/`  
  تنظیمات Django و URLهای اصلی.
- `documents/`  
  مدل سند + استخراج متن + چانک‌بندی + تولید امبدینگ.
- `qa/`  
  پایپلاین پرسش‌وپاسخ (بازیابی + فراخوانی LLM) و ذخیره تاریخچه.
- `API_DOCUMENTATION.md`  
  مستندات کامل REST API و مثال‌ها.
- `docker-compose.yml`, `Dockerfile`  
  اجرای کانتینری وب‌سرویس و دیتابیس.

---

## راه‌اندازی (پیشنهادی): اجرا با Docker (PostgreSQL + pgvector)

### پیش‌نیازها
- نصب Docker و Docker Compose
- داشتن OpenRouter API key (از: https://openrouter.ai)

### 1) ساخت فایل `.env`
در ریشه پروژه (همان پوشه‌ای که `docker-compose.yml` هست) یک فایل `.env` بسازید.

از قالب بخش: [پیکربندی فایل .env](#پیکربندی-فایل-env) استفاده کنید.

### 2) build و اجرا
در ریشه پروژه:

```bash
docker compose up --build
```

چه اتفاقی می‌افتد:
- کانتینر `db` بالا می‌آید (PostgreSQL با pgvector).
- کانتینر `web` اجرا می‌شود و به‌صورت خودکار:
  - `python manage.py migrate`
  - `python manage.py runserver 0.0.0.0:8000`
  را اجرا می‌کند.

### 3) آدرس‌ها
- API: `http://localhost:8000/api/`
- پنل ادمین: `http://localhost:8000/admin/`

---

## راه‌اندازی (جایگزین): اجرای محلی بدون Docker (PostgreSQL + pgvector)

این روش برای زمانی مناسب است که می‌خواهید ابزارهای Django/Python را بهتر یاد بگیرید و همه‌چیز را مستقیم روی سیستم‌عامل خود اجرا کنید.

### پیش‌نیازها
- Python 3.12+
- PostgreSQL 16+
- نصب و فعال بودن extension مربوط به pgvector در PostgreSQL
- `pip` و `venv`

### 1) ساخت و فعال کردن محیط مجازی

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 3) ساخت فایل `.env`
در ریشه پروژه `.env` بسازید. بخش [پیکربندی فایل .env](#پیکربندی-فایل-env) را ببینید.

### 4) اجرای migrationها و اجرای سرور
```bash
python manage.py migrate
python manage.py runserver
```

سپس:
- API: `http://127.0.0.1:8000/api/`
- پنل ادمین: `http://127.0.0.1:8000/admin/`

---

## پیکربندی فایل .env

در ریشه پروژه یک فایل `.env` ایجاد کنید.

حداقل متغیرهای لازم:

```env
# Django
SECRET_KEY=replace-this-with-a-strong-secret-key

# Database (PostgreSQL)
# در Docker هاست دیتابیس داخل شبکه داکر "db" است.
# اگر بدون Docker اجرا می‌کنید معمولاً باید "localhost" بگذارید.
DATABASE_URL=postgresql://docqa_user:docqa_password@db:5432/docqa

# OpenRouter (LLM)
OPENROUTER_API_KEY=replace-with-your-openrouter-api-key
# اختیاری: تغییر مدل پیش‌فرض
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

نکات:
- `OPENROUTER_MODEL` اختیاری است و اگر نباشد از مدل پیش‌فرض داخل کد استفاده می‌شود.
- اگر **بدون Docker** اجرا می‌کنید، `@db:5432` را به `@localhost:5432` (یا هاست دیتابیس خودتان) تغییر دهید.

---

## پایگاه داده و Migrationها

### Migration چیست؟
Migrationها تغییرات ساختار دیتابیس را نسخه‌بندی می‌کنند. جدول‌هایی مثل موارد زیر ساخته می‌شوند:
- `documents_document`
- `documents_documentchunk` (شامل ستون embedding با نوع برداری)
- `qa_qahistory` (ذخیره سوال/جواب و منابع)

### اجرای migrationها
در Docker معمولاً migration در شروع کانتینر اجرا می‌شود، اما می‌توانید دستی هم اجرا کنید:

```bash
docker compose exec web python manage.py migrate
```

در حالت محلی:

```bash
python manage.py migrate
```

---

## ساخت کاربر ادمین (Django Admin)

برای ورود به پنل ادمین یک superuser بسازید:

**Docker:**
```bash
docker compose exec web python manage.py createsuperuser
```

**Local:**
```bash
python manage.py createsuperuser
```

سپس وارد شوید:
- `http://localhost:8000/admin/`

---

## استفاده از پنل ادمین

در Django Admin می‌توانید:
- سندها را اضافه/ویرایش/حذف کنید
- چانک‌های هر سند را (به‌صورت inline و فقط خواندنی) ببینید
- تاریخچه سوال/جواب را (فقط خواندنی) مشاهده کنید

روال پیشنهادی:
1. ورود به `/admin/`
2. ساخت Document و آپلود `.docx`
3. کمی صبر کنید تا پردازش انجام شود (استخراج متن + چانک + امبدینگ)
4. با `/api/ask/` سوال بپرسید
5. تاریخچه را در admin مشاهده کنید

---

## نمای کلی API (چند مثال کوتاه)

Base URL: `http://localhost:8000/api`

### 1) آپلود سند (`.docx`)
```bash
curl -X POST http://localhost:8000/api/documents/ \
  -F "title=My Document" \
  -F "file=@/path/to/file.docx"
```

### 2) پرسیدن سوال
```bash
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this document about?"}'
```

### 3) دریافت تاریخچه (۲۰ مورد آخر)
```bash
curl http://localhost:8000/api/history/
```

---

## مستندات کامل‌تر API

برای مستندات کامل به فایل زیر مراجعه کنید:
- `API_DOCUMENTATION.md`

این فایل شامل:
- لیست کامل endpointها
- ساختار request/response
- کدهای وضعیت و ارورها
- مثال‌های بیشتر

---

## داده نمونه

در این مخزن پوشه‌ی آماده‌ی `sample_data/` با **۱۰ فایل `.docx`** وجود دارد:

- `sample_data/en_01_employee_handbook.docx`
- `sample_data/en_02_rental_agreement.docx`
- `sample_data/en_03_product_manual.docx`
- `sample_data/en_04_university_regulations.docx`
- `sample_data/en_05_project_requirements_docqa.docx`
- `sample_data/en_06_customer_support_faq.docx`
- `sample_data/fa_01_راهنمای_کارمند.docx`
- `sample_data/fa_02_قرارداد_اجاره.docx`
- `sample_data/fa_03_راهنمای_محصول.docx`
- `sample_data/fa_04_سوالات_متداول.docx`

هر فایل عمداً طولانی (حداقل بیش از ۶۰۰۰ کاراکتر) تهیه شده تا برای نمایش chunking و retrieval مناسب باشد.

### دستورات آپلود (از ریشه‌ی مخزن اجرا شود)

```bash
curl -X POST http://localhost:8000/api/documents/ -F "title=Employee Handbook" -F "file=@sample_data/en_01_employee_handbook.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=Rental Agreement" -F "file=@sample_data/en_02_rental_agreement.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=Product Manual" -F "file=@sample_data/en_03_product_manual.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=University Regulations" -F "file=@sample_data/en_04_university_regulations.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=DocQA Project Requirements" -F "file=@sample_data/en_05_project_requirements_docqa.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=Customer Support FAQ" -F "file=@sample_data/en_06_customer_support_faq.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=راهنمای کارمند" -F "file=@sample_data/fa_01_راهنمای_کارمند.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=قرارداد اجاره" -F "file=@sample_data/fa_02_قرارداد_اجاره.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=راهنمای محصول" -F "file=@sample_data/fa_03_راهنمای_محصول.docx"
curl -X POST http://localhost:8000/api/documents/ -F "title=سوالات متداول" -F "file=@sample_data/fa_04_سوالات_متداول.docx"
```

### نکته پردازش

بعد از هر آپلود، کمی صبر کنید تا استخراج متن، چانک‌بندی و ساخت embedding کامل شود؛ سپس سوال بپرسید.  
در صورت نیاز لاگ‌ها را بررسی کنید:

```bash
docker compose logs -f web
```

### سوال‌های کوتاه پیشنهادی برای تست

- “What is the monthly payroll date in the employee handbook?”
- “How much is the security deposit in the rental agreement?”
- “What is the first response SLA for priority support tickets?”
- «ساعت کاری عادی در راهنمای کارمند چیست؟»
- «در قرارداد اجاره، مبلغ ودیعه چقدر است؟»
- «در سوالات متداول، زمان پاسخ اولیه برای تیکت فوری چقدر است؟»

---

## رفع اشکال (Troubleshooting)

### 1) خطاهای OpenRouter / API key
- مطمئن شوید `OPENROUTER_API_KEY` در `.env` تنظیم شده
- بعد از تغییر `.env` کانتینرها را ری‌استارت کنید:
  ```bash
  docker compose down
  docker compose up --build
  ```

### 2) مشکل pgvector / امبدینگ
این پروژه نیاز دارد extension `vector` در PostgreSQL فعال باشد. در Docker با ایمیج `pgvector/pgvector` این مورد آماده است.

### 3) خطا در migrationها
migration را دستی اجرا کنید:

```bash
docker compose exec web python manage.py migrate
```

### 4) بعد از آپلود متن خالی است
استخراج متن و ساخت چانک‌ها با signal انجام می‌شود و ممکن است کمی زمان ببرد. لاگ‌ها را ببینید:

```bash
docker compose logs -f web
```

---

## نکات / محدودیت‌ها

- در پیاده‌سازی فعلی فقط فایل‌های `.docx` پشتیبانی می‌شوند.
- اسناد بزرگ ممکن است زمان بیشتری برای امبدینگ بخواهند و مصرف RAM را افزایش دهند.
- سامانه برای جلوگیری از hallucination به LLM می‌گوید فقط از کانتکست استفاده کند، اما کیفیت خروجی به موارد زیر وابسته است:
  - کیفیت متن سند
  - نحوه چانک‌بندی
  - کیفیت بازیابی
  - رفتار مدل زبانی

---

## لایسنس

MIT (فایل `LICENSE`)