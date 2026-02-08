import os


def _env(name, default=None):
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


GAME_SLUG = _env("GAME_SLUG", "agame")

if GAME_SLUG == "/":
    GAME_SLUG = ""
if GAME_SLUG.startswith("/"):
    GAME_SLUG = GAME_SLUG.strip("/")

URL_PREFIX = f"/{GAME_SLUG}" if GAME_SLUG else ""
URL_PATH = f"{URL_PREFIX}/" if URL_PREFIX else "/"

SESSION_COOKIE_NAME = f"{GAME_SLUG}_session" if GAME_SLUG else "game_session"
CSRF_COOKIE_NAME = f"{GAME_SLUG}_csrf" if GAME_SLUG else "game_csrf"

DB_NAME = _env("DB_NAME", GAME_SLUG or "agame")
