# Author: Jason Marencic
# June 2, 2026

"""
A short status email.

Running this file prints the message. Pass --send to actually dispatch it,
which needs relay settings in a .env file or the environment:

    SMTP_SERVER=smtp.example.com
    SMTP_PORT=587
    SMTP_USER=reports@example.com
    SMTP_PASS=...
    SENDER_EMAIL=reports@example.com
"""

import argparse

from bentomail import BentoMailer, themes


def build_alert(recipient: str) -> BentoMailer:
    mail = BentoMailer(
        recipients=[recipient],
        subject="Backup Job Completed",
        theme=themes.NEUTRAL,
    )

    mail.create_header(
        description="STORAGE OPERATIONS",
        title="Nightly Backup",
        subtitle="Completed 03:14 UTC",
    )

    mail.add_card(
        title="Volumes", value="18 / 18", label="All captured", color="SUCCESS"
    )
    mail.add_card(title="Transferred", value="1.4 TB", label="42 min", color="INFO")
    mail.add_card(title="Failures", value="0", label="None", color="SUCCESS")

    mail.add_success("Every volume was captured and verified against its checksum.")

    mail.create_footer(
        line1="Sent by the storage reporting job.",
        links=[{"text": "Runbook", "url": "https://example.com/runbook"}],
    )
    return mail


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", default="ops@example.com", help="Recipient address.")
    parser.add_argument("--send", action="store_true", help="Dispatch over SMTP.")
    args = parser.parse_args()

    mail = build_alert(args.to)

    if not args.send:
        print(mail.to_text())
        print("\nNothing was sent. Re-run with --send to dispatch over SMTP.")
        return

    mail.send_dashboard()
    print(f"Sent to {args.to}")


if __name__ == "__main__":
    main()
