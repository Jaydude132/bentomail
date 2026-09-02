import pytest
from email.mime.multipart import MIMEMultipart

from bentomail import Dashboard


def test_message_carries_the_routing_headers(mailer):
    em = mailer(
        recipients=["target@example.com"],
        subject="MIME Test",
        cc_recipient=["cc@example.com"],
        sender="noreply@example.com",
    )
    em.create_header(title="MIME Assembly Test")

    msg = em.as_mime_message()
    assert isinstance(msg, MIMEMultipart)
    assert msg["Subject"] == "MIME Test"
    assert msg["To"] == "target@example.com"
    assert msg["Cc"] == "cc@example.com"
    assert msg["From"] == "noreply@example.com"


def test_multiple_recipients_are_joined(mailer):
    em = mailer(recipients=["a@example.com", "b@example.com"])
    assert em.as_mime_message()["To"] == "a@example.com, b@example.com"


# =========================================================================
# --- CARBON COPY ROUTING ---
# =========================================================================
def test_cc_accepts_a_comma_separated_string(mailer):
    em = mailer(cc_recipient="one@example.com, two@example.com")
    assert em.cc_list() == ["one@example.com", "two@example.com"]


def test_cc_accepts_a_list(mailer):
    em = mailer(cc_recipient=["one@example.com", "two@example.com"])
    assert em.cc_list() == ["one@example.com", "two@example.com"]


def test_no_cc_header_when_none_configured(mailer):
    assert "Cc" not in mailer().as_mime_message()


def test_envelope_covers_both_to_and_cc(mailer):
    em = mailer(recipients=["a@example.com"], cc_recipient="cc@example.com")
    assert em.envelope_recipients() == ["a@example.com", "cc@example.com"]


def test_envelope_does_not_duplicate_an_address(mailer):
    em = mailer(recipients=["a@example.com"], cc_recipient="a@example.com")
    assert em.envelope_recipients() == ["a@example.com"]


def test_cc_never_leaks_into_the_to_header(mailer):
    """
    Regression guard: CC addresses were previously appended to the recipient
    list, which corrupted the To header on every send after the first.
    """
    em = mailer(recipients=["a@example.com"], cc_recipient="cc@example.com")
    em.add_card(title="A", value="1")

    for _ in range(3):
        msg = em.as_mime_message()
        assert msg["To"] == "a@example.com"
        assert msg["Cc"] == "cc@example.com"

    assert em.recipients == ["a@example.com"]


# =========================================================================
# --- BODY ASSEMBLY ---
# =========================================================================
def test_body_offers_both_renderings_when_there_are_no_attachments(mailer):
    assert mailer().as_mime_message().get_content_type() == "multipart/alternative"


def test_body_is_mixed_once_a_file_is_attached(mailer, tmp_path):
    payload = tmp_path / "report.csv"
    payload.write_text("a,b\n1,2\n")

    em = mailer()
    em.add_attachment(str(payload))
    msg = em.as_mime_message()

    assert msg.get_content_type() == "multipart/mixed"
    filenames = [p.get_filename() for p in msg.walk() if p.get_filename()]
    assert "report.csv" in filenames


def test_attachment_can_be_renamed(mailer, tmp_path):
    payload = tmp_path / "raw.csv"
    payload.write_text("x\n")

    em = mailer()
    em.add_attachment(str(payload), custom_filename="Weekly Metrics.csv")
    filenames = [p.get_filename() for p in em.as_mime_message().walk() if p.get_filename()]
    assert "Weekly Metrics.csv" in filenames


def test_missing_attachment_is_reported(mailer, tmp_path):
    with pytest.raises(FileNotFoundError):
        mailer().add_attachment(str(tmp_path / "nope.pdf"))


def test_dashboard_to_mime_has_no_routing_headers():
    """A bare Dashboard produces a body only; addressing belongs to the mailer."""
    dash = Dashboard(subject="x")
    dash.add_card(title="A", value="1")
    msg = dash.to_mime()
    assert msg["To"] is None
    assert msg["Subject"] is None
    assert msg.get_content_type() == "multipart/alternative"


# =========================================================================
# --- ROUTING VALIDATION ---
# =========================================================================
def test_missing_recipients_are_rejected(mailer):
    with pytest.raises(ValueError, match="recipients"):
        mailer(recipients=None).as_mime_message()


def test_missing_subject_is_rejected(mailer):
    with pytest.raises(ValueError, match="subject"):
        mailer(subject=None).as_mime_message()


# =========================================================================
# --- PLAIN TEXT ALTERNATIVE ---
# =========================================================================
def test_message_carries_both_a_text_and_an_html_part(mailer):
    em = mailer()
    em.create_header(title="Service Health")
    em.add_card(title="Uptime", value="99.98%")

    types = [p.get_content_type() for p in em.as_mime_message().walk()]
    assert "text/plain" in types
    assert "text/html" in types


def test_plain_part_precedes_the_html_part(mailer):
    """
    Clients display the last alternative they can render, so the HTML has to
    come second or nobody would ever see it.
    """
    em = mailer()
    em.add_card(title="Uptime", value="99.98%")

    alternative = em.as_mime_message()
    assert alternative.get_content_type() == "multipart/alternative"
    assert [p.get_content_type() for p in alternative.get_payload()] == [
        "text/plain",
        "multipart/related",
    ]


def test_plain_part_contains_the_dashboard_content(mailer):
    em = mailer()
    em.create_header(title="Service Health Report")
    em.add_card(title="Uptime", value="99.98%", label="SLO target 99.90%")
    em.add_success("Cache rollout completed.")

    plain = next(
        p for p in em.as_mime_message().walk() if p.get_content_type() == "text/plain"
    ).get_payload(decode=True).decode()

    assert "Service Health Report" in plain
    assert "99.98%" in plain
    assert "Cache rollout completed." in plain
    assert "<" not in plain


def test_attachments_wrap_the_alternative_body(mailer, tmp_path):
    payload = tmp_path / "report.csv"
    payload.write_text("a,b\n")

    em = mailer()
    em.add_attachment(str(payload))
    msg = em.as_mime_message()

    assert msg.get_content_type() == "multipart/mixed"
    assert msg.get_payload()[0].get_content_type() == "multipart/alternative"
