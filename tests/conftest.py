import pytest

from bentomail import BentoMailer

RELAY_VARS = (
    "SMTP_SERVER",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASS",
    "SMTP_USE_TLS",
    "SMTP_USE_SSL",
    "SENDER_EMAIL",
)


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    """Keeps the suite independent of relay settings exported on the host."""
    for name in RELAY_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def mailer():
    """
    Builds a BentoMailer that never reads an ambient .env file, so tests
    behave the same on a developer machine as they do in CI.
    """

    def _make(**kwargs):
        kwargs.setdefault("recipients", ["target@example.com"])
        kwargs.setdefault("subject", "Test Subject")
        kwargs.setdefault("load_env", False)
        return BentoMailer(**kwargs)

    return _make
