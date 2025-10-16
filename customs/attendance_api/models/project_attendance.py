from odoo import models, fields, api
from cryptography.fernet import Fernet
import qrcode
import base64
from io import BytesIO
import logging
_lg = logging.getLogger(__name__)
class ProjectProject(models.Model):
    _inherit = "project.project"

    qr_code = fields.Binary("QR Code")
    assignee_ids = fields.Many2many('hr.employee', string='Assignees',compute='_compute_assignees', store=True)
    department_ids = fields.Many2many('hr.department', string='Departments')
    
    
    @api.depends('department_ids')
    def _compute_assignees(self):
        for project in self:
            if project.department_ids:
                employees = self.env['hr.employee'].search([('department_id', 'in', project.department_ids.ids)])
                project.assignee_ids = employees
            else:
                project.assignee_ids = False
    
    def generate_and_show_qr(self):
        for rec in self:
            # Static key (must be the same in Flutter)
            STATIC_KEY = b'KzD8nN1QzYj_8jA7Yqg5hD2fV1lR8J4bJb8aR1xQG9I='
            cipher = Fernet(STATIC_KEY)

            # Compose the string to encrypt
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            date = fields.Date.today()
            main_string = f"{base_url}/project_id={rec.id}/date={date}"
            _lg.info(f"********* {main_string}")
            # Encrypt it
            encrypted_string = cipher.encrypt(main_string.encode()).decode()
            _lg.info(f"****** {encrypted_string}")
            # Generate QR code from the encrypted string
            qr = qrcode.make(main_string)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue())

            # Save the QR code binary on the record (optional)
            rec.qr_code = qr_base64

            # Return a wizard to display it
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.qr.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_qr_image': qr_base64.decode(),'value':main_string},
            }



class ProjectQrWizard(models.TransientModel):
    _name = 'project.qr.wizard'
    _description = 'Project QR Display Wizard'

    qr_image = fields.Binary('QR Code', readonly=True)
    value = fields.Char(string="Value")
