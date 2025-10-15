from odoo import http
from odoo.http import request
import json

class TimesheetAPI(http.Controller):

    @http.route('/api/timesheet/create', type='json', auth='user', csrf=False, methods=['POST'])
    def create_timesheet(self, **kw):
        """
        Create a timesheet line via API using sudo() to bypass access rules.
        Expected JSON body:
        {
            "name": "Work on Project X",
            "user_id": 2,
            "date": "2025-10-14",
            "unit_amount": 5.0
        }
        """
        try:
            data = http.request.httprequest.data
            payload = json.loads(data)

            # Required fields
            name = payload.get('name')
            user_id = payload.get('user_id')
            date = payload.get('date')
            unit_amount = payload.get('unit_amount')

            if not all([name, user_id, date, unit_amount]):
                return {"error": "Missing required field(s)"}

            # Create timesheet line using sudo() to bypass access rules
            line = request.env['account.analytic.line'].sudo().create({
                'name': name,
                'user_id': user_id,
                'date': date,
                'unit_amount': unit_amount,
            })

            return {
                "success": True,
                "line_id": line.id,
                "message": "Timesheet line created successfully"
            }

        except Exception as e:
            return {"error": str(e)}
