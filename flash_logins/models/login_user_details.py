# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Your Name (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from datetime import datetime
import logging
from itertools import chain
from odoo.http import request
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import AccessDenied
import httpagentparser
import pytz

_logger = logging.getLogger(__name__)
USER_PRIVATE_FIELDS = ['password']
concat = chain.from_iterable


class LoginUserDetail(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        user = request.env['res.users'].search([('login', '=', login)])

        vals = {
            'user': user.id,
            'platform': browser['os']['name'],
            'browser': browser['browser']['name'],
            'browser_version': browser['browser']['version'],
            'ip_address': ip_address,
            'date_time': datetime.now(),
            'state': 'failed'
        }

        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth():
                    user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password, user_agent_env)
                    tz = request.httprequest.cookies.get('tz') if request else None
                    if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                        # first login or missing tz -> set tz to browser tz
                        user.tz = tz
                    user._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            vals.update({'state':'failed'})
            request.env['login.detail'].sudo().create(vals)
            raise

        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)
        vals.update({'state':'in'})
        request.env['login.detail'].sudo().create(vals)

        return user.id

class LoginUpdate(models.Model):
    _name = 'login.detail'
    _description = 'Login Detail'

    user = fields.Many2one('res.users', string="User")
    platform = fields.Char("Platform")
    browser = fields.Char("Browser")
    browser_version = fields.Char("Browser Version")
    ip_address = fields.Char(string="IP Address")
    date_time = fields.Datetime(string="Login Date And Time", default=lambda self: fields.datetime.now())
    logout_datetime = fields.Datetime(string="Logout Date And Time")
    session_time = fields.Float(string="Session time (minutes)")
    state = fields.Selection([
        ('in', 'Logged In'), 
        ('out', 'Logged Out'), 
        ('failed', 'Login Failed')
    ], string="State")