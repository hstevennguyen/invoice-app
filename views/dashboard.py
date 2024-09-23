from flask import Blueprint, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Invoice App").sheet1

@dashboard_bp.route('/')
def dashboard():
    # Fetch data from Google Sheets
    records = sheet.get_all_records()

    # Group invoices by shop name and date
    invoices = defaultdict(lambda: {"items": [], "total_delivery": 0})

    for record in records:
        shop_name = record['Shop Name']
        date = record['Date']
        
        # Convert subtotal to float, handle missing or invalid data
        subtotal = record.get('Subtotal', 0)
        try:
            subtotal = float(subtotal)
        except ValueError:
            subtotal = 0  # In case the subtotal is not a valid number

        # Add each item's subtotal to the invoice's total
        invoices[(shop_name, date)]["items"].append(record)
        invoices[(shop_name, date)]["total_delivery"] += subtotal  # Sum up subtotals

    # Pass grouped invoices to the template
    return render_template('dashboard.html', invoices=invoices)
