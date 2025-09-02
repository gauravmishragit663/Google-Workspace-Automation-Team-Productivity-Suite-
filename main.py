import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
import json

# Load config
with open("config.json") as f:
    config = json.load(f)

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open Sheet
spreadsheet = client.open_by_key(config["spreadsheet_id"])
try:
    sheet = spreadsheet.worksheet(config["worksheet_name"])
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=config["worksheet_name"], rows="100", cols="20")

# Read CSV
df = pd.read_csv("data.csv")

# Upload data
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())
print("✅ Data uploaded to Google Sheets!")

# Prepare summary
summary = f"""
Team Task Summary
=================
Total Tasks: {len(df)}
Upcoming Deadlines:
{df[['Name','Task','Deadline']].to_string(index=False)}
"""

# Send summary email (via Gmail SMTP)
msg = MIMEText(summary)
msg["Subject"] = "Team Task Summary"
msg["From"] = config["gmail"]
msg["To"] = config["gmail"]

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(config["gmail"], "YOUR_APP_PASSWORD")
        server.send_message(msg)
        print("📧 Email sent successfully!")
except Exception as e:
    print("❌ Email failed:", e)
