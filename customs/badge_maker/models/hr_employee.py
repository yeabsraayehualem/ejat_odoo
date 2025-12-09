from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    badge_front_image = fields.Binary(
        string='Badge Front Image',
        help='Front side of the employee badge'
    )
    badge_back_image = fields.Binary(
        string='Badge Back Image',
        help='Back side of the employee badge'
    )

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
