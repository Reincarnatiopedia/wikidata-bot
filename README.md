# Wikidata Bot

Bot for adding missing descriptions and labels to Wikidata items in underrepresented languages.

## What it does

- **wikidata_warmup.py** -- Adds missing descriptions to science/tech Wikidata items in multiple languages (RU, DE, ES, FR, PT, and 20+ more via LLM)
- **wikidata_latvian_bot.py** -- Adds missing Latvian labels and descriptions using hand-curated dictionaries
- **wikidata_report.py** -- Generates daily progress reports, optionally sent to Telegram

## How it works

1. Uses SPARQL to find Wikidata items that have English descriptions but lack them in target languages
2. Generates translations using a multi-tier approach:
   - **DeepSeek API** (fast, reliable)
   - **Ollama local LLM** (free, runs locally)
   - **Gemini API** (free tier)
   - **Rule-based dictionaries** (fallback, highest quality for known patterns)
3. Applies quality gates to prevent abuse filter triggers
4. Includes safety features: revert detection, abuse log monitoring, emergency stop

## Setup

1. Create a Wikidata bot password at https://www.wikidata.org/wiki/Special:BotPasswords
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies: `pip install requests`
4. Run with `--dry-run` first:

```bash
python3 wikidata_warmup.py --count 10 --lang ru --dry-run
python3 wikidata_latvian_bot.py --count 10 --dry-run
python3 wikidata_report.py --dry-run
```

## Usage

```bash
# Add Russian descriptions to 50 items
python3 wikidata_warmup.py --count 50 --lang ru

# Add descriptions in multiple languages
python3 wikidata_warmup.py --count 50 --lang de,es,fr,pt

# Use LLM for extended languages (ja, ko, ar, hi, etc.)
python3 wikidata_warmup.py --count 50 --lang ja,ko --use-llm

# Geometric scaling (auto-increase daily)
python3 wikidata_warmup.py --geometric --lang ru,de,es,fr,pt

# Latvian bot
python3 wikidata_latvian_bot.py --count 20
```

## Safety features

- **Quality gate**: Rejects generic/short descriptions that trigger Wikidata abuse filters
- **Revert detection**: Stops if 2+ recent edits were reverted
- **Abuse log monitoring**: Checks for filter hits every 10 edits, emergency stops if triggered
- **Rate limiting**: Enforces delays between SPARQL queries and edits
- **Deduplication**: Limits identical descriptions to prevent mass-cloning

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WIKIDATA_BOT_USER` | Yes | Bot username (e.g., `User@BotName`) |
| `WIKIDATA_BOT_PASS` | Yes | Bot password from Special:BotPasswords |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key for LLM translations |
| `GEMINI_API_KEYS` | No | Comma-separated Gemini API keys |
| `OLLAMA_URL` | No | Ollama API URL (default: localhost:11434) |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token for reports |
| `TELEGRAM_CHAT_ID` | No | Telegram chat ID for reports |

## License

MIT
