from odoo import models,fields,api
from datetime import timedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    project_id = fields.Many2one('project.project', string='Project', required=True)

    
    @api.model
    def close_attendance(self, employee_id, project_id=None):
        attendance = self.search([('employee_id', '=', employee_id), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.write({'check_out': attendance.check_in + timedelta(hours=2) })
          
        return attendance