# VoiceScribe 🎙️

Telegram-бот для расшифровки голосовых сообщений и аудиофайлов.  
Отправь голосовое — получи текст. Одним нажатием сохрани в TXT или PDF.

---

## Возможности

- **Голосовые любой длины** — принимает OGG/Opus из Telegram напрямую
- **Автоматическое определение языка** — русский, украинский, английский и другие
- **Транскрипция через Groq Whisper** — быстро и точно
- **Кнопки экспорта под каждым сообщением** — [📄 TXT] и [📑 PDF]
- **Имена файлов с датой и временем** — `voicescribe_2026-04-15_14-30.pdf`
- **PDF с поддержкой кириллицы**

---

## Как это выглядит

### Бот в работе — транскрипция голосового

![Транскрипция голосового](screenshots/bot%20test%201.PNG)

### Кнопки экспорта TXT и PDF

![Инлайн кнопки](screenshots/bot%20test%203%20inline%20buttoms.PNG)

### Результат в PDF-файле

![PDF файл](screenshots/save%20result%20in%20pdf%20file.PNG)

### Редактор PDF

![Редактор PDF](screenshots/editor%20PDF.PNG)

---

## Стек

| Компонент | Технология |
|---|---|
| Бот | [aiogram 3](https://docs.aiogram.dev/) |
| Транскрипция | [Groq Whisper](https://console.groq.com/) (`whisper-large-v3-turbo`) |
| PDF | [fpdf2](https://py-pdf.github.io/fpdf2/) |
| Тесты | pytest (30 тестов, Groq замокан) |

---

## Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/TinaUma/voicescribe.git
cd voicescribe
```

### 2. Создай виртуальное окружение и установи зависимости

```bash
python -m venv .venv
.venv/Scripts/activate     # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 3. Настрой переменные окружения

```bash
cp .env.example .env
```

Открой `.env` и заполни:

```
BOT_TOKEN=твой_токен_от_@BotFather
GROQ_API_KEY=твой_ключ_от_console.groq.com
```

### 4. Добавь шрифт для PDF (кириллица)

```bash
# Windows — скопируй системный шрифт:
cp C:\Windows\Fonts\arial.ttf fonts\Arial.ttf
```

### 5. Запусти бота

```bash
python bot.py
```

---

## Тесты

```bash
pytest tests/ -v
```

30 тестов: environment, handlers, transcriber, exporter. Groq API замокан — работают без реального ключа.

---

## Архитектура

```
bot.py          — точка входа, регистрация роутера
handlers.py     — обработчики: voice, audio, callback (TXT/PDF)
transcriber.py  — Groq Whisper: bytes → str
exporter.py     — генерация TXT и PDF в памяти (bytes)
tests/          — 30 pytest тестов
fonts/          — Arial.ttf (не в репо, нужен локально)
```

---

## Планируемые улучшения

- Поддержка длинных аудио (разбивка на части)
- История транскрипций пользователя
- Рерайт текста через Claude API

---

## Лицензия

MIT
