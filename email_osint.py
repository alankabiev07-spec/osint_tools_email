#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMAIL OSINT SCANNER v1.2 — Termux Edition
Установка: pip install --upgrade requests urllib3
Запуск:    python email_osint.py
"""

import sys
import os
import re
import json
import time
import socket
import datetime
import argparse
import hashlib
import urllib.parse

try:
    import requests
except ImportError:
    print("[!] Установи: pip install --upgrade requests urllib3")
    sys.exit(1)

R="\033[31m"; G="\033[32m"; Y="\033[33m"; C="\033[36m"
W="\033[37m"; BOLD="\033[1m"; DIM="\033[2m"; RST="\033[0m"

def clr(t, *c): return "".join(c) + str(t) + RST

# ─── Загрузка ключей из config.env ───────────────────────────────────────────
def load_config():
    config = {"IPINFO_KEY": "", "HIBP_KEY": ""}
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip()
    return config

CONFIG = load_config()

BANNER = r"""
  ███████╗███╗   ███╗ █████╗ ██╗██╗
  ██╔════╝████╗ ████║██╔══██╗██║██║
  █████╗  ██╔████╔██║███████║██║██║
  ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║
  ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗
  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
   ██████╗ ███████╗██╗███╗   ██╗████████╗
  ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
  ██║   ██║███████╗██║██╔██╗ ██║   ██║
  ██║   ██║╚════██║██║██║╚██╗██║   ██║
  ╚██████╔╝███████║██║██║ ╚████║   ██║
   ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝
  ┌─────────────────────────────────────┐
  │   📧  Email Intelligence Scanner   │
  │   Termux Edition  |  v1.2          │
  └─────────────────────────────────────┘
  [!] Только для законных целей
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Mobile Safari/537.36"
    )
}

