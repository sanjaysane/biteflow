# Video 1 script: BiteFlow local setup in 10 minutes

**Format:** screencast with voiceover. **Length:** ~8–10 min.
**Audience:** a junior developer. **Goal:** from zero to a working local
server with green tests.

---

## Scene 1 — Cold open (0:00–0:30)

**On screen:** Title card — "BiteFlow: WhatsApp micro-commerce, running on
your laptop in 10 minutes."

**Say:** "BiteFlow lets home cooks take orders entirely inside WhatsApp —
no app to install, single-digit replies, three languages built in. In this
video I'll get the whole thing running locally: server, database-free
fakes, and the full test suite, green."

## Scene 2 — Clone and tour (0:30–2:30)

**On screen:** Terminal; `git clone` the repo; open the tree in an editor.
Highlight `src/main.py`, `src/state_machine.py`, `locales/`, `tests/`.

**Say:** "The app is a FastAPI webhook. Meta POSTs WhatsApp messages to
`/webhook`; a declarative state machine routes them; sessions live in
Postgres — or in a fake in-memory DB when no credentials are set, which is
exactly what makes local dev painless."

**On-screen text:** `src/main.py → webhook in` · `state_machine.py → routes`
· `chat_sessions → Postgres`

## Scene 3 — Boot it (2:30–4:30)

**On screen:** Terminal, type along:

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
./run.sh
```

Then `curl localhost:8000/health` → `{"ok": true}`.

**Say:** "No credentials, no problem — with a blank `.env` the app boots
with fake database and fake WhatsApp clients. Perfect for development."

**On-screen text:** `blank .env → fake DB + fake WhatsApp (safe)`

## Scene 4 — The one-command stack (4:30–6:00)

**On screen:** `docker compose up --build`; wait; `curl localhost:8000/health`.

**Say:** "Want the real thing? One command boots Postgres plus the app.
The entrypoint applies the schema and migrations automatically — watch for
the 'database ready' line in the logs."

**On-screen text:** `docker compose up --build` · `entrypoint applies migrations`

## Scene 5 — Green tests (6:00–8:00)

**On screen:** `python -m pytest tests/ -q` → 47 passed; then
`ruff check src tests scripts locustfile.py` → all checks passed;
`python scripts/check_locales.py` → "158 keys × 3 languages".

**Say:** "Forty-seven tests drive the state machine exactly like the
webhook does — invalid menu numbers, cook broadcasts, mid-chat language
switches, the whole business-owner addendum. Lint, format, and locale
parity are all gated in CI, so what you just ran is what GitHub runs."

## Scene 6 — Outro (8:00–8:30)

**On screen:** Title card — "Next: deploy to Render → video 2."

**Say:** "Local's done. Next video: shipping it to Render for about seven
dollars a month, wiring the Meta webhook, and taking a real order."
