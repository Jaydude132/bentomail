# Author: Jason Marencic
# June 2, 2026

import contextlib
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Union

from . import themes
from .dashboard import Dashboard


def _load_env_file(path: str = ".env") -> None:
    """
    Populates os.environ from a .env file, preferring python-dotenv when it is
    installed and falling back to a minimal parser when it is not. Variables
    already present in the environment are left alone.
    """
    try:
        from dotenv import load_dotenv

        load_dotenv(path)
        return
    except ImportError:
        pass

    if not os.path.exists(path):
        return

    with open(path, "r") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _env_flag(name: str) -> bool:
    """Reads a boolean-style environment variable."""
    return str(os.getenv(name, "")).strip().lower() in ("true", "1", "yes")


def _resolve_port(explicit: Optional[int]) -> int:
    """Resolves the relay port from an explicit value or the environment."""
    if explicit is not None:
        return int(explicit)
    try:
        return int(os.getenv("SMTP_PORT", "25"))
    except (ValueError, TypeError):
        return 25


class BentoMailer(Dashboard):
    """
    A Dashboard that can address and deliver itself over SMTP.

    Relay settings resolve from explicit arguments first, then the
    environment, then a local development default.
    """

    def __init__(
        self,
        recipients: Optional[List[str]] = None,
        subject: Optional[str] = None,
        cc_recipient: Optional[Union[str, List[str]]] = None,
        sender: Optional[str] = None,
        theme: themes.EmailTheme = themes.NEUTRAL,
        branding: bool = True,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None,
        use_tls: Optional[bool] = None,
        use_ssl: Optional[bool] = None,
        load_env: bool = True,
    ) -> None:
        super().__init__(theme=theme, subject=subject, branding=branding)

        if load_env:
            _load_env_file()

        self.sender: str = sender or os.getenv("SENDER_EMAIL", "sender@example.com")
        self.smtp_server: str = smtp_server or os.getenv("SMTP_SERVER", "localhost")
        self.smtp_port: int = _resolve_port(smtp_port)

        # Authentication & Security
        self.smtp_user: Optional[str] = smtp_user or os.getenv("SMTP_USER")
        self.smtp_pass: Optional[str] = smtp_pass or os.getenv("SMTP_PASS")

        # Encryption follows the standard submission ports unless set explicitly.
        self.use_tls: bool = (
            use_tls
            if use_tls is not None
            else _env_flag("SMTP_USE_TLS") or self.smtp_port == 587
        )
        self.use_ssl: bool = (
            use_ssl
            if use_ssl is not None
            else _env_flag("SMTP_USE_SSL") or self.smtp_port == 465
        )

        self.recipients: Optional[List[str]] = list(recipients) if recipients else None
        self.cc_recipient: Optional[Union[str, List[str]]] = cc_recipient

    def _validate_routing_fields(self) -> None:
        if not self.recipients:
            raise ValueError("recipients is not defined")
        if not self.subject:
            raise ValueError("subject is not defined")

    def as_mime_message(self) -> MIMEMultipart:
        """Returns the fully addressed MIME message, ready to hand to a relay."""
        self._validate_routing_fields()
        msg = self.to_mime()

        msg["Subject"] = self.subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipient.strip() for recipient in self.recipients)

        cc_list = self.cc_list()
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)

        return msg

    def cc_list(self) -> List[str]:
        """Normalizes the configured CC value into a list of addresses."""
        if self.cc_recipient is None:
            return []
        if isinstance(self.cc_recipient, str):
            return [
                address.strip()
                for address in self.cc_recipient.split(",")
                if address.strip()
            ]
        return [address.strip() for address in self.cc_recipient if address.strip()]

    def envelope_recipients(self) -> List[str]:
        """
        Every address the message is delivered to, CC included.

        This is the SMTP envelope rather than the visible headers, so the
        configured recipient list is never modified to carry CC addresses.
        """
        envelope = [recipient.strip() for recipient in self.recipients]
        for cc in self.cc_list():
            if cc not in envelope:
                envelope.append(cc)
        return envelope

    def send_dashboard(self) -> None:
        """Compiles the dashboard and dispatches it over the configured SMTP relay."""
        msg = self.as_mime_message()

        # Dispatch Relay (with Auth & Encryption Support)
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()

            # Authenticate if credentials exist
            if self.smtp_user and self.smtp_pass:
                server.login(self.smtp_user, self.smtp_pass)

            server.sendmail(self.sender, self.envelope_recipients(), msg.as_string())

        except Exception as e:
            relay = f"{self.smtp_server}:{self.smtp_port}"
            raise RuntimeError(f"Failed to send email via {relay}. Error: {e}") from e
        finally:
            # Closing is best effort; the send result is what matters.
            with contextlib.suppress(Exception):
                server.quit()
