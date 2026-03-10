# AI Papers Digest Bot

AI-powered arXiv paper digest bot for Telegram.

## Overview

This bot automatically:
- Fetches new papers from arXiv (5000+ daily)
- Filters and scores them using LLM (Claude + Gemini)
- Generates clear summaries in Russian
- Sends daily/weekly/monthly digests via Telegram

## Topics

1. **LLM General** - Prompt engineering, LLM architecture, reasoning methods
2. **LLM in Oil & Gas** - LLM applications in geology, geophysics, drilling
3. **AI in Oil & Gas** - ML/AI applications in petroleum industry

## Tech Stack

- Python 3.12+
- PostgreSQL + SQLAlchemy 2.0
- Aiogram 3.x (Telegram Bot API)
- Anthropic Claude API (Sonnet 4.5 + Opus 4.5)
- Google Gemini API
- APScheduler for task scheduling

## Quick Start

```bash
# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your tokens

# Run database migrations
alembic upgrade head

# Start the bot
python -m src.main
```

## Project Structure

```
ai-papers-bot/
├── src/
│   ├── bot/           # Telegram bot handlers
│   ├── database/      # SQLAlchemy models & repositories
│   ├── llm/           # LLM clients & prompts
│   ├── pipeline/      # 8-stage processing pipeline
│   ├── scheduler/     # APScheduler jobs
│   └── core/          # Config, logging, exceptions
├── migrations/        # Alembic migrations
├── prompts/          # LLM prompt templates
└── tests/            # Pytest tests
```

## License

MIT
