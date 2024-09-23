from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

invoice_bp = Blueprint('invoice', __name__)

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the spreadsheet by name or use Sheet ID
sheet = client.open("Invoice App").sheet1

# Check if the header is already in place, if not, add it
def add_headers_if_missing():
    existing_headers = sheet.row_values(1)
    if not existing_headers:
        # Add headers if the sheet is empty
        headers = ["Shop Name", "Date", "Item", "Quantity", "Price", "Subtotal", "Total for Invoice"]
        sheet.insert_row(headers, 1)  # Insert headers at the first row

@invoice_bp.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    if request.method == 'POST':
        # Get form data
        shop_name = request.form['shop_name']
        date_of_delivery = datetime.now().strftime("%Y-%m-%d")
        dessert_names = request.form.getlist('dessert_name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')

        # Consolidate all items into one invoice
        total_delivery = 0  # To store total price of all items
        rows = []
        
        for dessert_name, quantity, price in zip(dessert_names, quantities, prices):
            quantity = int(quantity)
            price = float(price)
            subtotal = quantity * price
            total_delivery += subtotal  # Add each subtotal to the overall total
            # Collect the row for each item
            rows.append([shop_name, date_of_delivery, dessert_name, quantity, price, subtotal])

        # Add headers if they are missing
        add_headers_if_missing()

        # Append rows for all items
        for row in rows:
            sheet.append_row(row)
        
        # Append a final row for the total delivery
        # Including an empty row before the total price to separate items from the total
        sheet.append_row([shop_name, date_of_delivery, "", "", "", "", total_delivery])
        sheet.append_row([f"Total Price for {shop_name}: ", "", "", "", "", "", total_delivery])

        return redirect(url_for('dashboard.dashboard'))

    return render_template('create_invoice.html')
