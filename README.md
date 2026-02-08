# A Game

A browser-based game prototype at https://documentbrain.com/agame/

Players visit the page, automatically get a persistent anonymous account, and earn points by clicking buttons. Points are saved server-side. Closing and reopening the browser preserves progress via a long-lived session cookie.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Django + Django REST Framework |
| Frontend | React + Vite |
| Styling | Tailwind CSS |
| Database | MariaDB |
| Web Server | Caddy |
| Process Manager | systemd |

## Project Structure

```
/home/agame/
  backend/                # Django project
    config/               # Django settings, urls, wsgi
    game/                 # App: API views (raw SQL), CSRF enforcement
    venv/                 # Python virtual environment
  frontend/               # React app (Vite)
    src/                  # Components, entry point
    dist/                 # Production build (served by Caddy)
  content/                # Writer-editable text (served at runtime)
    ui.json               # UI strings: title, buttons, labels
    dialog/               # NPC dialog (future)
    story/                # Story text (future)
```

## Architecture

- **Caddy** terminates HTTPS and serves the React build at `/agame/*`
- API requests (`/agame/api/*`) are proxied to **Django/gunicorn** on port 8001
- Content files (`/agame/content/*`) are served directly by Caddy with no-cache
- **Django sessions** (stored in MariaDB) track anonymous users via a 2-year cookie
- All game text lives in `/content/` — editable without a rebuild

## Database

Two tables in the `agame` database, linked 1:1 by `user_id` (UUID, no FK constraint):

- **user_login** — user identity (user_id, name, created_at)
- **players** — game state (user_id, points, updated_at)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/agame/api/user/me/` | Get or create anonymous user |
| POST | `/agame/api/user/me/points/` | Add points (body: `{"amount": N}`) |

## Common Operations

```bash
# Rebuild frontend after code changes
cd /home/agame/frontend && npm run build

# Restart backend after code changes
systemctl restart agame

# Edit game text (no rebuild needed)
nano /home/agame/content/ui.json

# View logs
journalctl -u agame -f
tail -f /var/log/agame-access.log

# Check database
mariadb -u root agame -e "SELECT * FROM user_login; SELECT * FROM players;"

# Reload Caddy after config changes
systemctl reload caddy
```

## Running Tests

```bash
# Backend (Django)
cd /home/agame/backend && source venv/bin/activate && DB_PASSWORD=<password> python manage.py test game

# Frontend (Vitest)
cd /home/agame/frontend && npx vitest run
```
