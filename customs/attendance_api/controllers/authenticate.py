from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
import json
import logging
_logger = logging.getLogger(__name__)
class AuthenticationController(http.Controller):

    @http.route('/api/authenticate', type='json', auth='none', csrf=False, methods=['POST'])
    def authenticate_user(self, **kw): 

        data = json.loads(http.request.httprequest.data)
        _logger.info(f"*** {data}")
        data= data['params']
        try:
            login = data['login']
            password =data['password']

            if not login or not password:
                return {'error': 'Missing login or password'}

            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            if not user:
                return {'error': 'Invalid login or password'}

            try:
                user._check_credentials(password, request.httprequest.headers)
            except AccessDenied:
                return {'error': 'Invalid login or password'}

            # Step 3: Return user info
            return {
                'success': True,
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'session_id': request.session.sid
            }

        except Exception as e:
            request.env.cr.rollback()
            return {'error': str(e)}
