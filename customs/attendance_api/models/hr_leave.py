from odoo import models, fields, api, _
import logging
_lg = logging.getLogger(__name__)

class LeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    def action_adjust_leave(self):
        _lg.info("in action_adjust_leave")
        leaves = self.env['hr.leave.allocation'].search([
            ('duration_display', '=', 1)
        ])
        _lg.info(f"Leaves found: {leaves.ids}")

        for i in leaves:
            i.number_of_days = 3  # 👈 write to stored field
            _lg.info(f"Updated leave {i.id} to 3 days")


class HrEmployee(models.Model):
    _inherit='hr.employee'
    
    
    def action_create_user(self):
        employees = self.env['hr.employee'].search([
            ('user_id','=',False)
        ])
        
        for emp in employees:
            self.env['res.users'].create({
                'name': emp.name,
                "login":emp.mobile_phone,
                "password":"123456"
            })