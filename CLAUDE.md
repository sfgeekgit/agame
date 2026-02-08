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

## Content Directory Structure

- `/content/ui.json` — UI strings (title, buttons, labels, status messages)
- `/content/dialog/` — NPC dialog (Markdown or YAML)
- `/content/story/` — Story text, descriptions

Content is served by Caddy at `/agame/content/*` with no-cache headers.
Frontend fetches it at runtime — no rebuild required for text changes.

## Stack

- **Backend**: Django + DRF, raw SQL, gunicorn on port 8001
- **Frontend**: React + Vite + Tailwind, built to `frontend/dist/`
- **Database**: MariaDB — tables `user_login` and `players`
- **Web server**: Caddy (HTTPS, reverse proxy, static files)
- **Service**: systemd `agame.service` runs as `agame` user

## Key Paths

| What | Path |
|------|------|
| Django settings | `backend/config/settings.py` |
| API views (raw SQL) | `backend/game/views.py` |
| React app | `frontend/src/App.jsx` |
| Vite config | `frontend/vite.config.js` |
| UI text | `content/ui.json` |
| Caddy config | `/etc/caddy/Caddyfile` |
| Systemd service | `/etc/systemd/system/agame.service` |
| DB credentials | `.db_credentials` |

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

## After Changes

- **Frontend code changes**: `cd frontend && npm run build` (rebuilds to `dist/`)
- **Backend code changes**: `systemctl restart agame`
- **Content text changes**: Nothing — takes effect immediately
- **Caddy config changes**: `systemctl reload caddy`
