from flask import Blueprint, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

dashboard_bp = Blueprint('dashboard', __name__)

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Invoice App").sheet1

@dashboard_bp.route('/')
def dashboard():
    # Fetch data from Google Sheets (modify as needed)
    records = sheet.get_all_records()
    return render_template('dashboard.html', invoices=records)
