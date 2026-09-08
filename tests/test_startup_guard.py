"""F-17: startup guard — pilot/demo boot modes must not silently run on the
in-memory fake DB. Only an explicit BITEFLOW_FAKE_DB=1 opt-in (or a real
DATABASE_URL) lets them boot."""

import pytest

from src import config, main
from src.db import FakeDatabase


def _pilot(monkeypatch, **overrides):
    monkeypatch.setattr(config.settings, "database_url", "")
    monkeypatch.setattr(config.settings, "biteflow_mode", "pilot")
    monkeypatch.setattr(config.settings, "fake_db_explicit", False)
    for k, v in overrides.items():
        monkeypatch.setattr(config.settings, k, v)


def test_pilot_mode_refuses_fake_db_without_explicit_flag(monkeypatch):
    _pilot(monkeypatch)
    with pytest.raises(RuntimeError, match="fake DB"):
        main.build_runtime()


def test_demo_mode_refuses_fake_db_without_explicit_flag(monkeypatch):
    _pilot(monkeypatch, biteflow_mode="demo")
    with pytest.raises(RuntimeError, match="fake DB"):
        main.build_runtime()


def test_pilot_mode_boots_with_explicit_flag(monkeypatch):
    _pilot(monkeypatch, fake_db_explicit=True)
    db, *_ = main.build_runtime()
    assert isinstance(db, FakeDatabase)


def test_local_mode_still_boots_on_fake_db(monkeypatch):
    _pilot(monkeypatch, biteflow_mode="local")
    db, *_ = main.build_runtime()
    assert isinstance(db, FakeDatabase)
