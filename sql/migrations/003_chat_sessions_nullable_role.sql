-- 003: brand-new chats have no role until the user picks one
-- (customer vs cook), so chat_sessions.system_role must allow NULL.
-- FakeDatabase never enforced NOT NULL, which hid this until a real
-- PostgreSQL rejected the very first save_session of a new chat.
ALTER TABLE chat_sessions ALTER COLUMN system_role DROP NOT NULL;
