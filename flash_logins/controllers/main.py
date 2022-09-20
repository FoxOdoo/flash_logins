from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main
from odoo.addons.web.controllers.main import Home
from datetime import datetime
import werkzeug
import httpagentparser

class InheritSession(main.Session):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        user = request.env['res.users'].with_user(1).search(
            [('id', '=', request.session.uid)])
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        
        agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)

        # buscar el usuario logeado con la misma ip, sistema y navegador
        logdetail = request.env['login.detail'].sudo().search([
            ('user', '=', user.id),
            ('platform', '=', browser['os']['name']),
            ('browser', '=', browser['browser']['name']),
            ('browser_version', '=', browser['browser']['version']),
            ('ip_address', '=', ip_address)
        ], order="date_time desc", limit=1)
                
        session_time = (datetime.now() - logdetail.date_time).total_seconds()/60

        logdetail.sudo().write({
            'logout_datetime': datetime.now(),
            'session_time': session_time,
            'state': 'out'
        })

        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

# class InheritHome(Home):
#     @http.route()
#     def web_login(self, redirect=None, **kw):
#         if 'login' in kw:
#             print(kw)
        
#         return super(InheritHome, self).web_login(redirect=redirect, kw=kw)