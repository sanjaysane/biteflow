-- 004: chat_sessions.phone_number must NOT reference users.
-- Sessions are created on the very first inbound message, before the chat
-- owner picks a role and before any users row exists ("brand-new chats
-- start unregistered" in src/state_machine.py). The FK made that first
-- save_session fail on real PostgreSQL; FakeDatabase never enforced it.
-- Trade-off: deleting a user no longer cascades to their session row.
ALTER TABLE chat_sessions DROP CONSTRAINT IF EXISTS chat_sessions_phone_number_fkey;
