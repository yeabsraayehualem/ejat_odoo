from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta


class AttendanceReport(models.Model):
    _name = 'attendance.report'
    _description = 'Attendance Report'

    name = fields.Many2one('hr.employee', string='Employee',)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    line_ids = fields.One2many('attendance.report.line', 'attendance_report_id', string='Report Lines')
    total_present_days = fields.Integer(string="Present Days", compute="_compute_summary", store=True)
    total_absent_days = fields.Integer(string="Absent Days", compute="_compute_summary", store=True)
    total_on_leave_days = fields.Integer(string="On Leave Days", compute="_compute_summary", store=True)
    total_worked_hours = fields.Float(string="Total Worked Hours", compute="_compute_summary", store=True)

    @api.depends('line_ids')
    def _compute_summary(self):
        for rec in self:
            present = absent = on_leave = 0
            worked_hours = 0.0
            for line in rec.line_ids:
                if line.is_present:
                    present += 1
                    worked_hours += line.duration or 0.0
                elif line.is_on_leave:
                    on_leave += 1
                else:
                    absent += 1
            rec.total_present_days = present
            rec.total_absent_days = absent
            rec.total_on_leave_days = on_leave
            rec.total_worked_hours = worked_hours
    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for rec in self:
            if rec.from_date > rec.to_date:
                raise ValidationError(_("From Date must be before To Date."))

    @api.model
    def create(self, vals):
        record = super(AttendanceReport, self).create(vals)
        record._generate_report_lines()
        return record

    def _generate_report_lines(self):
        """Generate daily report lines between from_date and to_date."""
        for rec in self:
            rec.line_ids.unlink()  # clear existing lines

            employee = rec.name or False
            current_day = rec.from_date
            end_date = rec.to_date

            Attendance = self.env['hr.attendance']
            Leave = self.env['hr.leave']

            while current_day <= end_date:
                next_day = current_day + timedelta(days=1)

                # Get attendance records for this day
                d = [
                    ('check_in', '>=', current_day),
                    ('check_in', '<', next_day),
                ]
                if employee:
                    d.append(('employee_id', '=', employee.id))
                attendances = Attendance.search(d)

                # Get leaves for this day
                dom = [
                    ('state', '=', 'validate'),
                    ('request_date_from', '<=', current_day),
                    ('request_date_to', '>=', current_day),
                ]
                if employee:
                    dom.append(('employee_id', '=', employee.id))
                leaves = Leave.search(dom)

                # Determine status
                is_present = bool(attendances)
                is_on_leave = bool(leaves)
                is_absent = not is_present and not is_on_leave

                if is_present:
                    for att in attendances:
                        self.env['attendance.report.line'].create({
                            'attendance_report_id': rec.id,
                            'check_in': att.check_in,
                            'check_out': att.check_out,
                            'is_present': True,
                            'is_on_leave': False,
                        })
                else:
                    # Create one record per day even if absent or on leave
                    self.env['attendance.report.line'].create({
                        'attendance_report_id': rec.id,
                        'check_in': False,
                        'check_out': False,
                        'is_present': False,
                        'is_on_leave': is_on_leave,
                    })

                current_day = next_day


class AttendanceReportLine(models.Model):
    _name = 'attendance.report.line'
    _description = 'Attendance Report Line'

    attendance_report_id = fields.Many2one('attendance.report', string='Attendance Report', required=True, ondelete='cascade')
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    is_present = fields.Boolean(string='Is Present', default=False)
    is_on_leave = fields.Boolean(string='Is On Leave', default=False)
    is_absent = fields.Boolean(string='Is Absent', compute='_compute_absent', store=True)

    @api.depends('check_in', 'check_out')
    def _compute_duration(self):
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0

    @api.depends('is_present', 'is_on_leave')
    def _compute_absent(self):
        for rec in self:
            rec.is_absent = not rec.is_present and not rec.is_on_leave



from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    project_id = fields.Many2one('project.project', string='Project', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    def action_generate_report(self):
        """Create an attendance.report record and open it."""
        self.ensure_one()
        if self.from_date > self.to_date:
            raise UserError(_("From Date cannot be after To Date."))
        if self.employee_id:
            report = self.env['attendance.report'].create({
                'name': self.employee_id.id,
                'project_id': self.project_id.id,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }) .id 
        else:
            report = []
            employee_ids = self.env['hr.employee'].search([]).ids
            for emp_id in employee_ids:
                report = self.env['attendance.report'].create({
                    'name': emp_id,
                    'project_id': self.project_id.id,
                    'from_date': self.from_date,
                    'to_date': self.to_date,
                }).id

        if isinstance(report, int):
            report = [report]
        return {
            'name': _('Attendance Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'attendance.report',
            'view_mode': 'list,form',
            "domain": [('id', 'in', report)],
            'target': 'current',
        }
