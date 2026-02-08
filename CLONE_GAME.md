# Clone Game Checklist (agame -> bgame)

This checklist assumes you want a second instance running at `/bgame/` with its own DB.

## 1) Create the new directory

```bash
cp -R /home/agame /home/bgame
```

## 1b) New Git repo (optional but recommended)

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

## 2) Create the new database + user (example)

```bash
mariadb -u root -e "CREATE DATABASE bgame CHARACTER SET utf8mb4;"
mariadb -u root -e "CREATE USER 'bgame'@'localhost' IDENTIFIED BY '<strong-password>';"
mariadb -u root -e "GRANT ALL PRIVILEGES ON bgame.* TO 'bgame'@'localhost';"
mariadb -u root -e "FLUSH PRIVILEGES;"
```

## 3) Set instance env vars (systemd service)

Create a new service unit (e.g. `/etc/systemd/system/bgame.service`) or copy `agame.service` and change:

- `WorkingDirectory=/home/bgame/backend`
- `Environment="GAME_SLUG=bgame"`
- `Environment="DB_NAME=bgame"`
- `Environment="DJANGO_SECRET_KEY=..."`
- `Environment="DB_PASSWORD=..."`
- `ExecStart` path to `/home/bgame/backend/venv/bin/gunicorn`

## 4) Frontend build with the correct slug

```bash
cd /home/bgame/frontend
VITE_GAME_SLUG=bgame npm run build
```

## 5) Caddy routing

Add handlers for `/bgame/*`, `/bgame/api/*`, `/bgame/content/*` in `/etc/caddy/Caddyfile`, mirroring the `/agame/*` blocks.

## 6) Content

Copy or edit `/home/bgame/content/ui.json` as needed.

## 7) Start service

```bash
systemctl daemon-reload
systemctl start bgame
```

## 8) Verify

- `https://documentbrain.com/bgame/` loads the UI
- `GET /bgame/api/user/me/` returns a user
- Points update works
