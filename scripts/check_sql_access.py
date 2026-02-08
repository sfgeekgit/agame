import os
import sys


ALLOWED = {
    os.path.normpath("backend/game/db.py"),
}

DENY_TOKENS = [
    "django.db import connection",
    "django.db import connections",
    "django.db import connection as",
    "connection.cursor(",
    "connections[",
]


def iter_python_files(root):
    for dirpath, _, filenames in os.walk(root):
        if os.path.normpath(dirpath).startswith(os.path.normpath("backend/venv")):
            continue
        for name in filenames:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def check_file(path):
    rel = os.path.normpath(path)
    if rel in ALLOWED:
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        return [f"{rel}: failed to read ({exc})"]

    hits = []
    for token in DENY_TOKENS:
        if token in text:
            hits.append(token)
    if hits:
        return [f"{rel}: forbidden DB access token(s): {', '.join(hits)}"]
    return []


def main():
    errors = []
    for path in iter_python_files("backend"):
        errors.extend(check_file(path))
    if errors:
        print("SQL access policy violations found:")
        for err in errors:
            print(f"  - {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
