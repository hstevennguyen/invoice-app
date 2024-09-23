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
sheet = client.open("Invoice App").sheet1

@invoice_bp.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    if request.method == 'POST':
        # Get form data
        shop_name = request.form['shop_name']
        date_of_delivery = datetime.now().strftime("%Y-%m-%d")
        dessert_names = request.form.getlist('dessert_name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')

        total_delivery = 0
        rows = []

        # Calculate the subtotals and total delivery
        for dessert_name, quantity, price in zip(dessert_names, quantities, prices):
            quantity = int(quantity)
            price = float(price)
            subtotal = quantity * price
            total_delivery += subtotal
            # Collect the row for each item without adding total delivery yet
            rows.append([shop_name, date_of_delivery, dessert_name, quantity, price, subtotal])

        # Append all the invoice items to Google Sheets
        for index, row in enumerate(rows):
            # For the last row, append the total delivery in the "Total for Invoice" column
            if index == len(rows) - 1:
                row.append(total_delivery)
            else:
                row.append('')  # Leave the "Total for Invoice" column blank for all but the last item
            sheet.append_row(row)

        return redirect(url_for('dashboard.dashboard'))

    return render_template('create_invoice.html')