def validate_email(email):
    return bool(re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', email))

def check_domain(domain):
    result = {"valid": False, "ip": None, "provider": "Неизвестно"}
    try:
        result["ip"] = socket.gethostbyname(domain)
        result["valid"] = True
    except Exception:
        return result
    providers = {
        "gmail.com":"Google Gmail","googlemail.com":"Google Gmail",
        "yahoo.com":"Yahoo Mail","outlook.com":"Microsoft Outlook",
        "hotmail.com":"Microsoft Hotmail","live.com":"Microsoft Live",
        "mail.ru":"Mail.ru","yandex.ru":"Яндекс Почта",
        "yandex.com":"Яндекс Почта","icloud.com":"Apple iCloud",
        "protonmail.com":"ProtonMail","proton.me":"ProtonMail",
        "tutanota.com":"Tutanota","rambler.ru":"Rambler",
        "bk.ru":"Mail.ru (bk)","list.ru":"Mail.ru (list)",
        "inbox.ru":"Mail.ru (inbox)",
    }
    result["provider"] = providers.get(domain, "Корпоративный (" + domain + ")")
    return result

# ─── IPinfo — подробная инфо по IP ───────────────────────────────────────────
def check_ipinfo(ip):
    result = {}
    if not ip or not CONFIG.get("IPINFO_KEY"):
        return result
    try:
        url = "https://ipinfo.io/" + ip + "?token=" + CONFIG["IPINFO_KEY"]
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            d = r.json()
            result = {
                "IP":           d.get("ip"),
                "Город":        d.get("city"),
                "Регион":       d.get("region"),
                "Страна":       d.get("country"),
                "Координаты":   d.get("loc"),
                "Провайдер":    d.get("org"),
                "Почтовый код": d.get("postal"),
                "Часовой пояс": d.get("timezone"),
            }
    except Exception:
        pass
    return result

def check_gravatar(email):
    result = {"found": False, "profile": {}}
    h = hashlib.md5(email.lower().strip().encode()).hexdigest()
    try:
        r = requests.get("https://www.gravatar.com/avatar/" + h + "?d=404", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            result["found"] = True
            rp = requests.get("https://www.gravatar.com/" + h + ".json", headers=HEADERS, timeout=8)
            if rp.status_code == 200:
                d = rp.json().get("entry", [{}])[0]
                n = d.get("name", {})
                result["profile"] = {
                    "Имя":              n.get("givenName"),
                    "Фамилия":          n.get("familyName"),
                    "Отображаемое имя": d.get("displayName"),
                    "О себе":           d.get("aboutMe"),
                    "Местоположение":   d.get("currentLocation"),
                    "Профиль":          "https://www.gravatar.com/" + h,
                    "Аватар":           "https://www.gravatar.com/avatar/" + h + "?s=200",
                }
    except Exception:
        pass
    return result

def check_hibp(email):
    result = {"checked": False, "breaches": [], "count": 0, "error": None}
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/" + urllib.parse.quote(email)
    h = dict(HEADERS)
    if CONFIG.get("HIBP_KEY"):
        h["hibp-api-key"] = CONFIG["HIBP_KEY"]
    try:
        r = requests.get(url, headers=h, timeout=10)
        result["checked"] = True
        if r.status_code == 200:
            data = r.json()
            result["count"] = len(data)
            result["breaches"] = [
                {"Сайт": b.get("Name",""), "Дата": b.get("BreachDate",""),
                 "Данные": ", ".join(b.get("DataClasses",[]))[:60]}
                for b in data[:5]
            ]
        elif r.status_code == 404:
            result["count"] = 0
        elif r.status_code == 401:
            result["error"] = "HIBP требует API-ключ — добавь в config.env"
        elif r.status_code == 429:
            result["error"] = "Слишком много запросов"
    except Exception as e:
        result["error"] = str(e)[:50]
    return result

def check_hash(email):
    h = hashlib.md5(email.lower().strip().encode()).hexdigest()
    out = {}
    for name, url in [
        ("Gravatar",   "https://www.gravatar.com/avatar/" + h + "?d=404"),
        ("Libravatar", "https://seccdn.libravatar.org/avatar/" + h + "?d=404"),
    ]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            out[name] = r.status_code == 200
        except Exception:
            out[name] = None
    return out

def dorks(email):
    enc  = urllib.parse.quote('"' + email + '"')
    user = urllib.parse.quote(email.split("@")[0])
    return {
        "Google (email)":    "https://www.google.com/search?q=" + enc,
        "Google (username)": "https://www.google.com/search?q=%22" + user + "%22",
        "Pastebin":          "https://www.google.com/search?q=site:pastebin.com+" + enc,
        "GitHub":            "https://github.com/search?q=" + enc + "&type=commits",
        "LinkedIn":          "https://www.linkedin.com/search/results/people/?keywords=" + user,
        "HaveIBeenPwned":    "https://haveibeenpwned.com/account/" + urllib.parse.quote(email),
    }

def sec(title, icon="▸"):
    print("")
    print(clr(icon + " " + title, BOLD, C))
    print(clr("  " + "─" * 42, DIM, W))

def row(k, v, color=W):
    if v: print("  " + clr(k + ":", DIM, W) + " " + clr(str(v), color))

def scan(email):
    report = {"email": email, "scanned_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    print(clr("\n  Цель: " + email, BOLD, C))
    print(clr("  " + "=" * 44, C))

    # Статус ключей
    ipinfo_ok = bool(CONFIG.get("IPINFO_KEY"))
    hibp_ok   = bool(CONFIG.get("HIBP_KEY"))
    print(clr("  IPinfo: ", DIM, W) + clr("✔ активен", G) if ipinfo_ok else clr("  IPinfo: ", DIM, W) + clr("✗ нет ключа", DIM))
    print(clr("  HIBP:   ", DIM, W) + clr("✔ активен", G) if hibp_ok   else clr("  HIBP:   ", DIM, W) + clr("✗ нет ключа (добавь в config.env)", DIM))

    sec("Формат и домен", "📋")
    if not validate_email(email):
        print("  " + clr("✗ Неверный формат!", R, BOLD))
        return None

    domain = email.split("@")[1]
    row("Username", email.split("@")[0], Y)
    row("Домен",    domain, Y)
    print("  " + clr("✔ Формат валидный", G))

    sec("Проверка домена", "🌐")
    d = check_domain(domain)
    row("Активен",   "✔ Да" if d["valid"] else "✗ Нет", G if d["valid"] else R)
    row("IP",        d.get("ip"),       C)
    row("Провайдер", d.get("provider"), Y)
    report["domain"] = d
    time.sleep(0.3)

    # ─── IPinfo ───────────────────────────────────────────────────────────────
    if ipinfo_ok and d.get("ip"):
        sec("IP Геолокация (IPinfo)", "🌍")
        ipdata = check_ipinfo(d["ip"])
        if ipdata:
            row("Страна",       ipdata.get("Страна"),       Y)
            row("Регион",       ipdata.get("Регион"),       W)
            row("Город",        ipdata.get("Город"),        W)
            row("Координаты",   ipdata.get("Координаты"),   C)
            row("Провайдер",    ipdata.get("Провайдер"),    W)
            row("Часовой пояс", ipdata.get("Часовой пояс"), DIM)
        report["ipinfo"] = ipdata
        time.sleep(0.3)

    sec("Gravatar", "🖼 ")
    g = check_gravatar(email)
    if g["found"]:
        print("  " + clr("✔ Аккаунт найден!", G, BOLD))
        for k, v in g["profile"].items():
            row(k, v, G if k in ("Имя","Фамилия") else W)
    else:
        print("  " + clr("✗ Не найден", R))
    report["gravatar"] = g
    time.sleep(0.5)

    sec("Утечки (HaveIBeenPwned)", "🔓")
    hibp = check_hibp(email)
    if hibp.get("error"):
        print("  " + clr("⚠  " + hibp["error"], Y))
        print("  " + clr("→ https://haveibeenpwned.com", DIM, C))
    elif hibp["count"] > 0:
        print("  " + clr("⚠  Найдено утечек: " + str(hibp["count"]), Y, BOLD))
        for b in hibp["breaches"]:
            print("\n  " + clr("● " + b["Сайт"], R, BOLD))
            row("  Дата",   b.get("Дата"),   Y)
            row("  Данные", b.get("Данные"), DIM)
    elif hibp["checked"]:
        print("  " + clr("✔ Утечек не найдено", G))
    report["hibp"] = hibp
    time.sleep(0.5)

    sec("Проверка по хэшу", "🔍")
    for svc, found in check_hash(email).items():
        if found is None:
            print("  " + clr("? " + svc, Y))
        elif found:
            print("  " + clr("✔ " + svc + " — найден", G, BOLD))
        else:
            print("  " + clr("✗ " + svc + " — нет", DIM))

    sec("Ссылки для поиска", "🔗")
    dk = dorks(email)
    for name, url in dk.items():
        print("  " + clr("› " + name, Y))
        print("    " + clr(url, DIM, C))
        print("")
    report["dorks"] = dk

    return report

def save(report):
    slug = report["email"].replace("@","_at_").replace(".","_")
    date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    jf   = "email_osint_" + slug + "_" + date + ".json"
    tf   = "email_osint_" + slug + "_" + date + ".txt"

    with open(jf, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(tf, "w", encoding="utf-8") as f:
        f.write("=" * 55 + "\n")
        f.write("EMAIL OSINT: " + report["email"] + "\n")
        f.write("Дата: " + report["scanned_at"] + "\n")
        f.write("=" * 55 + "\n\n")
        d = report.get("domain", {})
        f.write("ДОМЕН:\n  Провайдер: " + str(d.get("provider")) + "\n  IP: " + str(d.get("ip")) + "\n\n")
        ip = report.get("ipinfo", {})
        if ip:
            f.write("ГЕОЛОКАЦИЯ IP:\n")
            for k, v in ip.items():
                if v: f.write("  " + k + ": " + str(v) + "\n")
            f.write("\n")
        g = report.get("gravatar", {})
        f.write("GRAVATAR:\n")
        if g.get("found"):
            for k, v in g.get("profile", {}).items():
                if v: f.write("  " + k + ": " + str(v) + "\n")
        else:
            f.write("  Не найден\n")
        h = report.get("hibp", {})
        f.write("\nУТЕЧКИ:\n")
        if h.get("error"):
            f.write("  " + h["error"] + "\n")
        elif h.get("count", 0) > 0:
            f.write("  Утечек: " + str(h["count"]) + "\n")
            for b in h.get("breaches", []):
                f.write("  • " + b["Сайт"] + " (" + b["Дата"] + ")\n")
        else:
            f.write("  Чисто\n")
        f.write("\nССЫЛКИ:\n")
        for k, v in report.get("dorks", {}).items():
            f.write("  " + k + ": " + v + "\n")
        f.write("\n" + "=" * 55 + "\n")

    return tf, jf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", "-e", default=None)
    args = parser.parse_args()

    os.system("clear")
    print(clr(BANNER, C, BOLD))

    # Показать статус конфига
    if CONFIG.get("IPINFO_KEY"):
        print(clr("  ✔ config.env загружен", G, DIM))
    else:
        print(clr("  ⚠  config.env не найден — часть функций недоступна", Y, DIM))
    print("")

    email = args.email.strip() if args.email else input(clr("  >>> Email: ", G, BOLD)).strip()
    if not email:
        print(clr("  [!] Пусто!", R))
        sys.exit(1)

    report = scan(email)

    if report:
        print(clr("\n  Сохранить отчёт? [Y/n]: ", W), end="")
        if input().strip().lower() != "n":
            tf, jf = save(report)
            print(clr("  ✔ TXT:  " + tf, G))
            print(clr("  ✔ JSON: " + jf, G))

    print(clr("\n  ⚠  Только для законных целей!\n", Y, BOLD))

if __name__ == "__main__":
    main()
