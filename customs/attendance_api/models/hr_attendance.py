from odoo import models,fields,api
from datetime import timedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    project_id = fields.Many2one('project.project', string='Project', required=True)

    
    @api.model
    def close_attendance(self, project_id=None):
        attendance = self.search([ ('check_out', '=', False)])
        if attendance:
            for a in attendance:
               
                a.write({'check_out': attendance.check_in + timedelta(hours=2) })
          
        return attendance