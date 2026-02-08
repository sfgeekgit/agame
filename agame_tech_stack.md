# Tech Stack Summary for Claude Code

## Overview

Set up a minimal Django + React project on Debian. Keep it simple — no extras.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Django |
| Frontend | React |
| Database | MySQL/MariaDB |
| CSS | Tailwind |
| Build tool | Vite |

## Architecture

- **Server-authoritative:** Django is the source of truth for all game state
- **API-based:** React frontend talks to Django via REST API (use Django REST Framework)
- **Raw SQL:** User prefers writing raw SQL over Django ORM — support both, but don't force ORM patterns

## Key Requirements

1. **Anonymous users:** Players start without login. Create a user record with random ID, store in session. They can register later to "claim" their account.

2. **PWA-ready:** Add manifest and minimal service worker for "install to home screen" capability. Don't overcomplicate — just the basics.

3. **Separation of concerns:** 
   - Game logic (Python) — rules, calculations, state
   - Content/Dialog (Markdown or YAML files) — all text, NPC dialog, story content in separate files a writer can edit
   - Components (React) — UI structure and behavior
   - Styling (Tailwind) — visual appearance only

4. **Content files:** All game text and dialog lives in its own directory, in human-readable markup (Markdown or YAML). A writer with small code knowledge can edit these files. Never hardcode dialog or story text in Python or JSX.

## Project Structure

Keep it minimal. Something like:

```
/project
  /backend        # Django project
    /api          # REST endpoints
    /game         # Game logic
  /frontend       # React app (Vite)
    /src
      /components
  /content        # Writer-editable files
    /dialog       # NPC dialog (Markdown or YAML)
    /story        # Story text, descriptions
```

## Setup Notes

- Python via system or pyenv, whatever's simpler on Debian
- Node.js for React/Vite
- MySQL/MariaDB — user already knows this
- Django REST Framework for API
- Tailwind via Vite plugin

## What NOT to include

- No Docker (unless asked)
- No complex deployment setup
- No CI/CD
- Include basic testing setup (see testing notes below)
- No extra libraries beyond the basics

## Goal

A minimal working skeleton where:
1. Django serves an API
2. React renders a page that talks to that API
3. Tailwind styles work
4. Ready to start building actual game features

Keep it simple. Less is more.

## Testing Notes

Include standard testing frameworks for both backend and frontend. Use whatever you (Claude) are most familiar with and is well-suited for Django + React. Set it up so tests can be written and run easily as the project develops.