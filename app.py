from flask import Flask
from views.dashboard import dashboard_bp
from views.invoice import invoice_bp

app = Flask(__name__)

app.register_blueprint(dashboard_bp)
app.register_blueprint(invoice_bp)

if __name__ == '__main__':
    app.run(debug=True)