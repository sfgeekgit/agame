# Clone Game Checklist (agame -> bgame)

This checklist assumes you want a second instance running at `/bgame/` with its own DB.

## 0) What you need to know up front

- New slug (e.g., `bgame`) for URL prefix and cookie names
- New DB name + DB user + DB password
- New `DJANGO_SECRET_KEY`
- New backend port (e.g., 8002)

## 1) Create the new directory

```bash
cp -R /home/agame /home/bgame
```

## 1b) New Git repo (optional)

```bash
cd /home/bgame
rm -rf .git
git init
git add -A
git commit -m "Initial bgame import"
```

If you want a new GitHub repo, create it there first, then:

```bash
git remote add origin <your-new-repo-url>
git branch -M main
git push -u origin main
```

If you want no Git repo at all, remove the `.git` directory after copying:

```bash
rm -rf /home/bgame/.git
```

## 2) Create the new database + user (example)

```bash
mariadb -u root -e "CREATE DATABASE bgame CHARACTER SET utf8mb4;"
mariadb -u root -e "CREATE USER 'bgame'@'localhost' IDENTIFIED BY '<strong-password>';"
mariadb -u root -e "GRANT ALL PRIVILEGES ON bgame.* TO 'bgame'@'localhost';"
mariadb -u root -e "FLUSH PRIVILEGES;"
```

## 2b) Copy data from agame (optional)

```bash
mariadb -u root -e "CREATE DATABASE bgame CHARACTER SET utf8mb4;"
mariadb -u root -e "CREATE USER 'bgame'@'localhost' IDENTIFIED BY '<strong-password>';"
mariadb -u root -e "GRANT ALL PRIVILEGES ON bgame.* TO 'bgame'@'localhost';"
mariadb -u root -e "FLUSH PRIVILEGES;"
mysqldump -u root agame | mariadb -u root bgame
```

## 3) Set instance env vars (systemd service)

Create a new service unit (e.g. `/etc/systemd/system/bgame.service`) or copy `agame.service` and change:

- `WorkingDirectory=/home/bgame/backend`
- `Environment="GAME_SLUG=bgame"`
- `Environment="DB_NAME=bgame"`
- `Environment="DB_USER=bgame"`
- `Environment="DJANGO_SECRET_KEY=..."` (generate securely, example below)
- `Environment="DB_PASSWORD=..."`
- `ExecStart` path to `/home/bgame/backend/venv/bin/gunicorn`
  - Use a unique port (e.g., 8002) and unique log files

Secure key generation example:

```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

## 4) Frontend build with the correct slug

```bash
cd /home/bgame/frontend
VITE_GAME_SLUG=bgame npm run build
```

## 5) Caddy routing

Add handlers for `/bgame/*`, `/bgame/api/*`, `/bgame/content/*` in `/etc/caddy/Caddyfile`, mirroring the `/agame/*` blocks and pointing to the new port and paths.

## 6) Content

Copy or edit `/home/bgame/content/ui.json` as needed.

## 7) Start service

```bash
systemctl daemon-reload
systemctl start bgame
```

## 7b) Log file permissions

If gunicorn fails to start due to log permissions, create the log files and set ownership:

```bash
touch /var/log/bgame-access.log /var/log/bgame-error.log
chown bgame:bgame /var/log/bgame-access.log /var/log/bgame-error.log
```

## 8) Verify

- `https://documentbrain.com/bgame/` loads the UI
- `GET /bgame/api/user/me/` returns a user
- Points update works

## Final Reminder

After everything above is completed and verified, update `/home/bgame/content/ui.json` to change the game title (or ask the agent to set a new title for you).

## Troubleshooting

- Blank page with `/agame/` assets: rebuild with `VITE_GAME_SLUG` and ensure `frontend/vite.config.js` uses it for `base`.
- API returns 500: ensure `DB_USER` is set (defaults to `DB_NAME`) and the service is running as the correct system user.
