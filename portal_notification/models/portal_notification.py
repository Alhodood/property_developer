# -*- coding: utf-8 -*-
#############################################################################
#    Alhodood Technologies.
#
#    Copyright (C) 2026-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api

class PortalNotification(models.Model):
    _name = 'portal.notification'
    _description = 'Portal Notification'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    message = fields.Text(required=True)
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    is_read = fields.Boolean(default=False)
    created_on = fields.Datetime(default=fields.Datetime.now)

