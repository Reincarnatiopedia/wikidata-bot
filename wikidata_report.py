#!/usr/bin/env python3
"""
Wikidata Daily Report → Telegram
Green wins + Red problems. Motivating, not depressing.
Runs after each bot cron, or standalone.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

# --- Config ---
API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = os.environ.get(
    "WIKIDATA_USER_AGENT",
    "WikidataBot/1.0 (https://github.com/Reincarnatiopedia/wikidata-bot)"
)
BOT_USER = os.environ.get("WIKIDATA_BOT_USER", "").split("@")[0]

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

WARMUP_LOG = os.environ.get("WARMUP_LOG", "logs/wikidata_warmup.log")
LATVIAN_LOG = os.environ.get("LATVIAN_LOG", "logs/wikidata_latvian.log")





def get_edit_count():
    """Get total edit count from Wikidata API."""
    try:
        url = f"{API_URL}?action=query&list=users&ususers={BOT_USER.replace(' ', '+')}&usprop=editcount&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data["query"]["users"][0].get("editcount", 0)
    except Exception:
        return None


def get_today_edits():
    """Count today's edits from Wikidata API."""
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
        url = (f"{API_URL}?action=query&list=usercontribs"
               f"&ucuser={BOT_USER.replace(' ', '+')}"
               f"&uclimit=500&ucstart={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"
               f"&ucend={today}&ucprop=timestamp&format=json")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return len(data.get("query", {}).get("usercontribs", []))
    except Exception:
        return None


def parse_log_results(log_path):
    """Parse bot log for last run results."""
    if not os.path.exists(log_path):
        return None, None, None

    lines = open(log_path).readlines()
    edits_done = 0
    errors = []
    abuse_hits = 0
    clean = False

    # Read last run (from last "Target languages" or "Searching" line)
    last_run_start = 0
    for i, line in enumerate(lines):
        if "Target languages" in line or "Searching for items" in line:
            last_run_start = i

    for line in lines[last_run_start:]:
        m = re.search(r'EDIT (\d+)/(\d+)', line)
        if m:
            edits_done = int(m.group(1))
        if "Error on" in line or "failed" in line.lower():
            errors.append(line.strip()[-100:])
        if "ABUSE FILTER" in line:
            m2 = re.search(r'(\d+) recent hits', line)
            if m2:
                abuse_hits = int(m2.group(1))
        if "Clean run" in line:
            clean = True

    return edits_done, errors[:3], (clean, abuse_hits)


def build_report():
    """Build motivating report with wins and problems."""
    total = get_edit_count()
    today = get_today_edits()

    warmup_edits, warmup_errors, warmup_abuse = parse_log_results(WARMUP_LOG)
    lv_edits, lv_errors, lv_abuse = parse_log_results(LATVIAN_LOG)

    # --- WINS (green) ---
    wins = []
    if total:
        wins.append(f"Всего правок: {total}")
        if total >= 500:
            wins.append("Расширенный статус достигнут!")
        elif total >= 400:
            wins.append(f"Почти! {500 - total} до расширенного статуса")
    if today and today > 0:
        wins.append(f"Сегодня: +{today} правок")
    if warmup_edits and warmup_edits > 0:
        wins.append(f"Основной бот: {warmup_edits} правок (RU/DE/ES/FR/PT)")
    if lv_edits and lv_edits > 0:
        wins.append(f"Латвийский бот: {lv_edits} правок (LV)")
    if warmup_abuse and warmup_abuse[0]:
        wins.append("Warmup: чистый запуск, фильтры не сработали")
    if lv_abuse and lv_abuse[0]:
        wins.append("Latvian: чистый запуск, фильтры не сработали")

    # --- PROBLEMS (red) ---
    problems = []
    if warmup_edits == 0 and warmup_edits is not None:
        problems.append("Основной бот: 0 правок за 24ч (проверить DeepSeek API / SPARQL)")
    if lv_edits == 0 and lv_edits is not None:
        problems.append("Латвийский бот: 0 правок за 24ч (словарь исчерпан?)")
    if warmup_abuse and warmup_abuse[1] > 0:
        problems.append(f"Фильтр злоупотреблений: {warmup_abuse[1]} срабатываний (старые, проверить)")
    if warmup_errors:
        for e in warmup_errors[:2]:
            problems.append(f"Error: {e[-80:]}")
    if lv_errors:
        for e in lv_errors[:2]:
            problems.append(f"LV Error: {e[-80:]}")
    if total and today == 0:
        problems.append("Ноль правок сегодня — крон не работает?")

    # --- Milestones ---
    milestones = ""
    if total:
        next_milestone = 500 if total < 500 else (1000 if total < 1000 else 10000)
        remaining = next_milestone - total
        milestones = f"\nСледующая цель: {next_milestone} (ещё нужно)"

    # --- Build message ---
    msg = "📊 *WIKIDATA ЕЖЕДНЕВНЫЙ ОТЧЁТ*\n"
    msg += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"

    if wins:
        msg += "✅ *ПОБЕДЫ:*\n"
        for w in wins:
            msg += f"  • {w}\n"
        msg += "\n"

    if problems:
        msg += "❌ *ТРЕБУЕТ ВНИМАНИЯ:*\n"
        for p in problems:
            msg += f"  • {p}\n"
        msg += "\n"
    else:
        msg += "🎯 *Проблем не обнаружено*\n\n"

    if milestones:
        msg += milestones + "\n"

    # Progress bar
    if total:
        next_m = 500 if total < 500 else (1000 if total < 1000 else 10000)
        prev_m = 0 if next_m == 500 else (500 if next_m == 1000 else 1000)
        pct = min(100, int((total - prev_m) / (next_m - prev_m) * 100))
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        msg += f"\n`[{bar}] {pct}% → {next_m}`"

    return msg


def send_telegram(msg, token, chat_id):
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    report = build_report()

    if "--dry-run" in sys.argv:
        print(report)
    elif TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        ok = send_telegram(report, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        print("Sent" if ok else "Failed")
    else:
        print("No TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID env vars set")
        print(report)
