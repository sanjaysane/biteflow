# How-to: Supabase setup

BiteFlow needs one Postgres database. Supabase's free tier is plenty for a
pilot.

## 1. Create the project

1. Sign up at [supabase.com](https://supabase.com) → **New project**.
2. Save the database password — you'll need it for the connection string.

## 2. Run the schema

1. Open the **SQL editor** in the Supabase dashboard.
2. Paste the entire contents of `sql/schema.sql` → **Run**.
3. Paste the entire contents of `sql/migrations/002_business_owner.sql` →
   **Run**. (Future migrations: new numbered files, applied in order —
   never re-edit `schema.sql`.)

Verify: **Table editor** should show `users`, `chat_sessions`, `menus`,
`orders`, `ingredients`, `recipes`, `suppliers`, `campaigns`, etc.

## 3. Get the connection string

Project Settings → Database → **Connection string** → **URI** mode. It
looks like:

```
postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres
```

- For **Render / Docker / a VPS**: use this direct URL as `DATABASE_URL`.
- For **Vercel / serverless**: switch the dropdown to the **connection
  pooler** (port 6543) and use that URL instead — serverless functions open
  many short connections and will exhaust the direct pool (see
  `docs/TROUBLESHOOTING.md`).

## 4. Point the app at it

```bash
DATABASE_URL="postgresql://..." ./run.sh
```

Say `hello` in WhatsApp — your session row appears in `chat_sessions`.

## Backups

Supabase free tier includes daily backups. Before any migration, take a
manual backup: Database → Backups → **Create backup**.
