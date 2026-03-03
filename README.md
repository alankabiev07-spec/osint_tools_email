# osint_tools_email
📧 Email OSINT + 👤 Username Scanner | Termux Android | 15 platforms
 Email OSINT Scanner + 🔍 Social Media Scanner

```
  ███████╗███╗   ███╗ █████╗ ██╗██╗
  ██╔════╝████╗ ████║██╔══██╗██║██║
  █████╗  ██╔████╔██║███████║██║██║
  ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║
  ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗
  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
```

> 🔎 OSINT инструмент для анализа email и поиска аккаунтов по username  
> 📱 Оптимизировано для **Termux (Android)**  
> ⚡ Работает без root

---

## 📋 Возможности

### 📧 Email Scanner (`email_osint.py`)
- ✅ Проверка валидности email
- ✅ Определение провайдера (Gmail, Yandex, Mail.ru и др.)
- ✅ Геолокация IP через IPinfo API
- ✅ Поиск профиля на Gravatar (имя, фамилия, аватар)
- ✅ Проверка утечек через HaveIBeenPwned
- ✅ Проверка по MD5 хэшу (Gravatar, Libravatar)
- ✅ Google Dorks — готовые ссылки для поиска
- ✅ Сохранение отчёта в TXT и JSON

### 👤 Social Media Scanner (`osint_termux.py`)
- ✅ Проверка username на 15 платформах
- ✅ GitHub: имя, bio, локация, фолловеры, репозитории
- ✅ Reddit: карма, дата регистрации
- ✅ Прогресс-бар в реальном времени
- ✅ Сохранение отчёта в TXT и JSON

**Платформы:** GitHub, Twitter/X, Instagram, TikTok, Reddit, Pinterest, Telegram, Medium, Dev.to, Twitch, Steam, Linktree, Soundcloud, Patreon, Spotify

---

## 📱 Установка в Termux

```bash
# Обновление пакетов
pkg update && pkg install python

# Установка зависимостей
pip install --upgrade requests urllib3
```

---

## ⚙️ Настройка API ключей

Скопируй `config.env.example` → `config.env` и вставь свои ключи:

```bash
cp config.env.example config.env
nano config.env
```

```env
IPINFO_KEY=твой_ключ_здесь
HIBP_KEY=твой_ключ_здесь
```

### Где получить ключи:
| Сервис | Ссылка | Цена |
|--------|--------|------|
| IPinfo | [ipinfo.io/signup](https://ipinfo.io/signup) | Бесплатно (50к/мес) |
| HaveIBeenPwned | [haveibeenpwned.com/API/Key](https://haveibeenpwned.com/API/Key) | ~$3.50/мес |

---

## 🚀 Запуск

### Email сканер:
```bash
# Интерактивный режим
python email_osint.py

# Через аргумент
python email_osint.py -e target@gmail.com
```

### Social Media сканер:
```bash
# Интерактивный режим
python osint_termux.py

# Через аргумент
python osint_termux.py -u username
python osint_termux.py -u username --delay 1.0
```

---

## 📊 Пример вывода

```
  Цель: example@gmail.com
  ════════════════════════════════════════════

▸ Формат и домен
  ────────────────────────────────────────────
  Username:  example
  Домен:     gmail.com
  ✔ Формат валидный

▸ IP Геолокация (IPinfo)
  ────────────────────────────────────────────
  Страна:       KZ
  Город:        Almaty
  Провайдер:    AS15169 Google LLC
  Часовой пояс: Asia/Almaty

▸ Gravatar
  ────────────────────────────────────────────
  ✔ Аккаунт найден!
  Имя:      John
  Фамилия:  Doe

▸ Утечки (HaveIBeenPwned)
  ────────────────────────────────────────────
  ⚠  Найдено утечек: 3
  ● Adobe  Дата: 2013-10-04
  ● LinkedIn  Дата: 2016-05-05
```

---

## 📁 Структура проекта

```
📦 osint-tools/
 ┣ 📄 email_osint.py       — Email OSINT сканер
 ┣ 📄 osint_termux.py      — Social Media сканер
 ┣ 📄 config.env.example   — Шаблон конфига
 ┣ 📄 config.env           — Твои ключи (НЕ заливай на GitHub!)
 ┗ 📄 README.md
```

---

## ⚠️ Важно

- Используй **только в законных целях**
- Только для анализа **публичных данных**
- Автор не несёт ответственности за неправомерное использование
- `config.env` добавлен в `.gitignore` — ключи не утекут

---

## ☕ Поддержать автора

Если инструмент оказался полезным:

| Способ | Реквизиты |
|--------|-----------|
| ⭐ GitHub | Поставь звезду на репозиторий! |
| telegram | `police_003` |

---

## 📜 Лицензия

MIT License — используй свободно, упоминай автора.

---

*Сделано с ❤️ для Termux*
