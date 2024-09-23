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
    records = sheet.get_all_records()
    invoices = defaultdict(lambda: {"items": [], "total_delivery": 0})
    
    for record in records:
        shop_name = record['Shop Name']
        date = record['Date']
        subtotal = record.get('Subtotal', 0)
        try:
            subtotal = float(subtotal)
        except ValueError:
            subtotal = 0
        invoices[(shop_name, date)]["items"].append(record)
        invoices[(shop_name, date)]["total_delivery"] += subtotal
    
    return render_template('dashboard.html', invoices=invoices)


@dashboard_bp.route('/print_invoice/<shop_name>/<date>')
def print_invoice(shop_name, date):
    # Fetch data from Google Sheets for the given shop and date
    records = sheet.get_all_records()
    invoice_items = []
    total_delivery = 0

    # Filter records by shop name and date
    for record in records:
        if record['Shop Name'] == shop_name and record['Date'] == date:
            invoice_items.append(record)

            # Get subtotal and handle empty/invalid cases
            subtotal = record.get('Subtotal', 0)
            try:
                subtotal = float(subtotal) if subtotal else 0  # Default to 0 if empty or invalid
            except ValueError:
                subtotal = 0  # Default to 0 if subtotal is not a valid float

            total_delivery += subtotal

    if not invoice_items:
        return "No invoice found for this shop and date."

    # Render the invoice details in a print-friendly template
    return render_template('print_invoice.html', shop_name=shop_name, date=date, items=invoice_items, total_delivery=total_delivery)
