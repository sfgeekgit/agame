# A Game — Project Rules for Claude

## !!!! CRITICAL RULE — ALL TEXT IN /content/ !!!!
##
## NEVER hardcode user-visible text in JSX, Python, or HTML.
## ALL text — titles, labels, button text, error messages, dialog,
## story content, UI strings — lives in /home/agame/content/.
##
## A writer with minimal code knowledge must be able to change
## any text the player sees by editing files in /content/.
## No rebuild needed — content is fetched at runtime.
##
## If you're adding new text, add it to the appropriate content
## file first, then reference it in code.
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Documentation Split

- **`CLAUDE.md`** (this file, in git) — code rules, test commands, git workflow. Things any contributor needs.
- **`SERVER.md`** (gitignored) — infrastructure: Caddy, systemd, MariaDB, ports, security. Server-operator details only. **Read it and write to it** when dealing with deployment, config, or security topics.

## Content Directory

- `content/ui.json` — UI strings (title, buttons, labels, status messages)
- `content/dialog/` — NPC dialog (Markdown or YAML)
- `content/story/` — Story text, descriptions

Content is fetched at runtime — no rebuild required for text changes.

## Stack

- **Backend**: Django + DRF, raw SQL
- **Frontend**: React + Vite + Tailwind
- **Database**: MariaDB

## Key Code Paths

| What | Path |
|------|------|
| Django settings | `backend/config/settings.py` |
| API views (raw SQL) | `backend/game/views.py` |
| React app | `frontend/src/App.jsx` |
| Vite config | `frontend/vite.config.js` |
| UI text | `content/ui.json` |

## Tests

Run before committing. Both must pass.

```bash
# Backend (16 tests)
cd /home/agame/backend && source venv/bin/activate && DB_PASSWORD=$(grep -oP 'password: \K.*' /home/agame/.db_credentials) python manage.py test game -v2

# Frontend (10 tests)
cd /home/agame/frontend && npx vitest run
```

## Git / GitHub

This server has the owner's GitHub SSH keys configured. When making commits:
- Commits MUST use the git user.name and user.email already set in the environment so the owner gets contribution credit ("green squares")
- It's fine to also credit Claude as co-author, but the owner must be the committer
- Repo: https://github.com/sfgeekgit/agame

## After Code Changes

- **Frontend**: `cd frontend && npm run build`
- **Backend**: `systemctl restart agame`
- **Content text**: Nothing — takes effect immediately
