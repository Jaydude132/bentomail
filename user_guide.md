# User Guide: How to Send Simple & Dashboard Emails

# Author: Jason Marencic

# June 2, 2026

Welcome to the **Python Emailer Module**! This guide is a straightforward, non-technical manual showing you how to build and send emails using this Python library.

Whether you want to send a **quick plain-text note** or a **high-end, styled dashboard report**, this guide shows you exactly what blocks to write without needing to understand how the system works under the hood.

---

## 📅 The Two Types of Emails You Can Send

Depending on your audience, you can choose between two completely different email styles:

### Style A: The Simple/Traditional Email

- **What it is:** A standard white-background email.
- **Best for:** Direct text messages, quick status updates, automated logs, or sending raw HTML tables.
- **How to send it:** Use `mailer.send()`

### Style B: The Dashboard Email

- **What it is:** A modern, dark-themed, visual dashboard featuring card grids, colored notice banners, and styled reports.
- **Best for:** Executive summaries, daily/weekly metrics, system health reports, or anything where visual layout matters.
- **How to send it:** Use `mailer.send_dashboard()`

---

## ✉️ Style A: How to Send a Simple / Traditional Email

To send a traditional email, you initialize the program, add your text or HTML content, queue any files you want to attach, and trigger the send.

### Example: Quick Status Update with an Attachment

```python
from emailer import Emailer

# 1. Start the email program
mailer = Emailer(
    recipients=["manager@example.com", "team@example.com"],
    subject="Weekly Project Status Update",
    cc_recipient="coordinator@example.com" # Optional Carbon Copy
)

# 2. Add an "Action Required" alert block at the very top (Optional)
mailer.add_alert(
    title="REVIEW REQUIRED BY FRIDAY",
    content="Please review the attached spreadsheet and submit changes before 5:00 PM EST.",
    align="left"
)

# 3. Add the body text of your email
mailer.set_plain_text_body(
    "Hello Team,\n\n"
    "I have compiled the weekly metrics. All deliverables are on track.\n"
    "Please find the detailed logs attached to this email.\n\n"
    "Best regards,\n"
    "Project Lead"
)

# 4. Attach a file from your computer
mailer.add_attachment(
    file_path="/documents/weekly_report.xlsx",
    custom_filename="Weekly_Metrics_May_2026.xlsx" # Optional: rename the file for the recipient
)

# 5. Send the email!
mailer.send()
```
