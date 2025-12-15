# app.py
import base64
from pathlib import Path
from flask import Flask, request, make_response, render_template
from weasyprint import HTML
import traceback

app = Flask(__name__)

# === Preload static assets as base64 (at startup) ===
STATIC_DIR = Path(__file__).parent / "static"

# Load background and logo once
try:
    with open(STATIC_DIR / "idfront.png", "rb") as f:
        ID_FRONT_B64 = base64.b64encode(f.read()).decode('utf-8')
    with open(STATIC_DIR / "logo.jpeg", "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode('utf-8')
except FileNotFoundError as e:
    print("❌ ERROR: Missing static asset:", e)
    ID_FRONT_B64 = ""
    LOGO_B64 = ""

@app.route('/generate-badge-pdf', methods=['POST'])
def generate_badge_pdf():
    try:
        data = request.get_json()
        if not data:
            return "No JSON payload", 400

        # Validate required fields
        required = ['fullname', 'title', 'christian_name', 'phone', 'branch', 'id_number', 'registration_date', 'expiry_date']
        for field in required:
            if field not in data or not str(data[field]).strip():
                return f"Missing or empty required field: {field}", 400

        # Optional dynamic images (from Odoo)
        photo_b64 = data.get('photo_base64', '')
        qr_b64 = data.get('qr_base64', '')

        # Validate base64 if provided
        if photo_b64:
            base64.b64decode(photo_b64, validate=True)
        if qr_b64:
            base64.b64decode(qr_b64, validate=True)

        # Render template with ALL data as base64
        html_content = render_template(
            'index.html',
            # Static assets (embedded)
            id_front_b64=ID_FRONT_B64,
            logo_b64=LOGO_B64,
            # Dynamic data from Odoo
            fullname=data['fullname'],
            title=data['title'],
            christian_name=data['christian_name'],
            phone=data['phone'],
            branch=data['branch'],
            id_number=data['id_number'],
            registration_date=data['registration_date'],
            expiry_date=data['expiry_date'],
            photo_base64=photo_b64,
            qr_base64=qr_b64
        )

        # Generate PDF — no base_url needed!
        pdf = HTML(string=html_content).write_pdf()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=badge_{data["id_number"]}.pdf'
        return response

    except Exception as e:
        print("🔥 PDF Generation Error:")
        traceback.print_exc()
        return f"Server error: {str(e)}", 500

if __name__ == '__main__':
    # Verify assets loaded
    if ID_FRONT_B64 and LOGO_B64:
        print("✅ Static assets loaded successfully.")
    else:
        print("⚠️ Warning: Some static assets are missing.")

    app.run(host='0.0.0.0', port=5001, debug=True)