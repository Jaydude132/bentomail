from unittest import mock

import pytest

from bentomail import BentoMailer


@pytest.fixture
def relay(mailer):
    """A mailer aimed at a fake relay, with one card so it has content."""

    def _make(**kwargs):
        kwargs.setdefault("smtp_server", "relay.test")
        em = mailer(**kwargs)
        em.add_card(title="A", value="1")
        return em

    return _make


# =========================================================================
# --- CONFIGURATION RESOLUTION ---
# =========================================================================
def test_explicit_arguments_beat_the_environment(monkeypatch):
    monkeypatch.setenv("SMTP_SERVER", "from-env.example.com")
    em = BentoMailer(
        recipients=["a@b.com"], subject="x", smtp_server="explicit.example.com"
    )
    assert em.smtp_server == "explicit.example.com"


def test_environment_is_used_when_no_argument_is_given(monkeypatch):
    monkeypatch.setenv("SMTP_SERVER", "from-env.example.com")
    monkeypatch.setenv("SMTP_PORT", "2525")
    em = BentoMailer(recipients=["a@b.com"], subject="x")
    assert em.smtp_server == "from-env.example.com"
    assert em.smtp_port == 2525


def test_unparseable_port_falls_back_to_the_default(monkeypatch):
    monkeypatch.setenv("SMTP_PORT", "not-a-number")
    em = BentoMailer(recipients=["a@b.com"], subject="x")
    assert em.smtp_port == 25


def test_load_env_false_skips_the_dotenv_file(tmp_path, monkeypatch):
    """A caller supplying settings directly must not pick up a stray .env."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text('SMTP_SERVER="from-dotenv.example.com"\n')

    em = BentoMailer(
        recipients=["a@b.com"], subject="x", smtp_server="explicit", load_env=False
    )
    assert em.smtp_server == "explicit"


@pytest.mark.parametrize(
    "port, expect_tls, expect_ssl",
    [(587, True, False), (465, False, True), (25, False, False)],
)
def test_encryption_follows_the_standard_ports(mailer, port, expect_tls, expect_ssl):
    em = mailer(smtp_port=port)
    assert em.use_tls is expect_tls
    assert em.use_ssl is expect_ssl


def test_explicit_flag_overrides_port_inference(mailer):
    assert mailer(smtp_port=587, use_tls=False).use_tls is False


# =========================================================================
# --- DISPATCH ---
# =========================================================================
def test_submission_port_negotiates_starttls(relay):
    em = relay(smtp_port=587)
    with mock.patch("smtplib.SMTP") as smtp:
        em.send_dashboard()
    assert smtp.call_args[0] == ("relay.test", 587)
    assert smtp.return_value.starttls.called


def test_smtps_port_uses_an_implicit_ssl_connection(relay):
    em = relay(smtp_port=465)
    with mock.patch("smtplib.SMTP_SSL") as smtp_ssl:
        em.send_dashboard()
    assert smtp_ssl.called
    assert not smtp_ssl.return_value.starttls.called


def test_credentials_trigger_a_login(relay):
    em = relay(smtp_port=587, smtp_user="user", smtp_pass="secret")
    with mock.patch("smtplib.SMTP") as smtp:
        em.send_dashboard()
    smtp.return_value.login.assert_called_once_with("user", "secret")


def test_login_is_skipped_without_credentials(relay):
    em = relay(smtp_port=25)
    with mock.patch("smtplib.SMTP") as smtp:
        em.send_dashboard()
    assert not smtp.return_value.login.called


def test_delivery_uses_the_envelope_not_the_to_header(relay):
    em = relay(recipients=["a@b.com"], cc_recipient="cc@b.com")
    with mock.patch("smtplib.SMTP") as smtp:
        em.send_dashboard()

    sender, envelope, body = smtp.return_value.sendmail.call_args[0]
    assert envelope == ["a@b.com", "cc@b.com"]
    assert "To: a@b.com" in body
    assert "Cc: cc@b.com" in body


def test_connection_is_always_closed(relay):
    em = relay()
    with mock.patch("smtplib.SMTP") as smtp:
        em.send_dashboard()
    assert smtp.return_value.quit.called


def test_relay_failure_is_wrapped_but_keeps_its_cause(relay):
    em = relay()
    failing = mock.patch("smtplib.SMTP", side_effect=OSError("connection refused"))
    with failing, pytest.raises(RuntimeError, match="relay.test") as excinfo:
        em.send_dashboard()

    assert isinstance(excinfo.value.__cause__, OSError)
    assert "connection refused" in str(excinfo.value)
