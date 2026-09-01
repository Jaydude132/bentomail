from bentomail import BentoMailer, themes

# 1. Initialize the engine
mail = BentoMailer(subject="Weekly Garage & Fleet Telemetry", theme=themes.SLATE)

# 2. Header
mail.create_header(
    title="Personal Garage Systems", subtitle="Vehicle Telemetry & Workshop Report"
)

# 3. Hero Section
mail.create_hero(
    badge="SYSTEMS NOMINAL",
    title="Fleet Status OK",
    description="All vehicles and workshop circuits are operating within optimal parameters. No immediate maintenance is required.",
)

# 4. Status Alert
mail.add_info(
    "Reminder: 2026 Chevy 3500HD scheduled for routine oil change in 1,200 miles."
)

# 5. KPI Metric Cards
mail.add_card(title="Shop Temp", value="68°F", color=mail.theme.success_color)
mail.add_card(title="3500HD Oil Life", value="42%", color=mail.theme.info_color)
mail.add_card(
    title="Welder 50A Circuit", value="Standby", color=mail.theme.success_color
)
mail.add_card(title="Active Faults", value="0", color=mail.theme.warning_color)

# 6. Data Visualization
mail.add_bar_chart(
    title="Fleet Mileage (Last 4 Weeks)",
    categories=["Week 1", "Week 2", "Week 3", "Week 4"],
    values=[124, 210, 185, 95],
)

# 7. Data Tables (Side-by-Side Reports)
# Left Report (colspan=1)
mail.add_report(
    title="Recent Maintenance Log",
    headers=["System", "Task", "Status"],
    data=[
        ["3500HD", "Tire Rotation", "Done"],
        ["Workshop", "50A Breaker", "Done"],
        ["3500HD", "Cabin Filter", "Pending"],
    ],
    highlight_row_index=2,  # Visually highlights the pending item
)

# Right Report (colspan=1)
mail.add_report(
    title="Shop Consumables",
    headers=["Supply", "Level", "Action"],
    data=[
        ["Argon Gas (TIG)", "800 PSI", "Refill Soon"],
        ["15W-40 Oil", "3 Gallons", "None"],
        ["Shop Towels", "2 Boxes", "None"],
    ],
    highlight_row_index=0,  # Visually highlights the low argon gas
)

# 8. Footer Section
mail.create_footer(
    line1="Automated Garage Telemetry",
    line2="Generated securely from local network.",
    links=[{"text": "View Full Diagnostic Logs", "url": "https://example.com"}],
)

# 9. Generate the raw HTML
html_output = mail.compile_dashboard_html()

# --- THE BROWSER FIX ---
for img in mail._inline_images:
    cid = img.get("Content-ID").strip("<>")
    b64_data = img.get_payload().replace("\n", "")
    html_output = html_output.replace(f"cid:{cid}", f"data:image/png;base64,{b64_data}")
# -----------------------

with open("readme_screenshot.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print(
    "Dashboard generated! Double-click 'readme_screenshot.html' to open it in your browser."
)
