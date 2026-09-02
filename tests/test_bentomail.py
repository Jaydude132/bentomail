from bentomail import BentoMailer, Section, themes
from bentomail.layout import group_components
from bentomail.components import Card, FooterLink


def test_bentomailer_initialization_defaults():
    # Verify environment loading logic or fallback
    em = BentoMailer(recipients=["test@example.com"], subject="Test Subject")
    assert em.theme == themes.NEUTRAL
    assert em.subject == "Test Subject"
    assert em.recipients == ["test@example.com"]


def test_bentomailer_component_pipeline():
    em = BentoMailer(recipients=["test@example.com"], subject="Test")
    em.add_card(title="My Card", value="10")
    em.add_critical("System Alert")
    assert len(em._components) == 2
    assert isinstance(em._components[0], Card)
    assert em._components[1].message == "System Alert"


def test_section_widget_enforcements():
    sec = Section(title="Test Section", subtitle="Sub-units")
    sec.add_card(title="My Card", value="50")
    sec.add_report(title="Sub Report", headers=["A", "B"], data=[["1", "2"]])
    assert len(sec.widgets) == 2
    assert sec.widgets[1].colspan == 2


def test_create_footer_dictionary_mapping():
    em = BentoMailer(recipients=["test@example.com"], subject="Test")
    em.create_footer(
        line1="Footer Text", links=[{"text": "Docs", "url": "https://example.com"}]
    )
    assert em.footer_block is not None
    assert len(em.footer_block.links) == 1
    assert isinstance(em.footer_block.links[0], FooterLink)


def test_colspan_grouping_logic():
    em = BentoMailer(recipients=["test@example.com"], subject="Test")
    em.add_critical("Notice 1", colspan=1)
    em.add_success("Notice 2", colspan=1)
    em.add_critical("Notice 3", colspan=2)
    grouped = group_components(em._components)
    assert len(grouped) == 2
    assert len(grouped[0]["items"]) == 2
    assert len(grouped[1]["items"]) == 1


def test_dynamic_card_auto_padding():
    """
    Verifies that if a row is explicitly under-filled,
    the engine automatically appends an invisible padding card to balance the grid.
    """
    em = BentoMailer(recipients=["test@example.com"], subject="Test")

    # Give it one card that explicitly only takes up half the row (colspan=2)
    em.add_card(title="Half Width Card", value="A", colspan=2)

    grouped = group_components(em._components)
    row_items = grouped[0]["items"]

    # 1 real card + 1 auto-generated invisible spacer = 2 items total
    assert len(row_items) == 2
    assert row_items[-1].invisible is True

    # The engine should calculate that exactly 2 columns were missing
    assert row_items[-1].colspan == 2


def test_compile_dashboard_html_execution():
    """
    Integration test: Verifies that the Jinja2 PackageLoader successfully locates
    dashboard.jinja and compiles the variables into a raw HTML string without throwing exceptions.
    """
    em = BentoMailer(recipients=["test@example.com"], subject="Compilation Test")
    em.create_header(title="Test Header")
    em.add_card(title="Test Card", value="99.9%")

    html_output = em.compile_dashboard_html()

    assert isinstance(html_output, str)
    assert "Test Header" in html_output
    assert "99.9%" in html_output
    assert "<html" in html_output.lower()


def test_as_mime_message_assembly():
    """
    Verifies that the as_mime_message method correctly packs the HTML
    and applies standard SMTP headers without attempting a live network send.
    """
    from email.mime.multipart import MIMEMultipart

    em = BentoMailer(
        recipients=["target@example.com"],
        subject="MIME Test",
        cc_recipient=["cc@example.com"],
        sender="noreply@example.com",
    )
    em.create_header(title="MIME Assembly Test")

    msg = em.as_mime_message()

    # Verify the object type and the SMTP routing headers
    assert isinstance(msg, MIMEMultipart)
    assert msg["Subject"] == "MIME Test"
    assert msg["To"] == "target@example.com"
    assert msg["Cc"] == "cc@example.com"
    assert msg["From"] == "noreply@example.com"
