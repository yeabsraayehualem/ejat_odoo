# controllers/hr_badge.py
import logging
import requests
from odoo import http
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError
from datetime import timedelta
_logger = logging.getLogger(__name__)

class HrBadgeController(http.Controller):

    @http.route('/hr/badge/pdf/<int:employee_id>', type='http', auth='user')
    def download_badge_pdf(self, employee_id, **kwargs):
        # Fetch employee
        emp = request.env['hr.employee'].sudo().browse(employee_id)
        if not emp.exists():
            return request.not_found()

        # Security: ensure user has access
        try:
            emp.check_access_rights('read')
            emp.check_access_rule('read')
        except AccessError:
            return request.not_found()

        # Prepare data
        company = emp.company_id or request.env.company

        # Employee photo (image_1920 is full-res)
        photo_b64 = emp.image_1920.decode('utf-8') if emp.image_1920 else ''

        # QR code (already computed and base64-encoded)
        qr_b64 = emp.qr_code.decode('utf-8') if emp.qr_code else ''

        # Build payload for Flask
        payload = {
            'fullname': emp.name or 'ዲ/ን የአብስራ አየሁአለም',
            'title': emp.job_id.name or 'ጃን ኤልያስ',
            'christian_name': getattr(emp, 'name_of_baptism', ''),  # ← adjust if field name differs
            'phone': emp.work_phone or emp.mobile_phone or '0987656788',
            'branch': company.city or 'እዲስ እበባ',
            'id_number': emp.barcode or emp.identification_id or str(emp.id),
            'registration_date': emp.create_date.strftime('%d/%m/%Y') if emp.create_date else '',
            'expiry_date': (emp.create_date + timedelta(days=3*365)).strftime('%d/%m/%Y') if emp.create_date else '',
            'photo_base64': photo_b64,
            'qr_base64': qr_b64,
        }

        # Call Flask service
        try:
            flask_url = 'http://flask_badge:5001/generate-badge-pdf'
            response = requests.post(flask_url, json=payload, timeout=20)
            response.raise_for_status()
            pdf_content = response.content
        except Exception as e:
            _logger.error("Failed to generate badge PDF: %s", e)
            return request.make_response(
                "Error generating badge. Please check the Flask service.",
                [('Content-Type', 'text/plain')],
                status=500
            )

        # Return PDF as download
        filename = f'badge_{emp.barcode or emp.id}.pdf'
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', content_disposition(filename)),
            ]
        )