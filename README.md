# Wikidata Bot — Missing Descriptions in Underrepresented Languages

Bot for adding missing descriptions to Wikidata items in underrepresented languages,
focusing on science, technology, and academic items.

**Operator:** [Maris Dreshmanis](https://www.wikidata.org/wiki/User:Maris_Dreshmanis)
**Account:** Maris Dreshmanis (bot password: ReNeuralAgent)
**Contributions:** [Special:Contributions](https://www.wikidata.org/wiki/Special:Contributions/Maris_Dreshmanis)

## Bots

### wikidata_warmup.py — Multilingual Descriptions
Adds missing descriptions in RU, ES, FR, PT, ID, MS, TR for science/technology items.

- **Method:** Rule-based pattern matching from EN descriptions (1,700+ patterns)
- **Source:** SPARQL queries against Wikidata's own category hierarchy
- **Safety:** maxlag=5, 3-5s delays, abuse filter monitoring, auto-stop on reverts

### wikidata_latvian_bot.py — Latvian Descriptions
Adds missing Latvian (lv) labels and descriptions. Operator is a native Latvian speaker.

- **Method:** Curated dictionary of 2,800+ verified translation pairs. NO machine translation — Latvian grammar is too complex for automated tools.
- **Deduplication:** Max 2 identical descriptions per run to ensure diversity

### wikidata_report.py — Daily Report
Sends daily statistics to Telegram: edit counts, milestones, errors.

## Setup

```bash
# Required environment variables
export WIKIDATA_BOT_USER="Your Username@BotName"
export WIKIDATA_BOT_PASS="your_bot_password"
export DEEPSEEK_API_KEY="your_key"  # optional, for LLM fallback

# Install dependencies
pip install requests

# Run
python3 wikidata_warmup.py --count 50 --lang ru,es --dry-run
python3 wikidata_latvian_bot.py --count 10 --dry-run
```

## Technical Details

- **API:** MediaWiki Action API (wbsetdescription, wbsetlabel)
- **SPARQL:** Wikidata Query Service for candidate discovery
- **Rate limiting:** 5s between SPARQL queries, 3-5s between edits
- **Session management:** Auto re-login on expired CSRF tokens
- **Error handling:** Automatic stop on 2+ reverts, abuse filter monitoring

## License

MIT
