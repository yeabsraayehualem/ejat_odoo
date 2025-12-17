from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    name_of_baptism = fields.Char(string='Name of Baptism')
    birth_place = fields.Char(string="ትውልድ")
    branch = fields.Char(string="Branch")
    issued_date=fields.Date(string="Issued Date",default=fields.Date.today())
    expiration_date = fields.Date(string="Expiration Date")
    

    qr_code = fields.Binary(
        string='QR Code',
        help='QR code for the employee', compute="_compute_qr_code"
    )

    @api.depends('barcode')
    def _compute_qr_code(self):
        for record in self:
            if record.barcode:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.barcode)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')

                # Save to a BytesIO buffer
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                qr_image = buffer.getvalue()
                record.qr_code = base64.b64encode(qr_image)
            else:
                record.qr_code = False

    def action_generate_id_badge_pdf(self):
        """Open a URL that will generate and download the badge PDF."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/hr/badge/pdf/{self.id}',
            'target': 'self',
        }